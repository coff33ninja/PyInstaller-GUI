import sys
import subprocess
import os
import json
import tempfile
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QPushButton, QWidget, QCheckBox, QFileDialog, QLabel, QLineEdit, QHBoxLayout, QMenuBar, QMenu, QMessageBox, QToolTip, QGroupBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSlot, QThread, pyqtSignal

class PyInstallerThread(QThread):
    signal_log = pyqtSignal(str)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def run(self):
        process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        log_output = stdout.decode() + "\n" + stderr.decode()
        self.signal_log.emit(log_output)

class PyInstallerGUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # Menu
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')

        open_action = QAction("Open Script", self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        save_config_action = QAction("Save Config", self)
        save_config_action.triggered.connect(self.save_config)
        file_menu.addAction(save_config_action)

        load_config_action = QAction("Load Config", self)
        load_config_action.triggered.connect(self.load_config)
        file_menu.addAction(load_config_action)

        # Layout
        main_layout = QVBoxLayout()

        # File input for the Python script path
        self.file_path_input = QLineEdit(self)
        file_path_layout = QHBoxLayout()
        file_path_label = QLabel("Python Script Path: ", self)
        file_path_select_button = QPushButton("Select", self)
        file_path_select_button.clicked.connect(self.open_file_dialog)
        file_path_layout.addWidget(file_path_label)
        file_path_layout.addWidget(self.file_path_input)
        file_path_layout.addWidget(file_path_select_button)
        main_layout.insertLayout(0, file_path_layout)

        # Python Script Text Edit
        self.script_edit = QTextEdit(self)
        script_label = QLabel("Optional Paste or Type Python Script Here:", self)
        main_layout.addWidget(script_label)
        main_layout.addWidget(self.script_edit)

        # Options Layout
        options_layout = QVBoxLayout()

        # Basic Options Group
        basic_options_group = QGroupBox("Basic Options", self)
        basic_options_layout = QVBoxLayout()

        # PyInstaller Basic Options
        self.one_dir_checkbox = QCheckBox('One Directory', self)
        self.one_file_checkbox = QCheckBox('One File', self)
        self.windowed_checkbox = QCheckBox('Windowed', self)
        self.no_console_checkbox = QCheckBox('No Console', self)

        basic_options_layout.addWidget(self.one_dir_checkbox)
        basic_options_layout.addWidget(self.one_file_checkbox)
        basic_options_layout.addWidget(self.windowed_checkbox)
        basic_options_layout.addWidget(self.no_console_checkbox)

        # Icon Option
        self.icon_edit = QLineEdit(self)
        icon_layout = QHBoxLayout()
        icon_label = QLabel("Icon Path: ", self)
        icon_select_button = QPushButton("Select", self)
        icon_select_button.clicked.connect(self.select_icon)
        icon_layout.addWidget(icon_label)
        icon_layout.addWidget(self.icon_edit)
        icon_layout.addWidget(icon_select_button)
        basic_options_layout.addLayout(icon_layout)

        basic_options_group.setLayout(basic_options_layout)

        # Advanced Options Group
        advanced_options_group = QGroupBox("Advanced Options", self)
        advanced_options_layout = QVBoxLayout()

        # Name Option
        name_layout = QHBoxLayout()
        name_label = QLabel("Name: ", self)
        self.name_edit = QLineEdit(self)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        advanced_options_layout.addLayout(name_layout)

        # Paths Option
        paths_layout = QHBoxLayout()
        paths_label = QLabel("Additional Paths (':' separated): ", self)
        self.paths_edit = QLineEdit(self)
        paths_layout.addWidget(paths_label)
        paths_layout.addWidget(self.paths_edit)
        advanced_options_layout.addLayout(paths_layout)

        # Hidden Imports
        hidden_imports_layout = QHBoxLayout()
        hidden_imports_label = QLabel("Hidden Imports (',' separated): ", self)
        self.hidden_imports_edit = QLineEdit(self)
        hidden_imports_layout.addWidget(hidden_imports_label)
        hidden_imports_layout.addWidget(self.hidden_imports_edit)
        advanced_options_layout.addLayout(hidden_imports_layout)

        # Distpath Option
        distpath_layout = QHBoxLayout()
        distpath_label = QLabel("Distpath: ", self)
        self.distpath_edit = QLineEdit(self)
        distpath_layout.addWidget(distpath_label)
        distpath_layout.addWidget(self.distpath_edit)
        advanced_options_layout.addLayout(distpath_layout)

        # Workpath Option
        workpath_layout = QHBoxLayout()
        workpath_label = QLabel("Workpath: ", self)
        self.workpath_edit = QLineEdit(self)
        workpath_layout.addWidget(workpath_label)
        workpath_layout.addWidget(self.workpath_edit)
        advanced_options_layout.addLayout(workpath_layout)

        # Specpath Option
        specpath_layout = QHBoxLayout()
        specpath_label = QLabel("Specpath: ", self)
        self.specpath_edit = QLineEdit(self)
        specpath_layout.addWidget(specpath_label)
        specpath_layout.addWidget(self.specpath_edit)
        advanced_options_layout.addLayout(specpath_layout)

        # UPX directory Option
        upx_dir_layout = QHBoxLayout()
        upx_dir_label = QLabel("UPX Directory: ", self)
        self.upx_dir_edit = QLineEdit(self)
        upx_dir_layout.addWidget(upx_dir_label)
        upx_dir_layout.addWidget(self.upx_dir_edit)
        advanced_options_layout.addLayout(upx_dir_layout)

        # Log Level Option
        log_level_layout = QHBoxLayout()
        log_level_label = QLabel("Log Level: ", self)
        self.log_level_edit = QLineEdit(self)
        log_level_layout.addWidget(log_level_label)
        log_level_layout.addWidget(self.log_level_edit)
        advanced_options_layout.addLayout(log_level_layout)

        # Version File (Windows)
        self.version_file_edit = QLineEdit(self)
        version_file_layout = QHBoxLayout()
        version_file_label = QLabel("Version File Path (Windows): ", self)
        version_file_select_button = QPushButton("Select", self)
        version_file_select_button.clicked.connect(self.select_version_file)
        version_file_layout.addWidget(version_file_label)
        version_file_layout.addWidget(self.version_file_edit)
        version_file_layout.addWidget(version_file_select_button)
        advanced_options_layout.addLayout(version_file_layout)

        self.exclude_edit = QLineEdit(self)
        exclude_layout = QHBoxLayout()
        exclude_label = QLabel("Exclude Modules (',' separated): ", self)
        exclude_layout.addWidget(exclude_label)
        exclude_layout.addWidget(self.exclude_edit)
        advanced_options_layout.addLayout(exclude_layout)

        self.add_data_edit = QLineEdit(self)
        add_data_layout = QHBoxLayout()
        add_data_label = QLabel("Add Data (format: src;dst): ", self)
        add_data_layout.addWidget(add_data_label)
        add_data_layout.addWidget(self.add_data_edit)
        advanced_options_layout.addLayout(add_data_layout)

        advanced_options_group.setLayout(advanced_options_layout)

        main_layout.addWidget(basic_options_group)
        main_layout.addWidget(advanced_options_group)

        # Packing the options into the main layout
        main_layout.addLayout(options_layout)

        # Build Button
        self.build_button = QPushButton('Build', self)
        self.build_button.clicked.connect(self.on_build_clicked)
        main_layout.addWidget(self.build_button)

        # Log Viewer
        self.log_widget = QTextEdit(self)
        main_layout.addWidget(self.log_widget)

        # Setting the layout
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle('PyInstaller GUI')
        self.setGeometry(100, 100, 400, 300)

    def apply_styles(self):
        # Main Window Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QLabel {
                color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                border: none;
                color: #ecf0f1;
                padding: 5px 15px;
                text-align: center;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a5276;
            }
            QTextEdit, QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                border-radius: 3px;
                padding: 3px;
            }
            QCheckBox {
                color: #ecf0f1;
            }
            QMenuBar::item {
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
            }
            QMenu {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #3498db;
            }
            QMenu::item::selected {
                background-color: #3498db;
            }
        """)

        # Log Widget Specific Styling
        self.log_widget.setStyleSheet("""
            QTextEdit {
                background-color: #000;
                color: #00FF00;
                font-family: "Courier New", monospace;
            }
        """)

    @pyqtSlot()
    def save_config(self):
        options = {
            "one_dir": self.one_dir_checkbox.isChecked(),
            "one_file": self.one_file_checkbox.isChecked(),
            # ... continue for all other settings
        }
        with open("config.json", "w") as f:
            json.dump(options, f)

    @pyqtSlot()
    def load_config(self):
        try:
            with open("config.json", "r") as f:
                options = json.load(f)
                self.one_dir_checkbox.setChecked(options.get("one_dir", False))
                self.one_file_checkbox.setChecked(options.get("one_file", False))
                # ... continue for all other settings
        except FileNotFoundError:
            self.log_widget.append("Config file not found!")

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Python Script", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_name:
            self.file_path_input.setText(file_name)

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        for file in files:
            if file.endswith(".py"):
                self.file_path_input.setText(file)
            else:
                QMessageBox.critical(self, "Error", f"Unsupported file type: {file}")

    def select_icon(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Icon Files (*.ico);;All Files (*)", options=options)
        if file_name:
            self.icon_edit.setText(file_name)

    def select_version_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Version File", "", "All Files (*)", options=options)
        if file_name:
            self.version_file_edit.setText(file_name)

    def on_build_clicked(self):
        if not self.file_path_input.text() and not self.script_edit.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Please select a Python file or enter Python code directly.")
            return
        try:
            cmd = ["pyinstaller"]

            if self.one_dir_checkbox.isChecked():
                cmd.append("--onedir")
            if self.one_file_checkbox.isChecked():
                cmd.append("--onefile")
            if self.windowed_checkbox.isChecked():
                cmd.append("--windowed")
            if self.no_console_checkbox.isChecked():
                cmd.append("--noconsole")
            if self.name_edit.text():
                cmd.extend(["--name", self.name_edit.text()])
            if self.paths_edit.text():
                paths = self.paths_edit.text().split(":")
                for path in paths:
                    cmd.extend(["--paths", path])
            if self.hidden_imports_edit.text():
                hidden_imports = self.hidden_imports_edit.text().split(",")
                for hi in hidden_imports:
                    cmd.extend(["--hidden-import", hi])
            if self.icon_edit.text():
                cmd.extend(["--icon", self.icon_edit.text()])
            if self.version_file_edit.text():
                cmd.extend(["--version-file", self.version_file_edit.text()])
            if self.distpath_edit.text():
                cmd.extend(["--distpath", self.distpath_edit.text()])
            if self.workpath_edit.text():
                cmd.extend(["--workpath", self.workpath_edit.text()])
            if self.specpath_edit.text():
                cmd.extend(["--specpath", self.specpath_edit.text()])
            if self.upx_dir_edit.text():
                cmd.extend(["--upx-dir", self.upx_dir_edit.text()])
            if self.log_level_edit.text():
                cmd.extend(["--log-level", self.log_level_edit.text()])
            if self.exclude_edit.text():
                excludes = self.exclude_edit.text().split(",")
                for ex in excludes:
                    cmd.extend(["--exclude", ex])
            if self.add_data_edit.text():
                data_pairs = self.add_data_edit.text().split(";")
                for pair in data_pairs:
                    cmd.extend(["--add-data", pair])
        except Exception as e:
            self.log_widget.append(str(e))

        script_path = "temp_script.py"
        with open(script_path, "w") as f:
            f.write(self.script_edit.toPlainText())
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tf:
            tf.write(self.script_edit.toPlainText().encode())
            script_path = tf.name

        cmd.append(script_path)

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        log_output = stdout.decode() + "\n" + stderr.decode()
        self.log_widget.setPlainText(log_output)

        os.remove(script_path)
        thread = PyInstallerThread(cmd)
        thread.signal_log.connect(self.update_log)
        thread.start()

    def update_log(self, log):
        self.log_widget.setPlainText(log)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyInstallerGUI()
    window.show()
    sys.exit(app.exec())
