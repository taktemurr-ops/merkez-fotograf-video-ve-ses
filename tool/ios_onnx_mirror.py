"""iOS: onnxruntime pod arşivi için yedek kaynak.

download.onnxruntime.ai zaman zaman ana makine adıyla eşleşmeyen bir TLS
sertifikası sunuyor ve CocoaPods `onnxruntime-c` / `onnxruntime-objc`
arşivlerini indiremiyor. Bu betik yalnızca o durumda devreye girer:
podspec'leri CocoaPods CDN'inden alır, arşiv adresini Microsoft'un aynı
dosyaları barındıran depolama alanına çevirir ve Podfile'a yerel podspec
olarak ekler. TLS doğrulaması hiçbir yerde kapatılmaz; yedek adres de
doğrulanamazsa hiçbir şey değiştirilmez.
"""

import hashlib
import json
import os
import re
import subprocess
import sys

PRIMARY = "download.onnxruntime.ai"
MIRROR = "onnxruntimepackages.z14.web.core.windows.net"
PODS = ["onnxruntime-c", "onnxruntime-objc"]
CDN = "https://cdn.cocoapods.org"


def reachable(url):
    # curl ile, sertifika doğrulaması açık.
    return subprocess.run(
        ["curl", "-sfIL", "-m", "60", "-o", "/dev/null", url]
    ).returncode == 0


def fetch(url):
    # CDN, Python'un varsayılan istemci adını reddediyor (403); curl kullan.
    return subprocess.run(
        ["curl", "-sfL", "-m", "60", "-A", "CocoaPods/1.17.0", url],
        check=True, capture_output=True, text=True,
    ).stdout


def shard(name):
    h = hashlib.md5(name.encode()).hexdigest()
    return h[0], h[1], h[2]


def latest_version(name):
    a, b, c = shard(name)
    for line in fetch(f"{CDN}/all_pods_versions_{a}_{b}_{c}.txt").splitlines():
        parts = line.split("/")
        if parts[0] == name:
            vs = [v for v in parts[1:] if re.fullmatch(r"[0-9.]+", v)]
            return max(vs, key=lambda v: [int(x) for x in v.split(".")])
    raise SystemExit(f"{name} CDN'de bulunamadı")


def spec(name, version):
    a, b, c = shard(name)
    return json.loads(fetch(f"{CDN}/Specs/{a}/{b}/{c}/{name}/{version}/{name}.podspec.json"))


def main():
    version = latest_version("onnxruntime-objc")
    specs = {n: spec(n, version) for n in PODS}
    first = specs["onnxruntime-c"]["source"].get("http", "")
    if PRIMARY not in first or reachable(first):
        print("onnxruntime arşivi doğrudan indirilebiliyor; değişiklik yok.")
        return
    changed = []
    for n, s in specs.items():
        url = s["source"].get("http", "")
        if PRIMARY not in url:
            continue
        alt = url.replace(PRIMARY, MIRROR)
        if not reachable(alt):
            print(f"UYARI: yedek adres de doğrulanamadı: {alt}", file=sys.stderr)
            return
        s["source"]["http"] = alt
        changed.append(n)
    if not changed:
        return
    podfile = "ios/Podfile"
    p = open(podfile).read()
    lines = ""
    for n in changed:
        fn = f"{n}.podspec.json"
        with open(os.path.join("ios", fn), "w") as f:
            json.dump(specs[n], f, indent=2)
        lines += f"  pod '{n}', :podspec => '{fn}'\n"
    p = re.sub(r"(target 'Runner' do\n)", r"\1" + lines.replace("\\", "\\\\"), p, count=1)
    open(podfile, "w").write(p)
    print(f"onnxruntime {version}: {', '.join(changed)} yedek kaynaktan indirilecek ({MIRROR}).")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # yedek kaynak isteğe bağlı; derlemeyi kendisi bozmasın
        print(f"UYARI: onnxruntime yedek kaynak denetimi atlandı: {e}", file=sys.stderr)
