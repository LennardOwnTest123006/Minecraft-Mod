"""Package src/main/resources into a loadable Fabric mod jar.

A Fabric mod jar is an ordinary zip with fabric.mod.json at the root next to
assets/ and data/, so no compiler is involved for a content-only mod.

Run with:  python3 tools/build_jar.py
"""
import json
import os
import sys
import zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(ROOT, "src/main/resources")
BUILD = os.path.join(ROOT, "build")

MANIFEST = (
    "Manifest-Version: 1.0\r\n"
    "Implementation-Title: {name}\r\n"
    "Implementation-Version: {version}\r\n"
    "Fabric-Loom-Version: n/a (content-only mod, no compiled classes)\r\n"
    "\r\n"
)
# Fixed timestamp so rebuilding the same sources gives a byte-identical jar.
STAMP = (2026, 1, 1, 0, 0, 0)


def main():
    with open(os.path.join(RES, "fabric.mod.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    name, version = meta["id"], meta["version"]

    entries = []
    for dirpath, dirnames, filenames in os.walk(RES):
        dirnames.sort()
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            entries.append((os.path.relpath(full, RES).replace(os.sep, "/"), full))
    entries.sort()

    os.makedirs(BUILD, exist_ok=True)
    out = os.path.join(BUILD, f"{name}-{version}.jar")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        info = zipfile.ZipInfo("META-INF/MANIFEST.MF", STAMP)
        info.external_attr = 0o644 << 16
        z.writestr(info, MANIFEST.format(name=meta["name"], version=version))
        for arcname, full in entries:
            info = zipfile.ZipInfo(arcname, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(full, "rb") as fh:
                z.writestr(info, fh.read())

    size = os.path.getsize(out)
    print(f"built {os.path.relpath(out, ROOT)}  ({size:,} bytes, "
          f"{len(entries) + 1} entries)")

    # Sanity-check what we just wrote.
    with zipfile.ZipFile(out) as z:
        bad = z.testzip()
        if bad:
            sys.exit(f"corrupt entry in jar: {bad}")
        names = z.namelist()
        for required in ("fabric.mod.json",):
            if required not in names:
                sys.exit(f"jar is missing {required} at its root")
        json.loads(z.read("fabric.mod.json"))
        assets = [n for n in names if n.startswith("assets/")]
        data = [n for n in names if n.startswith("data/")]
        print(f"  fabric.mod.json OK, {len(assets)} asset files, {len(data)} data files")
    return out


if __name__ == "__main__":
    main()
