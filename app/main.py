import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMenu,
    QMessageBox,
    QToolButton,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QPoint, Qt

from PyQt6.QtWidgets import QListWidget
from PyQt6.QtCore import Qt

from PyQt6.QtCore import QTimer

from pdf_service import PyPDFService
import subprocess
from pathlib import Path

from PyQt6.QtNetwork import (
    QLocalServer,
    QLocalSocket
)
from install_extension import is_gnome, extension_installed, install_extension, enable_extension

from uninstaller import uninstall_application

class DropArea(QLabel):
    def __init__(self, sidebar):
        super().__init__()

        self.sidebar = sidebar
        self.setAcceptDrops(True)

        self.files = []

        self.setText("Drop PDFs Here")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setMinimumHeight(200)

        self.default_style = """
            border: 2px dashed #666;
            border-radius: 10px;
            font-size: 16px;
            padding: 20px;
        """

        self.highlight_style = """
            border: 2px dashed #4CAF50;
            border-radius: 10px;
            font-size: 16px;
            padding: 20px;
        """

        self.setStyleSheet(self.default_style)

    def add_files(self, files):

        for file_path in files:

            if file_path.lower().endswith(".pdf"):

                if file_path not in self.files:
                    self.files.append(file_path)

        self.sidebar.update_file_list()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(self.highlight_style)

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.default_style)

    def dropEvent(self, event):
        self.setStyleSheet(self.default_style)
        files = []

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()

            if file_path.lower().endswith(".pdf"):
                files.append(file_path)

        self.add_files(files)

        event.acceptProposedAction()
        self.sidebar.update_file_list()
        event.acceptProposedAction()
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            files, _ = QFileDialog.getOpenFileNames(
                None,
                "Select PDF Files",
                "",
                "PDF Files (*.pdf)"
            )
            self.add_files(files)
        super().mouseDoubleClickEvent(event)


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self.output_dir = str(Path.home() / "Documents" / "PDF_Merger_Output")

        self.setup_window()
        self.setup_ui()
        self.position_window()
        self.pdf_service = PyPDFService()

        self.drag_position = QPoint()

        self.force_exit = False

        if is_gnome() and not extension_installed():
            self.install_extension_btn.show()
        else:
            self.install_extension_btn.hide()
            self.status_label.setMaximumWidth(280)

    def setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedWidth(320)

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )


    def setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(
            10, 10, 10, 10
        )
        container = QWidget()
        container.setObjectName("container")

        container.setStyleSheet("""
            QWidget#container {
                border-radius: 15px;
                border: 1px solid #444;
            }
        """)
        outer_layout.addWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(
            10, 10, 10, 10
        )

        # Title
        title_bar = QHBoxLayout()
        #drag handle
        self.drag_button = QPushButton("⣿")
        self.drag_button.setFixedWidth(40)
        self.drag_button.setCursor(
            Qt.CursorShape.SizeAllCursor
        )

        self.drag_button.mousePressEvent = self.drag_mouse_press
        self.drag_button.mouseMoveEvent = self.drag_mouse_move
        self.drag_button.mouseReleaseEvent = self.drag_mouse_release

        self.title = QLabel("PDF Merger")

        self.settings_btn = QToolButton()
        self.settings_btn.setIcon(
            QIcon.fromTheme("preferences-system")
        )
        self.settings_btn.setToolTip(
            "Application settings"
        )
        self.settings_btn.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup
        )
        settings_menu = QMenu(self)
        uninstall_action = settings_menu.addAction(
            QIcon.fromTheme("edit-delete"),
            "Uninstall PDF Merger"
        )

        uninstall_action.triggered.connect(
            self.uninstall_application
        )

        self.settings_btn.setMenu(
            settings_menu
        )

        self.close_btn = QPushButton("-")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close)

        title_bar.addWidget(self.drag_button)
        title_bar.addWidget(self.title)
        title_bar.addStretch()
        title_bar.addWidget(self.settings_btn)
        title_bar.addWidget(self.close_btn)

        self.drag_button.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #404040;
                border-radius: 4px;
            }
        """)

        self.title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
            background-color: transparent;
        """)

        self.settings_btn.setStyleSheet("""
            QToolButton {
                border: none;
                border-radius: 8px;
                padding: 6px;
                font-size: 16px;
                background: transparent;
            }

            QToolButton:hover {
                background: rgba(255,255,255,0.08);
            }

            QToolButton:pressed {
                background: rgba(255,255,255,0.15);
            }
        """)

        settings_menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 6px;
            }

            QMenu::item {
                padding: 8px 24px 8px 12px;
                border-radius: 6px;
            }

            QMenu::item:selected {
                background-color: #3a82f7;
            }

            QMenu::separator {
                height: 1px;
                background: #444;
                margin: 4px 0px;
            }
        """)

        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #d32f2f;
                border-radius: 5px;
            }
        """)

        # Drop area
        self.drop_area = DropArea(self)
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.drop_area.setMinimumHeight(200)

        self.drop_area.setStyleSheet("""
            border: 2px dashed #666;
            border-radius: 10px;
            font-size: 16px;
            padding: 20px;
        """)

        #File list
        self.file_list = QListWidget()
        self.file_list.setDragDropMode(
            QListWidget.DragDropMode.InternalMove
        )
        self.file_list.setMinimumHeight(120)
        self.file_list.model().rowsMoved.connect(
            self.sync_file_order
        )

        self.output_label = QLabel("Output Path:")
        self.output_label.setToolTip(
            self.output_dir
        )
        # Buttons
        merge_btn = QPushButton("Merge PDFs")
        remove_btn = QPushButton("Remove Selected")
        clear_btn = QPushButton("Clear All")
        self.set_output_btn = QPushButton("Set Output Path")
        self.open_output_btn = QPushButton("Open Output Path")

        self.merge_btn = merge_btn
        self.remove_btn = remove_btn
        self.clear_btn = clear_btn
        self.open_output_btn = self.open_output_btn

        self.remove_btn.clicked.connect(
            self.remove_selected
        )

        self.clear_btn.clicked.connect(
            self.clear_files
        )

        self.merge_btn.clicked.connect(
            self.merge_pdfs
        )

        self.set_output_btn.clicked.connect(
            self.set_output_path
        )

        self.open_output_btn.clicked.connect(
            self.open_output_path
        )

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.set_output_btn)
        output_layout.addWidget(self.open_output_btn)

        #Status label
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Developed by: Dhakshinesh")
        self.status_label.setWordWrap(True)

        self.status_label.setStyleSheet("""
            QLabel {
                color: #BBBBBB;
                padding: 5px;
            }
        """)

        #Extension Button : Shows only if the user is on GNOME and the extension is not installed
        self.install_extension_btn = QPushButton("🧩")
        self.install_extension_btn.setToolTip(
            """
        Adds a PDF icon to the GNOME top panel.

        The panel widget lets you quickly open
        PDF Merger from the menu bar without
        searching for the application.
        """
        )
        self.install_extension_btn.clicked.connect(
            self.install_gnome_extension
        )
        self.status_label.setMaximumWidth(250)
        status_layout.addWidget(self.status_label)
        self.install_extension_btn.setMaximumWidth(30)
        status_layout.addWidget(self.install_extension_btn)

        layout.addLayout(title_bar)
        layout.addWidget(self.drop_area)
        layout.addWidget(self.file_list)
        layout.addWidget(self.merge_btn)
        layout.addWidget(self.remove_btn)
        layout.addWidget(self.clear_btn)
        layout.addLayout(output_layout)
        layout.addLayout(status_layout)

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(35,35,35,230);
                color: white;
                border-left: 1px solid #444;
            }

            QPushButton {
                background-color: #404040;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #555555;
            }
        """)

        # Let Qt determine the required height
        self.adjustSize()

    def update_file_list(self):
        self.file_list.clear()

        for path in self.drop_area.files:

            filename = path.split("/")[-1]

            self.file_list.addItem(filename)

    def remove_selected(self):
        current_row = self.file_list.currentRow()
        
        if current_row >= 0:
            self.file_list.takeItem(current_row)
            self.drop_area.files.pop(current_row)

    def clear_files(self):
        self.file_list.clear()
        self.drop_area.files.clear()

    def sync_file_order(self):

        ordered_files = []

        for i in range(self.file_list.count()):

            displayed_name = self.file_list.item(i).text()

            for path in self.drop_area.files:

                if path.endswith(displayed_name):

                    ordered_files.append(path)
                    break

        self.drop_area.files = ordered_files

    def merge_pdfs(self):
        files = self.drop_area.files

        if len(files) < 2:
            self.show_warning(
                "Please add at least 2 PDFs"
            )
            return

        self.merge_btn.setEnabled(False)

        try:
            result = self.pdf_service.merge_pdfs(files, self.output_dir)

            self.show_success(f"Merged PDF saved to:\n{result}")

            # Open merged PDF
            subprocess.Popen(
                ["xdg-open", str(Path(result).resolve())]
            )

        except Exception as e:
            self.show_error(f"Error: {str(e)}")
        finally:
            self.merge_btn.setEnabled(True)

    def set_output_path(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.output_dir
        )

        if folder:
            self.output_dir = folder

            self.show_info(f"Output folder set to:\n{folder}")

    def open_output_path(self):

        Path(self.output_dir).mkdir(
            parents=True,
            exist_ok=True
        )

        subprocess.Popen([
            "xdg-open",
            self.output_dir
        ])

    def show_success(self, message):
        self.status_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                padding: 5px;
            }
        """)
        self.status_label.setText(f"✓ {message}")
        QTimer.singleShot(5000, self.clear_status)

    def show_error(self, message):
        self.status_label.setStyleSheet("""
            QLabel {
                color: #F44336;
                padding: 5px;
            }
        """)
        self.status_label.setText(f"✗ {message}")
        QTimer.singleShot(5000, self.clear_status)

    def show_warning(self, message):
        self.status_label.setStyleSheet("""
            QLabel {
                color: #FF9800;
                padding: 5px;
            }
        """)
        self.status_label.setText(f"⚠ {message}")
        QTimer.singleShot(5000, self.clear_status)

    def show_info(self, message):
        self.status_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                padding: 5px;
            }
        """)
        self.status_label.setText(f"ℹ {message}")
        QTimer.singleShot(5000, self.clear_status)

    def clear_status(self):
        self.status_label.setStyleSheet("""
            QLabel {
                color: #BBBBBB;
                padding: 5px;
                border-top: 1px solid #444;
            }
        """)
        self.status_label.setText("Developed by: Dhakshinesh")

    def closeEvent(self, event):
        if self.force_exit:
            event.accept()

        else:
            self.hide()
            event.ignore()

    def install_gnome_extension(self):

        try:
            install_extension()
            enable_extension()

            self.show_success("Extension installed! Restart to see widget.")

            self.install_extension_btn.hide()
            self.status_label.setMaximumWidth(280)

        except Exception as e:
            print(f"Failed to install extension: {str(e)}")
            self.show_error(f"Failed to install extension: {str(e)}")

    def uninstall_application(self):
        try:
            uninstall_application(self)
            self.show_info("Restart the application to complete uninstallation.")
            #sleep and end application after 2 seconds
            self.force_exit = True
            QTimer.singleShot(2000, self.close)

        except Exception as e:
            self.show_error(f"Failed to uninstall: {str(e)}")
    def drag_mouse_press(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()

    def drag_mouse_move(self, event):

        if event.buttons() & Qt.MouseButton.LeftButton:

            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

            event.accept()

    def drag_mouse_release(self, event):
        pass

    def position_window(self):
        screen = QApplication.primaryScreen().availableGeometry()

        self.move(
            screen.width() - self.width() - 10,
            50
        )


if __name__ == "__main__":

    # Check if another instance is already running
    socket = QLocalSocket()
    socket.connectToServer("pdf_merger")

    if socket.waitForConnected(500):

        socket.write(b"show")
        socket.flush()
        socket.waitForBytesWritten()

        sys.exit(0)

    app = QApplication(sys.argv)

    window = Sidebar()
    window.show()

    # Create single-instance server
    server = QLocalServer()

    if not server.listen("pdf_merger"):

        # Socket may be stale from a crash
        QLocalServer.removeServer("pdf_merger")

        if not server.listen("pdf_merger"):
            print("Failed to create local server")
            sys.exit(1)

    def handle_connection():

        client = server.nextPendingConnection()

        if client:

            client.waitForReadyRead(100)

            message = bytes(
                client.readAll()
            ).decode()

            if message == "show":

                window.show()

                window.raise_()

                window.activateWindow()

            client.disconnectFromServer()

    server.newConnection.connect(
        handle_connection
    )

    sys.exit(app.exec())
