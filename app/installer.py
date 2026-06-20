import os
import shutil
import subprocess
from pathlib import Path


EXTENSION_UUID = "pdf-merger@dhakshinesh.com"


def install_appimage():

    appimage = os.environ.get("APPIMAGE")

    if not appimage:
        return

    install_dir = (
        Path.home()
        / ".local"
        / "share"
        / "pdf-merger"
    )

    install_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    target = install_dir / "PDF-Merger.AppImage"

    if not target.exists():

        shutil.copy2(
            appimage,
            target
        )

        target.chmod(0o755)

    launcher_dir = (
        Path.home()
        / ".local"
        / "bin"
    )

    launcher_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    launcher = launcher_dir / "pdf-merger"

    launcher.write_text(
        f"""#!/bin/bash
export PDF_MERGER_INSTALLED=1
exec "{target}" "$@"
"""
    )

    launcher.chmod(0o755)


def install_desktop_entry():

    desktop_dir = (
        Path.home()
        / ".local"
        / "share"
        / "applications"
    )

    desktop_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    desktop_file = desktop_dir / "pdf-merger.desktop"

    desktop_file.write_text(
        """[Desktop Entry]
Type=Application
Name=PDF Merger
Exec=pdf-merger
Terminal=false
Categories=Office;
"""
    )


def main():

    install_appimage()

    install_desktop_entry()

    env = os.environ.copy()

    env["PDF_MERGER_INSTALLED"] = "1"

    subprocess.Popen(
        ["pdf-merger"],
        env=env
    )


if __name__ == "__main__":
    main()