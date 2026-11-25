#!/usr/bin/env python3
"""Patches the platform folders created by `flutter create` (CI step).

* Android: app name, INTERNET permission, AdMob APPLICATION_ID, minSdk 24
  (Android 7+, whisper.cpp), target/compile SDK >= 35, every screen size (phones,
  tablets, foldables, Chromebooks; resizable multi-window), HTTPS-only
  network security config, optional release signing from CI secrets.
* iOS: display name, AdMob id, SKAdNetwork, tracking text, iOS 14+,
  universal app (iPhone + iPad, every iPad orientation, Split View /
  Stage Manager), App Transport Security kept strict.
* Web: title, description, PWA manifest (any orientation, standalone),
  referrer policy.

Idempotent: safe to run on every build.
"""
import json
import os
import re

APP_NAME = "Photo, Video & Audio"
APP_NAME_TR = "Fotoğraf, Video ve Ses"
# XML/HTML içinde "&" kaçışlı yazılır (AndroidManifest, Info.plist, index.html).
APP_NAME_XML = APP_NAME.replace("&", "&amp;")
# Google's PUBLIC TEST AdMob app ids. Replace before publishing.
ADMOB_ANDROID = os.environ.get("ADMOB_APP_ID_ANDROID") or "ca-app-pub-3940256099942544~3347511713"
ADMOB_IOS = os.environ.get("ADMOB_APP_ID_IOS") or "ca-app-pub-3940256099942544~1458002511"


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def android():
    man = "android/app/src/main/AndroidManifest.xml"
    if os.path.exists(man):
        s = read(man)
        s = re.sub(r'android:label="[^"]*"', 'android:label="%s"' % APP_NAME_XML, s, count=1)
        # Every screen size + resizable windows (tablets, foldables, ChromeOS).
        if "<supports-screens" not in s:
            s = s.replace(
                "<application",
                '<supports-screens android:smallScreens="true" android:normalScreens="true" '
                'android:largeScreens="true" android:xlargeScreens="true" android:anyDensity="true"/>\n    <application',
                1,
            )
        if "android:resizeableActivity" not in s:
            s = s.replace("<application", '<application android:resizeableActivity="true"', 1)
        # HTTPS only (no cleartext traffic) via network security config.
        if "android:networkSecurityConfig" not in s:
            s = s.replace(
                "<application",
                '<application android:networkSecurityConfig="@xml/network_security_config" '
                'android:usesCleartextTraffic="false"',
                1,
            )
        # Never lock orientation in the manifest; the app decides at runtime
        # (phones portrait, tablets/foldables every orientation).
        s = re.sub(r'\s+android:screenOrientation="[^"]*"', "", s)
        if "android.permission.INTERNET" not in s:
            s = s.replace("<application", '<uses-permission android:name="android.permission.INTERNET"/>\n    <application', 1)
        # Araç izinleri: yalnızca ilgili araç açıldığında, önce 33 dilde açıklama
        # gösterilerek istenir. Fotoğraf/video seçimi Android Photo Picker ile,
        # ses dosyaları sistem seçicisiyle (SAF) yapılır: READ_MEDIA_IMAGES,
        # READ_MEDIA_VIDEO, READ_MEDIA_AUDIO ve MANAGE_EXTERNAL_STORAGE İSTENMEZ.
        # Galeriye kaydetme (gal) Android 11+ izinsizdir; Android 7–10 için
        # WRITE_EXTERNAL_STORAGE (maxSdkVersion 29) ve requestLegacyExternalStorage.
        for perm in ("android.permission.CAMERA", "android.permission.RECORD_AUDIO"):
            if perm not in s:
                s = s.replace("<application", '<uses-permission android:name="%s"/>\n    <application' % perm, 1)
        if "android.permission.WRITE_EXTERNAL_STORAGE" not in s:
            s = s.replace(
                "<application",
                '<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="29"/>\n    <application',
                1,
            )
        if "requestLegacyExternalStorage" not in s:
            s = s.replace("<application", '<application android:requestLegacyExternalStorage="true"', 1)
        # Eklentilerin birleştirebileceği geniş medya izinleri kesinlikle kaldırılır
        # (Google Play "Photo and Video Permissions" politikası).
        if "xmlns:tools=" not in s:
            s = s.replace(
                'xmlns:android="http://schemas.android.com/apk/res/android"',
                'xmlns:android="http://schemas.android.com/apk/res/android" xmlns:tools="http://schemas.android.com/tools"',
                1,
            )
        for perm in ("android.permission.READ_MEDIA_IMAGES", "android.permission.READ_MEDIA_VIDEO",
                     "android.permission.READ_MEDIA_AUDIO", "android.permission.READ_MEDIA_VISUAL_USER_SELECTED",
                     "android.permission.READ_EXTERNAL_STORAGE", "android.permission.MANAGE_EXTERNAL_STORAGE"):
            if perm not in s:
                s = s.replace("<application", '<uses-permission android:name="%s" tools:node="remove"/>\n    <application' % perm, 1)
        for feat in ("android.hardware.camera", "android.hardware.camera.autofocus", "android.hardware.microphone"):
            if feat not in s:
                s = s.replace("<application", '<uses-feature android:name="%s" android:required="false"/>\n    <application' % feat, 1)
        # Uzun fotoğraf/video işlemleri için büyük yığın.
        if "android:largeHeap" not in s:
            s = s.replace("<application", '<application android:largeHeap="true"', 1)
        if "com.google.android.gms.ads.APPLICATION_ID" not in s:
            s = s.replace(
                "</application>",
                '    <meta-data android:name="com.google.android.gms.ads.APPLICATION_ID" android:value="%s"/>\n    </application>' % ADMOB_ANDROID,
                1,
            )
        # Firebase: ölçüm ve çökme raporu uygulama içinden (izinle) açılır;
        # reklam kimliği hiç toplanmaz.
        for k in ("firebase_analytics_collection_enabled", "google_analytics_adid_collection_enabled",
                  "firebase_crashlytics_collection_enabled"):
            if k not in s:
                s = s.replace("</application>", '    <meta-data android:name="%s" android:value="false"/>\n    </application>' % k, 1)
        write(man, s)
    values_dir = "android/app/src/main/res/values"
    if os.path.isdir("android/app/src/main/res"):
        os.makedirs(values_dir, exist_ok=True)
        # Crashlytics Gradle eklentisi olmadan yapı kimliği (her derlemede yeni).
        import uuid
        write(
            os.path.join(values_dir, "crashlytics.xml"),
            '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
            '    <string name="com.google.firebase.crashlytics.mapping_file_id" translatable="false">%s</string>\n'
            '    <bool name="com.crashlytics.RequireBuildId">false</bool>\n</resources>\n' % uuid.uuid4().hex,
        )
    xml_dir = "android/app/src/main/res/xml"
    if os.path.isdir("android/app/src/main/res"):
        os.makedirs(xml_dir, exist_ok=True)
        write(
            os.path.join(xml_dir, "network_security_config.xml"),
            """<?xml version="1.0" encoding="utf-8"?>
<!-- HTTPS only; user-installed CAs are not trusted in release builds. -->
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system"/>
        </trust-anchors>
    </base-config>
</network-security-config>
""",
        )
    # R8 strips Room's generated WorkDatabase_Impl (WorkManager comes in via
    # google_mobile_ads), which crashes release builds at startup with
    # "Failed to create an instance of androidx.work.impl.WorkDatabase".
    # The Flutter Gradle plugin applies android/app/proguard-rules.pro.
    rules = "android/app/proguard-rules.pro"
    keep = """
-keep class * extends androidx.room.RoomDatabase { <init>(); }
-keep class androidx.work.impl.WorkDatabase_Impl { *; }
-keep class androidx.work.impl.** extends androidx.room.RoomDatabase { *; }
-dontwarn androidx.work.**
# google_mlkit_text_recognition: optional Chinese/Devanagari/Japanese/Korean
# recognizers are not bundled; R8 must not fail on their missing classes.
-dontwarn com.google.mlkit.vision.text.chinese.**
-dontwarn com.google.mlkit.vision.text.devanagari.**
-dontwarn com.google.mlkit.vision.text.japanese.**
-dontwarn com.google.mlkit.vision.text.korean.**
"""
    old = read(rules) if os.path.exists(rules) else ""
    if "WorkDatabase_Impl" not in old:
        write(rules, old + keep)
    elif "mlkit.vision.text.chinese" not in old:
        write(rules, old + keep[keep.index("# google_mlkit"):])
    for gradle in ["android/app/build.gradle.kts", "android/app/build.gradle"]:
        if not os.path.exists(gradle):
            continue
        s = read(gradle)
        kts = gradle.endswith(".kts")
        if kts:
            s = s.replace("minSdk = flutter.minSdkVersion", "minSdk = maxOf(flutter.minSdkVersion, 24)")
            s = s.replace("targetSdk = flutter.targetSdkVersion", "targetSdk = maxOf(flutter.targetSdkVersion, 35)")
            s = s.replace("compileSdk = flutter.compileSdkVersion", "compileSdk = maxOf(flutter.compileSdkVersion, 35)")
        else:
            s = s.replace("minSdkVersion flutter.minSdkVersion", "minSdkVersion Math.max(flutter.minSdkVersion, 24)")
            s = s.replace("minSdk flutter.minSdkVersion", "minSdk Math.max(flutter.minSdkVersion, 24)")
        # Yerel bildirim eklentisi Java 8+ kütüphaneleri ister (desugaring).
        if kts and "isCoreLibraryDesugaringEnabled" not in s:
            s = s.replace("compileOptions {", "compileOptions {\n        isCoreLibraryDesugaringEnabled = true", 1)
        if kts and "desugar_jdk_libs" not in s:
            s += '\ndependencies {\n    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")\n}\n'
        # Release signing from CI secrets when available (see docs/RELEASE.md).
        if kts and os.environ.get("ANDROID_KEYSTORE_PATH") and "gs100Release" not in s:
            s = s.replace(
                "buildTypes {",
                """signingConfigs {
        create("gs100Release") {
            storeFile = file(System.getenv("ANDROID_KEYSTORE_PATH"))
            storePassword = System.getenv("ANDROID_KEYSTORE_PASSWORD")
            keyAlias = System.getenv("ANDROID_KEY_ALIAS")
            keyPassword = System.getenv("ANDROID_KEY_PASSWORD")
        }
    }
    buildTypes {""",
                1,
            )
            s = s.replace(
                'signingConfig = signingConfigs.getByName("debug")',
                'signingConfig = signingConfigs.getByName("gs100Release")',
            )
        write(gradle, s)


def ios():
    plist = "ios/Runner/Info.plist"
    if os.path.exists(plist):
        s = read(plist)
        s = re.sub(
            r"(<key>CFBundleDisplayName</key>\s*<string>)[^<]*(</string>)",
            r"\g<1>%s\g<2>" % APP_NAME_XML,
            s,
        )
        extra = ""
        for key, text in (
            ("NSCameraUsageDescription", "Kamera yalnızca filtreli kamera ve zaman atlamalı video açıkken kullanılır; görüntüler cihazınızda kalır. / The camera is used only in the filter camera and time-lapse tools; images stay on your device."),
            ("NSMicrophoneUsageDescription", "Mikrofon yalnızca ses kaydı yaptığınızda (podcast, ses değiştirici, ses düzenleyici) kullanılır; kayıtlar cihazınızda kalır. / The microphone is used only while you record; recordings stay on your device."),
            ("NSPhotoLibraryUsageDescription", "Yalnızca sizin seçtiğiniz fotoğraf ve videolar açılır. / Only the photos and videos you pick are opened."),
            ("NSPhotoLibraryAddUsageDescription", "Düzenlediğiniz fotoğraf ve videoları galerinize kaydetmek için. / To save the photos and videos you edit to your library."),
        ):
            if key not in s:
                extra += "\t<key>%s</key>\n\t<string>%s</string>\n" % (key, text)
        if "GADApplicationIdentifier" not in s:
            extra += "\t<key>GADApplicationIdentifier</key>\n\t<string>%s</string>\n" % ADMOB_IOS
        if "SKAdNetworkItems" not in s:
            extra += (
                "\t<key>SKAdNetworkItems</key>\n\t<array>\n\t\t<dict>\n"
                "\t\t\t<key>SKAdNetworkIdentifier</key>\n\t\t\t<string>cstr6suwn9.skadnetwork</string>\n"
                "\t\t</dict>\n\t</array>\n"
            )
        if "NSUserTrackingUsageDescription" not in s:
            extra += (
                "\t<key>NSUserTrackingUsageDescription</key>\n"
                "\t<string>Reklamları ilgi alanlarınıza göre göstermek için kullanılır. / "
                "Used to show more relevant ads.</string>\n"
            )
        # iPad: every orientation (required for Split View / Stage Manager);
        # iPhone orientation is chosen at runtime (portrait).
        if "UISupportedInterfaceOrientations~ipad" not in s:
            extra += (
                "\t<key>UISupportedInterfaceOrientations~ipad</key>\n\t<array>\n"
                "\t\t<string>UIInterfaceOrientationPortrait</string>\n"
                "\t\t<string>UIInterfaceOrientationPortraitUpsideDown</string>\n"
                "\t\t<string>UIInterfaceOrientationLandscapeLeft</string>\n"
                "\t\t<string>UIInterfaceOrientationLandscapeRight</string>\n\t</array>\n"
            )
        s = re.sub(r"\s*<key>UIRequiresFullScreen</key>\s*<true/>", "", s)
        # Keep App Transport Security strict (HTTPS only).
        s = re.sub(r"\s*<key>NSAllowsArbitraryLoads</key>\s*<true/>", "", s)
        if "FIREBASE_ANALYTICS_COLLECTION_ENABLED" not in s:
            extra += "\t<key>FIREBASE_ANALYTICS_COLLECTION_ENABLED</key>\n\t<false/>\n"
        if "FirebaseCrashlyticsCollectionEnabled" not in s:
            extra += "\t<key>FirebaseCrashlyticsCollectionEnabled</key>\n\t<false/>\n"
        if "ITSAppUsesNonExemptEncryption" not in s:
            extra += "\t<key>ITSAppUsesNonExemptEncryption</key>\n\t<false/>\n"
        if extra:
            idx = s.rfind("</dict>")
            s = s[:idx] + extra + s[idx:]
        write(plist, s)
    podfile = "ios/Podfile"
    # `flutter create` does not write a Podfile; Flutter would generate one at
    # build time with its default (too low) iOS target. Google ML Kit pods need
    # a higher iOS, so create it from the SDK template now and raise the platform.
    if not os.path.exists(podfile) and os.path.isdir("ios"):
        import shutil
        fl = shutil.which("flutter")
        if fl:
            root = os.path.dirname(os.path.dirname(os.path.realpath(fl)))
            tpl = os.path.join(root, "packages", "flutter_tools", "templates", "cocoapods", "Podfile-ios")
            if os.path.exists(tpl):
                shutil.copy(tpl, podfile)
    if os.path.exists(podfile):
        s = read(podfile)
        s = re.sub(r"#?\s*platform :ios, '[0-9.]+'", "platform :ios, '15.6'", s, count=1)
        write(podfile, s)
    pbx = "ios/Runner.xcodeproj/project.pbxproj"
    if os.path.exists(pbx):
        s = read(pbx)
        s = re.sub(r"IPHONEOS_DEPLOYMENT_TARGET = [0-9.]+;", "IPHONEOS_DEPLOYMENT_TARGET = 15.6;", s)
        # Universal app: iPhone (1) + iPad (2).
        s = re.sub(r'TARGETED_DEVICE_FAMILY = "?[0-9,]+"?;', 'TARGETED_DEVICE_FAMILY = "1,2";', s)
        write(pbx, s)


def web():
    index = "web/index.html"
    if os.path.exists(index):
        s = read(index)
        s = re.sub(r"<title>[^<]*</title>", "<title>%s</title>" % APP_NAME_XML, s)
        s = re.sub(
            r'<meta name="description" content="[^"]*">',
            '<meta name="description" content="%s - %s">' % (APP_NAME_XML, APP_NAME_TR),
            s,
        )
        if 'name="referrer"' not in s:
            s = s.replace("<head>", '<head>\n  <meta name="referrer" content="strict-origin-when-cross-origin">', 1)
        write(index, s)
    manifest = "web/manifest.json"
    if os.path.exists(manifest):
        m = json.loads(read(manifest))
        m["name"] = APP_NAME
        m["short_name"] = APP_NAME[:12]
        m["description"] = APP_NAME_TR
        m["display"] = "standalone"
        m["orientation"] = "any"
        m["categories"] = ["photo", "multimedia", "utilities"]
        write(manifest, json.dumps(m, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    android()
    ios()
    web()
    print("platform folders patched")
