import St from 'gi://St';
import Gio from 'gi://Gio';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';

export default class PDFMergerExtension extends Extension {

    enable() {

        const label = new St.Label({
            text: '📄 PDF'
        });

        this._button = new St.Button({
            child: label,
            reactive: true,
            can_focus: true,
            track_hover: true,
            style: `
                margin-left: 6px;
                margin-right: 6px;
                padding-left: 8px;
                padding-right: 8px;
            `
        });

        this._button.connect('clicked', () => {

            Gio.Subprocess.new(
            [
                "pdf-merger"
            ],
            Gio.SubprocessFlags.NONE
            );
        });

        Main.panel._rightBox.insert_child_at_index(
            this._button,
            0
        );
    }

    disable() {

        if (this._button) {
            this._button.destroy();
            this._button = null;
        }

    }
}
