
import subprocess
from pathlib import Path
import shutil

EXTENSION_UUID = "pdf-merger@dhakshinesh.com"

def uninstall_application(self):

    subprocess.run(
        [
            "gnome-extensions",
            "disable",
            EXTENSION_UUID
        ],
        check=False
    )

    Path.home().joinpath(
        ".local/bin/pdf-merger"
    ).unlink(missing_ok=True)

    Path.home().joinpath(
        ".local/share/applications/pdf-merger.desktop"
    ).unlink(missing_ok=True)

    shutil.rmtree(
        Path.home() / ".local/share/pdf-merger",
        ignore_errors=True
    )

    shutil.rmtree(
        Path.home()
        / ".local/share/gnome-shell/extensions"
        / EXTENSION_UUID,
        ignore_errors=True
    )

    self.close()