"""Writes the version details Windows shows in the .exe's Properties -> Details tab.

    python packaging/version_info.py packaging/version_info.txt

An .exe with a name, description, version and copyright looks less like an
anonymous download to antivirus heuristics, and tells users what they're running.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kopi_kopi import __version__  # noqa: E402

TEMPLATE = """VSVersionInfo(
  ffi=FixedFileInfo(filevers={nums}, prodvers={nums}, mask=0x3f, flags=0x0,
                    OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', 'Sethumadhavan N'),
      StringStruct('FileDescription', 'kopi-kopi: copy and paste with taps'),
      StringStruct('FileVersion', '{version}'),
      StringStruct('InternalName', 'kopi-kopi'),
      StringStruct('LegalCopyright', 'Copyright (c) 2026 Sethumadhavan N. MIT License.'),
      StringStruct('OriginalFilename', 'kopi-kopi.exe'),
      StringStruct('ProductName', 'kopi-kopi'),
      StringStruct('ProductVersion', '{version}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""


def main(out):
    nums = tuple(int(n) for n in __version__.split(".")) + (0,)
    Path(out).write_text(TEMPLATE.format(nums=nums, version=__version__), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "version_info.txt")
