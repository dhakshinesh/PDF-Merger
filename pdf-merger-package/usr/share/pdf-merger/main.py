import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMessageBox,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog
)
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl, Qt

from PyQt6.QtWidgets import QListWidget
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtCore import QTimer

from pdf_service import PyPDFService
import subprocess
from pathlib import Path

from PyQt6.QtNetwork import (
    QLocalServer,
    QLocalSocket
)

class DropArea(QLabel):
    def __init__(self):
        super().__init__()

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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(self.highlight_style)

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.default_style)

    def dropEvent(self, event):
        self.setStyleSheet(self.default_style)

        for url in event.mimeData().urls():

            file_path = url.toLocalFile()

            if file_path.lower().endswith(".pdf"):

                if file_path not in self.files:
                    self.files.append(file_path)

        self.parent().update_file_list()

        event.acceptProposedAction()


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self.output_dir = str(Path.home() / "Documents" / "PDF_Merger_Output")

        self.setup_window()
        self.setup_ui()
        self.position_window()
        self.pdf_service = PyPDFService()

    def setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.setFixedWidth(320)

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title_bar = QHBoxLayout()

        title = QLabel("PDF Merger")

        close_btn = QPushButton("-")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.closeEvent)

        title_bar.addWidget(title)
        title_bar.addStretch()
        title_bar.addWidget(close_btn)

        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
        """)

        close_btn.setStyleSheet("""
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
        self.drop_area = DropArea()
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
        self.status_label = QLabel("Developed by: Dhakshinesh")
        self.status_label.setWordWrap(True)

        self.status_label.setStyleSheet("""
            QLabel {
                color: #BBBBBB;
                font-size: 12px;
                padding: 5px;
                border-top: 1px solid #444;
            }
        """)

        layout.addLayout(title_bar)
        layout.addWidget(self.drop_area)
        layout.addWidget(self.file_list)
        layout.addWidget(self.merge_btn)
        layout.addWidget(self.remove_btn)
        layout.addWidget(self.clear_btn)
        layout.addLayout(output_layout)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

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
                font-size: 12px;
                padding: 5px;
                border-top: 1px solid #444;
            }
        """)
        self.status_label.setText("Developed by: Dhakshinesh")

    def closeEvent(self):
        self.hide()
    
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
