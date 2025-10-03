from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog,
                             QLabel, QVBoxLayout, QWidget, QMessageBox, QStatusBar, QHBoxLayout)
from PyQt5.QtGui import QIcon, QPixmap
import csv
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deeper Cleaner - Arc-Team Tools")
        self.setWindowIcon(QIcon('deeper_cleaner_icon.png'))
        self.setGeometry(100, 100, 400, 280)  # Aumentato l'altezza per il logo

        # Main layout
        layout = QVBoxLayout()

        # Header with icon and app name
        header_layout = QHBoxLayout()
        self.icon_label = QLabel()
        pixmap = QPixmap('./icons/deeper_cleaner_icon.png').scaled(150, 113)
        self.icon_label.setPixmap(pixmap)
        header_layout.addWidget(self.icon_label)

        title_layout = QVBoxLayout()
        self.app_name_label = QLabel("Deeper Cleaner")
        self.app_name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        title_layout.addWidget(self.app_name_label)

        self.package_label = QLabel("(Arc-Team Tools)")
        self.package_label.setStyleSheet("font-size: 12px; color: gray;")
        title_layout.addWidget(self.package_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        layout.addSpacing(10)

        # Input file selection
        self.label_input = QLabel("Select input CSV file:")
        layout.addWidget(self.label_input)

        self.button_select_input = QPushButton("Choose Input File")
        self.button_select_input.clicked.connect(self.open_input_file_dialog)
        layout.addWidget(self.button_select_input)

        # Output file selection
        self.label_output = QLabel("Select output CSV file:")
        layout.addWidget(self.label_output)

        self.button_select_output = QPushButton("Choose Output File")
        self.button_select_output.clicked.connect(self.open_output_file_dialog)
        layout.addWidget(self.button_select_output)

        # Clean data button
        self.button_clean = QPushButton("Clean Data")
        self.button_clean.clicked.connect(self.clean_data)
        self.button_clean.setEnabled(False)
        layout.addWidget(self.button_clean)

        # Container
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Status bar with logo
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Add "Powered by Arc-Team" label and logo to status bar
        status_layout = QHBoxLayout()
        status_label = QLabel("Powered by Arc-Team")
        status_layout.addWidget(status_label)

        # Add logo (replace 'arc_team_logo.png' with your file)
        logo_label = QLabel()
        logo_pixmap = QPixmap('./icons/arc-team_logo.png').scaled(300, 70)  # Adjust size as needed
        logo_label.setPixmap(logo_pixmap)
        status_layout.addWidget(logo_label)

        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        self.statusBar.addPermanentWidget(status_widget)

        # File paths
        self.input_file_path = None
        self.output_file_path = None

    def open_input_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Input File", "", "CSV Files (*.csv)")
        if file_path:
            self.input_file_path = file_path
            self.label_input.setText(f"Input file: {file_path}")
            self.check_if_ready_to_clean()

    def open_output_file_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Choose Output File", "", "CSV Files (*.csv)")
        if file_path:
            self.output_file_path = file_path
            self.label_output.setText(f"Output file: {file_path}")
            self.check_if_ready_to_clean()

    def check_if_ready_to_clean(self):
        self.button_clean.setEnabled(self.input_file_path is not None and self.output_file_path is not None)

    def clean_data(self):
        if not self.input_file_path or not self.output_file_path:
            return

        header = ["latitude", "longitude", "depth", "timestamp", "temperature"]

        def is_valid(row):
            if len(row) != 5:
                return False
            try:
                lat, lon = float(row[0]), float(row[1])
                return lat != 0.0 and lon != 0.0
            except ValueError:
                return False

        try:
            with open(self.input_file_path, newline='') as infile, open(self.output_file_path, 'w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                writer.writerow(header)
                for row in reader:
                    row = [item.strip() for item in row]
                    if is_valid(row):
                        writer.writerow(row)

            QMessageBox.information(self, "Success", f"Cleaned data saved to {self.output_file_path}!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
