#!/usr/bin/env python3
"""Patches the platform folders created by `flutter create` (CI step).

* Android: app name, INTERNET permission, AdMob APPLICATION_ID, minSdk 24
  (Android 7+, whisper.cpp), target/compile SDK >= 35, every screen size (phones,
  tablets, foldables, Chromebooks; resizable multi-window), HTTPS-only
  network security config, optional release signing from CI secrets.
* iOS: display name, AdMob id, SKAdNetwork, tracking text, iOS 14+,
  universal app (iPhone + iPad, every iPad orientation, Split View /
  Stage Manager), App Transport Security kept strict.
* Gizli Albüm biyometrik açma (local_auth): Android MainActivity
  FlutterFragmentActivity olur; iOS NSFaceIDUsageDescription Info.plist'e ve
  33 dilde InfoPlist.strings olarak eklenir (Xcode projesine kaydedilir).
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

# Face ID açıklaması (33 dil; iOS izin penceresinde gösterilir). lproj adları.
FACEID_TEXTS = [
    ('tr', 'Face ID yalnızca Gizli Albüm\'ü, sizin açtığınız biyometrik kilitle açmak için kullanılır. Yüz verileri uygulamaya verilmez.'),
    ('en', 'Face ID is used only to open the Hidden Album if you turn on biometric unlock. Face data is never shared with the app.'),
    ('de', 'Face ID wird nur verwendet, um das versteckte Album zu öffnen, wenn du biometrisches Entsperren aktivierst. Gesichtsdaten erhält die App nie.'),
    ('es', 'Face ID solo se usa para abrir el álbum oculto si activas el desbloqueo biométrico. La app nunca recibe datos faciales.'),
    ('fr', 'Face ID sert uniquement à ouvrir l’album caché si vous activez le déverrouillage biométrique. L’app ne reçoit jamais de données faciales.'),
    ('ar', 'يُستخدم Face ID فقط لفتح الألبوم المخفي إذا فعّلت الفتح بالقياسات الحيوية. لا يحصل التطبيق على بيانات الوجه أبدًا.'),
    ('fa', 'Face ID فقط برای باز کردن آلبوم پنهان، اگر بازکردن بیومتریک را روشن کنید، به کار می\u200cرود. داده\u200cهای چهره هرگز به برنامه داده نمی\u200cشود.'),
    ('he', 'Face ID משמש רק לפתיחת האלבום המוסתר אם הפעלתם ביטול נעילה ביומטרי. האפליקציה לעולם אינה מקבלת נתוני פנים.'),
    ('ur', 'Face ID صرف چھپا البم کھولنے کے لیے استعمال ہوتا ہے، اگر آپ بایومیٹرک ان لاک آن کریں۔ چہرے کا ڈیٹا ایپ کو کبھی نہیں ملتا۔'),
    ('ru', 'Face ID используется только для открытия скрытого альбома, если вы включили биометрическую разблокировку. Приложение не получает данные лица.'),
    ('uk', 'Face ID використовується лише для відкриття прихованого альбому, якщо ви ввімкнули біометричне розблокування. Застосунок не отримує даних обличчя.'),
    ('pl', 'Face ID służy tylko do otwierania ukrytego albumu, jeśli włączysz odblokowanie biometryczne. Aplikacja nigdy nie otrzymuje danych twarzy.'),
    ('cs', 'Face ID slouží jen k otevření skrytého alba, pokud zapnete biometrické odemknutí. Aplikace nikdy nedostává data obličeje.'),
    ('ro', 'Face ID este folosit doar pentru a deschide albumul ascuns, dacă activați deblocarea biometrică. Aplicația nu primește niciodată date faciale.'),
    ('hu', 'A Face ID csak a rejtett album megnyitására szolgál, ha bekapcsolod a biometrikus feloldást. Az alkalmazás soha nem kap arcadatokat.'),
    ('el', 'Το Face ID χρησιμοποιείται μόνο για το άνοιγμα του κρυφού άλμπουμ, αν ενεργοποιήσετε το βιομετρικό ξεκλείδωμα. Η εφαρμογή δεν λαμβάνει ποτέ δεδομένα προσώπου.'),
    ('it', 'Face ID viene usato solo per aprire l’album nascosto se attivi lo sblocco biometrico. L’app non riceve mai dati del volto.'),
    ('pt', 'O Face ID é usado só para abrir o álbum oculto se você ativar o desbloqueio biométrico. O app nunca recebe dados do rosto.'),
    ('nl', 'Face ID wordt alleen gebruikt om het verborgen album te openen als je biometrisch ontgrendelen aanzet. De app krijgt nooit gezichtsgegevens.'),
    ('sv', 'Face ID används bara för att öppna det dolda albumet om du slår på biometrisk upplåsning. Appen får aldrig ansiktsdata.'),
    ('da', 'Face ID bruges kun til at åbne det skjulte album, hvis du slår biometrisk oplåsning til. Appen får aldrig ansigtsdata.'),
    ('nb', 'Face ID brukes bare til å åpne det skjulte albumet hvis du slår på biometrisk opplåsing. Appen får aldri ansiktsdata.'),
    ('fi', 'Face ID:tä käytetään vain piilotetun albumin avaamiseen, jos otat biometrisen avauksen käyttöön. Sovellus ei koskaan saa kasvotietoja.'),
    ('ja', 'Face ID は、生体認証での解除をオンにした場合に非表示アルバムを開くためだけに使います。顔のデータがアプリに渡ることはありません。'),
    ('ko', 'Face ID는 생체 인증 잠금 해제를 켠 경우 숨긴 앨범을 여는 데만 사용돼요. 얼굴 데이터는 앱에 전달되지 않아요.'),
    ('zh-Hans', '仅在你开启生物识别解锁时，Face ID 用于打开隐藏相册。应用永远不会获得面部数据。'),
    ('hi', 'Face ID सिर्फ़ छिपा एल्बम खोलने के लिए इस्तेमाल होता है, अगर आप बायोमेट्रिक अनलॉक चालू करें। चेहरे का डेटा ऐप को कभी नहीं मिलता।'),
    ('bn', 'আপনি বায়োমেট্রিক আনলক চালু করলে Face ID শুধু লুকানো অ্যালবাম খুলতে ব্যবহার হয়। মুখের ডেটা অ্যাপ কখনও পায় না।'),
    ('id', 'Face ID hanya dipakai untuk membuka album tersembunyi jika Anda mengaktifkan buka dengan biometrik. Aplikasi tidak pernah menerima data wajah.'),
    ('ms', 'Face ID hanya digunakan untuk membuka album tersembunyi jika anda menghidupkan buka kunci biometrik. Aplikasi tidak pernah menerima data wajah.'),
    ('th', 'Face ID ใช้เพื่อเปิดอัลบั้มลับเท่านั้น เมื่อคุณเปิดการปลดล็อกด้วยไบโอเมตริก แอปไม่ได้รับข้อมูลใบหน้าเลย'),
    ('vi', 'Face ID chỉ được dùng để mở album ẩn nếu bạn bật mở khóa sinh trắc học. Ứng dụng không bao giờ nhận dữ liệu khuôn mặt.'),
    ('fil', 'Ginagamit lang ang Face ID para buksan ang nakatagong album kung i-on mo ang biometric na pag-unlock. Hindi kailanman natatanggap ng app ang data ng mukha.'),
]


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
        # camera_android_camerax aynı izni maxSdkVersion 28 ile bildiriyor;
        # Android 10'da galeriye kaydetme için 29 değeri korunur (tools:replace).
        for perm in ("android.permission.CAMERA", "android.permission.RECORD_AUDIO"):
            if perm not in s:
                s = s.replace("<application", '<uses-permission android:name="%s"/>\n    <application' % perm, 1)
        if "android.permission.WRITE_EXTERNAL_STORAGE" not in s:
            s = s.replace(
                "<application",
                '<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="29" tools:replace="android:maxSdkVersion"/>\n    <application',
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


def android_fragment_activity():
    """Gizli Albüm biyometrik açma (local_auth) FlutterFragmentActivity ister."""
    root = "android/app/src/main"
    if not os.path.isdir(root):
        return
    for d, _, files in os.walk(root):
        for f in files:
            if f not in ("MainActivity.kt", "MainActivity.java"):
                continue
            p = os.path.join(d, f)
            s = read(p)
            if "FlutterFragmentActivity" in s:
                continue
            s = s.replace("io.flutter.embedding.android.FlutterActivity", "io.flutter.embedding.android.FlutterFragmentActivity")
            s = re.sub(r"\bFlutterActivity\b", "FlutterFragmentActivity", s)
            write(p, s)


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
            ("NSFaceIDUsageDescription", FACEID_TEXTS[1][1]),
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
        s = ios_faceid_strings(s)
        write(pbx, s)


def ios_faceid_strings(pbx):
    """Face ID açıklamasını 33 dilde InfoPlist.strings olarak ekler ve projeye kaydeder."""
    for lang, text in FACEID_TEXTS:
        d = "ios/Runner/%s.lproj" % lang
        os.makedirs(d, exist_ok=True)
        esc = text.replace("\\", "\\\\").replace('"', '\\"')
        write(d + "/InfoPlist.strings", '"NSFaceIDUsageDescription" = "%s";\n' % esc)
    if "InfoPlist.strings in Resources" in pbx:
        return pbx
    import hashlib

    def uid(x):
        return hashlib.md5(("gs100-" + x).encode()).hexdigest()[:24].upper()

    def q(x):
        return '"%s"' % x if "-" in x else x

    vg, bf = uid("variant"), uid("buildfile")
    refs = [(uid("ref-" + l), l) for l, _ in FACEID_TEXTS]
    pbx = pbx.replace(
        "/* Begin PBXBuildFile section */\n",
        "/* Begin PBXBuildFile section */\n\t\t%s /* InfoPlist.strings in Resources */ = {isa = PBXBuildFile; fileRef = %s /* InfoPlist.strings */; };\n" % (bf, vg),
        1,
    )
    pbx = pbx.replace(
        "/* Begin PBXFileReference section */\n",
        "/* Begin PBXFileReference section */\n"
        + "".join(
            '\t\t%s /* %s */ = {isa = PBXFileReference; lastKnownFileType = text.plist.strings; name = %s; path = %s; sourceTree = "<group>"; };\n'
            % (r, l, q(l), q("%s.lproj/InfoPlist.strings" % l))
            for r, l in refs
        ),
        1,
    )
    group = "\t\t%s /* InfoPlist.strings */ = {\n\t\t\tisa = PBXVariantGroup;\n\t\t\tchildren = (\n%s\t\t\t);\n\t\t\tname = InfoPlist.strings;\n\t\t\tsourceTree = \"<group>\";\n\t\t};\n" % (
        vg, "".join("\t\t\t\t%s /* %s */,\n" % (r, l) for r, l in refs))
    if "/* Begin PBXVariantGroup section */\n" in pbx:
        pbx = pbx.replace("/* Begin PBXVariantGroup section */\n", "/* Begin PBXVariantGroup section */\n" + group, 1)
    else:
        pbx = pbx.replace(
            "/* Begin XCBuildConfiguration section */",
            "/* Begin PBXVariantGroup section */\n" + group + "/* End PBXVariantGroup section */\n\n/* Begin XCBuildConfiguration section */",
            1,
        )
    # Runner grubu ve Runner hedefinin kaynak adımı (Main.storyboard'u içeren; RunnerTests değil).
    pbx = re.sub(
        r"(/\* Runner \*/ = \{\s*isa = PBXGroup;\s*children = \()",
        lambda m: m.group(1) + "\n\t\t\t\t%s /* InfoPlist.strings */," % vg,
        pbx,
        count=1,
    )
    for m in re.finditer(r"/\* Resources \*/ = \{\s*isa = PBXResourcesBuildPhase;\s*buildActionMask = \d+;\s*files = \(([^)]*)\)", pbx):
        if "Main.storyboard in Resources" in m.group(1):
            pbx = pbx[: m.start(1)] + "\n\t\t\t\t%s /* InfoPlist.strings in Resources */," % bf + pbx[m.start(1):]
            break
    m = re.search(r"knownRegions = \(([^)]*)\);", pbx)
    if m:
        have = set(x.strip().strip('"') for x in m.group(1).replace("\n", " ").split(",") if x.strip())
        add = "".join("\t\t\t\t%s,\n" % q(l) for l, _ in FACEID_TEXTS if l not in have)
        if add:
            body = m.group(1).rstrip() + "\n"
            pbx = pbx[: m.start(1)] + body + add + "\t\t\t" + pbx[m.end(1):]
    return pbx


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


# Güvenlik denetimi (2026-11-26): Android yedekleme kuralları.
# Biyometrik anahtarın şifreli deposu (flutter_secure_storage) ve gizli albüm
# hiçbir yedeğe alınmaz (anahtar Keystore'da kalır, geri yüklenince bozulur).
# LOCAL_ONLY: sağlık/finans kayıtları Google bulut yedeğine alınmaz; yalnızca
# yeni telefona doğrudan aktarımda (cihazdan cihaza) taşınır.
LOCAL_ONLY_BACKUP = False

_SECRET_EXCLUDES = (
    '    <exclude domain="sharedpref" path="FlutterSecureStorage.xml"/>\n'
    '    <exclude domain="root" path="app_flutter/gizli_album/"/>\n'
    '    <exclude domain="root" path="app_flutter/gizli_album_tmp/"/>\n'
)
_ALL_EXCLUDES = "".join(
    '    <exclude domain="%s" path="."/>\n' % d for d in ("root", "file", "database", "sharedpref", "external")
)


def android_backup():
    man = "android/app/src/main/AndroidManifest.xml"
    res = "android/app/src/main/res"
    if not os.path.exists(man) or not os.path.isdir(res):
        return
    os.makedirs(res + "/xml", exist_ok=True)
    full = _ALL_EXCLUDES if LOCAL_ONLY_BACKUP else _SECRET_EXCLUDES
    write(res + "/xml/gs100_backup_rules.xml",
          '<?xml version="1.0" encoding="utf-8"?>\n<full-backup-content>\n%s</full-backup-content>\n' % full)
    cloud = _ALL_EXCLUDES if LOCAL_ONLY_BACKUP else _SECRET_EXCLUDES
    write(res + "/xml/gs100_data_extraction_rules.xml",
          '<?xml version="1.0" encoding="utf-8"?>\n<data-extraction-rules>\n'
          '  <cloud-backup>\n%s  </cloud-backup>\n'
          '  <device-transfer>\n%s  </device-transfer>\n'
          '</data-extraction-rules>\n' % (cloud.replace("    <", "    <"), _SECRET_EXCLUDES))
    s = read(man)
    if "android:fullBackupContent" not in s:
        s = s.replace(
            "<application",
            '<application android:fullBackupContent="@xml/gs100_backup_rules" '
            'android:dataExtractionRules="@xml/gs100_data_extraction_rules"',
            1,
        )
        write(man, s)


_SECURE_KT = """class MainActivity : FlutterFragmentActivity() {
    // Hassas ekranlar (şifre kasası, gizli albüm) "gs100/secure_window"
    // kanalıyla FLAG_SECURE ister: ekran görüntüsü, ekran kaydı ve son
    // uygulamalar önizlemesi boş görünür.
    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "gs100/secure_window")
            .setMethodCallHandler { call, result ->
                if (call.method == "set") {
                    if (call.arguments == true) {
                        window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)
                    } else {
                        window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE)
                    }
                    result.success(true)
                } else {
                    result.notImplemented()
                }
            }
    }
}
"""


def android_secure_window():
    """FLAG_SECURE kanalı (MainActivity.kt; FlutterFragmentActivity'den sonra)."""
    for d, _, files in os.walk("android/app/src/main"):
        for f in files:
            if f != "MainActivity.kt":
                continue
            p = os.path.join(d, f)
            s = read(p)
            if "gs100/secure_window" in s:
                continue
            m = re.search(r"class MainActivity\s*:\s*FlutterFragmentActivity\(\)\s*(\{\s*\})?\s*$", s)
            if not m:
                raise SystemExit("MainActivity.kt beklenen biçimde değil: FLAG_SECURE eklenemedi")
            s = s[: m.start()] + _SECURE_KT
            imports = ("import android.view.WindowManager\n"
                       "import io.flutter.embedding.engine.FlutterEngine\n"
                       "import io.flutter.plugin.common.MethodChannel\n")
            s = re.sub(r"(package [^\n]+\n)", r"\1\n" + imports.replace("\\", "\\\\"), s, count=1)
            write(p, s)


if __name__ == "__main__":
    android()
    android_backup()
    android_fragment_activity()
    android_secure_window()
    ios()
    web()
    print("platform folders patched")
