from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog,
                             QLabel, QVBoxLayout, QWidget, QMessageBox, QStatusBar,
                             QHBoxLayout, QLineEdit) # Aggiunto QLineEdit
from PyQt5.QtGui import QIcon, QPixmap
import csv
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deeper Cleaner - Arc-Team Tools")
        self.setWindowIcon(QIcon('deeper_cleaner_icon.png'))
        self.setGeometry(100, 100, 400, 350) # Aumentata altezza per il nuovo campo

        layout = QVBoxLayout()

        # Header
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
        self.package_label.setStyleSheet("font-size: 10px; color: gray;")
        title_layout.addWidget(self.package_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        layout.addSpacing(10)

        # --- NUOVO CAMPO: Quota Superficie ---
        self.label_surface = QLabel("Surface Altitude (m above sea level):")
        layout.addWidget(self.label_surface)
        self.input_surface = QLineEdit()
        self.input_surface.setPlaceholderText("e.g. 195.5")
        layout.addWidget(self.input_surface)
        # -------------------------------------

        # Input file
        self.label_input = QLabel("Select input CSV file:")
        layout.addWidget(self.label_input)
        self.button_select_input = QPushButton("Choose Input File")
        self.button_select_input.clicked.connect(self.open_input_file_dialog)
        layout.addWidget(self.button_select_input)

        # Output file
        self.label_output = QLabel("Select output CSV file:")
        layout.addWidget(self.label_output)
        self.button_select_output = QPushButton("Choose Output File")
        self.button_select_output.clicked.connect(self.open_output_file_dialog)
        layout.addWidget(self.button_select_output)

        # Clean button
        self.button_clean = QPushButton("Clean Data")
        self.button_clean.clicked.connect(self.clean_data)
        self.button_clean.setEnabled(False)
        layout.addWidget(self.button_clean)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        status_layout = QHBoxLayout()
        status_label = QLabel("Powered by Arc-Team")
        status_layout.addWidget(status_label)
        logo_label = QLabel()
        logo_pixmap = QPixmap('./icons/arc-team_logo.png').scaled(300, 70)
        logo_label.setPixmap(logo_pixmap)
        status_layout.addWidget(logo_label)
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        self.statusBar.addPermanentWidget(status_widget)

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

        # Recupero e validazione della quota superficie
        surface_alt_str = self.input_surface.text().replace(',', '.')
        try:
            surface_alt = float(surface_alt_str) if surface_alt_str else 0.0
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number for surface altitude.")
            return

        # Aggiornato l'header con il nuovo campo
        header = ["latitude", "longitude", "depth", "timestamp", "temperature", "altitude_asl"]

        def is_valid(row):
            if len(row) < 5: # Modificato a < 5 per sicurezza
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
                        try:
                            depth = float(row[2])
                            # Calcolo: Quota Superficie - Profondità
                            alt_asl = surface_alt - depth
                            row.append(f"{alt_asl:.2f}") # Aggiunge il valore calcolato
                            writer.writerow(row)
                        except ValueError:
                            continue # Salta righe con depth non numerica

            QMessageBox.information(self, "Success", f"Cleaned data with ASL altitude saved to {self.output_file_path}!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
