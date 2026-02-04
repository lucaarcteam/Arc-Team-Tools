import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog,
                             QLabel, QVBoxLayout, QWidget, QMessageBox, QStatusBar,
                             QHBoxLayout)
from PyQt5.QtGui import QIcon, QPixmap
from PIL import Image

class ExifEraserApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exif Eraser - Arc-Team Tools")
        # Assicurati di avere l'icona nella cartella corretta
        self.setWindowIcon(QIcon('./icons/exif_eraser_icon.png'))
        self.setGeometry(100, 100, 400, 350)

        layout = QVBoxLayout()

        # Header con Logo e Titolo
        header_layout = QHBoxLayout()
        self.icon_label = QLabel()
        # Carica l'icona specifica del software
        pixmap = QPixmap('./icons/exif_eraser_icon.png').scaled(150, 113)
        self.icon_label.setPixmap(pixmap)
        header_layout.addWidget(self.icon_label)

        title_layout = QVBoxLayout()
        self.app_name_label = QLabel("Exif Eraser")
        self.app_name_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        title_layout.addWidget(self.app_name_label)
        self.package_label = QLabel("(Arc-Team Tools)")
        self.package_label.setStyleSheet("font-size: 10px; color: gray;")
        title_layout.addWidget(self.package_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        layout.addSpacing(20)

        # Selezione Cartella Input
        self.label_input = QLabel("Cartella Foto Originali (con EXIF):")
        layout.addWidget(self.label_input)
        self.button_select_input = QPushButton("Seleziona Cartella Sorgente")
        self.button_select_input.clicked.connect(self.open_input_dir_dialog)
        layout.addWidget(self.button_select_input)

        layout.addSpacing(10)

        # Selezione Cartella Output
        self.label_output = QLabel("Cartella Destinazione (senza EXIF):")
        layout.addWidget(self.label_output)
        self.button_select_output = QPushButton("Seleziona Cartella Destinazione")
        self.button_select_output.clicked.connect(self.open_output_dir_dialog)
        layout.addWidget(self.button_select_output)

        layout.addSpacing(20)

        # Bottone Esegui
        self.button_run = QPushButton("Rimuovi Metadati EXIF")
        self.button_run.setStyleSheet("background-color: #2c3e50; color: white; font-weight: bold; height: 30px;")
        self.button_run.clicked.connect(self.process_images)
        self.button_run.setEnabled(False)
        layout.addWidget(self.button_run)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Status bar con Logo Arc-Team (come in Deeper Cleaner)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        status_widget = QWidget()
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 5, 0)

        status_label = QLabel("Powered by Arc-Team")
        status_layout.addWidget(status_label)

        logo_label = QLabel()
        logo_pixmap = QPixmap('./icons/arc-team_logo.png').scaled(200, 45) # Dimensioni simili al tuo standard
        logo_label.setPixmap(logo_pixmap)
        status_layout.addWidget(logo_label)

        status_widget.setLayout(status_layout)
        self.statusBar.addPermanentWidget(status_widget)

        self.input_dir = None
        self.output_dir = None

    def open_input_dir_dialog(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleziona Cartella Sorgente")
        if directory:
            self.input_dir = directory
            self.label_input.setText(f"Sorgente: ...{directory[-30:]}")
            self.check_ready()

    def open_output_dir_dialog(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleziona Cartella Destinazione")
        if directory:
            self.output_dir = directory
            self.label_output.setText(f"Destinazione: ...{directory[-30:]}")
            self.check_ready()

    def check_ready(self):
        if self.input_dir and self.output_dir:
            self.button_run.setEnabled(True)

    def process_images(self):
        try:
            files = [f for f in os.listdir(self.input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not files:
                QMessageBox.warning(self, "Nessun File", "Nessuna immagine trovata nella cartella selezionata.")
                return

            count = 0
            for filename in files:
                in_path = os.path.join(self.input_dir, filename)
                out_path = os.path.join(self.output_dir, filename)

                img = Image.open(in_path)
                # La magia: salvando senza passare l'argomento 'exif', i dati vengono eliminati
                img.save(out_path, 'JPEG', optimize=True, quality=100)
                count += 1

            QMessageBox.information(self, "Completato", f"Processo terminato con successo!\nImmagini elaborate: {count}")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'elaborazione: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExifEraserApp()
    window.show()
    sys.exit(app.exec_())
