import shutil
import subprocess
import os
from pathlib import Path

EXTENSION_DIR = (
            Path.home()
            / ".local/share/gnome-shell/extensions"
            / "pdf-merger@dhakshinesh.com"
        )

def is_gnome():
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "")
        return "GNOME" in desktop.upper()

def extension_installed():
        print(__file__)
        print(os.path.dirname(__file__))
        print(f"Checking if extension is installed at {EXTENSION_DIR}")
        print(f"Extension directory exists: {EXTENSION_DIR.exists()}")
        return EXTENSION_DIR.exists()

def install_extension():
        source = (Path(__file__).parent).parent / "extension"

        EXTENSION_DIR.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if EXTENSION_DIR.exists():
            shutil.rmtree(EXTENSION_DIR)

        shutil.copytree(
            source,
            EXTENSION_DIR
        )

def enable_extension():
        try:
            result = subprocess.run(
                [
                    "gnome-extensions",
                    "enable",
                    "pdf-merger@dhakshinesh.com"
                ],
                capture_output=True,
                text=True
            )
            print(result.returncode)
        except Exception:
            pass
