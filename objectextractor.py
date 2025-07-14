import sys
import os
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QSlider, QHBoxLayout, QScrollArea,
    QGridLayout, QMessageBox
)
from PyQt6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt
from PIL import Image

class ObjectExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PNG Objektextraktor by S. Macri , 2025")
        self.setAcceptDrops(True)
        self.image = None
        self.processed_objects = []
        self.filename_base = "bild"
        self.is_dark_mode = True

        # Hauptlayout
        layout = QVBoxLayout()

        # Buttonzeile
        btn_layout = QHBoxLayout()
        self.import_btn = QPushButton("PNG importieren")
        self.export_btn = QPushButton("Objekte exportieren")
        self.toggle_theme_btn = QPushButton("🌙 / ☀️")
        self.export_btn.setEnabled(False)
        self.import_btn.clicked.connect(self.load_image)
        self.export_btn.clicked.connect(self.export_objects)
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.toggle_theme_btn)

        # Slider + Label
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(10)
        self.slider.setMaximum(255)
        self.slider.setValue(100)
        self.slider.valueChanged.connect(self.process_image)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #444;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid #aaa;
                width: 14px;
                margin: -6px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #00bcd4;
                border-radius: 3px;
            }
        """)

        # Vorschau mit Grid-Layout
        self.scroll = QScrollArea()
        self.preview_widget = QWidget()
        self.preview_layout = QGridLayout()
        self.preview_widget.setLayout(self.preview_layout)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.preview_widget)

        # Statusmeldung
        self.status_label = QLabel("")

        # Zusammenbauen
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Threshold für Konturenerkennung:"))
        layout.addWidget(self.slider)
        layout.addWidget(QLabel("Vorschau der extrahierten Objekte:"))
        layout.addWidget(self.scroll)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        self.apply_dark_theme()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                self.load_image_from_path(path)
                break

    def toggle_theme(self):
        if self.is_dark_mode:
            self.apply_light_theme()
        else:
            self.apply_dark_theme()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: white;
            }
            QPushButton {
                background-color: #444;
                color: white;
                padding: 5px;
            }
        """)
        self.is_dark_mode = True

    def apply_light_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                color: black;
            }
            QPushButton {
                background-color: #ddd;
                color: black;
                padding: 5px;
            }
        """)
        self.is_dark_mode = False

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "PNG auswählen", "", "PNG-Bilder (*.png)")
        if file_path:
            self.load_image_from_path(file_path)

    def load_image_from_path(self, path):
        self.image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        self.filename_base = os.path.splitext(os.path.basename(path))[0]
        self.process_image()

    def process_image(self):
        self.clear_preview()
        if self.image is None:
            return

        img = self.image.copy()

        if img.shape[2] != 4:
            self.status_label.setText("Fehler: PNG hat keinen Alphakanal.")
            return

        alpha = img[:, :, 3]
        mask = alpha > 0
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        gray = alpha.copy()

        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, self.slider.value(), 255, cv2.THRESH_BINARY)
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=lambda c: (cv2.boundingRect(c)[1] // 100, cv2.boundingRect(c)[0]))

        self.processed_objects.clear()

        for i, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)
            if w < 10 or h < 10:
                continue

            roi = img_rgb[y:y+h, x:x+w]
            alpha_crop = alpha[y:y+h, x:x+w]
            rgba = cv2.merge((roi, alpha_crop))
            self.processed_objects.append(rgba)
            self.add_preview(rgba, i)

        self.export_btn.setEnabled(bool(self.processed_objects))
        self.status_label.setText(f"{len(self.processed_objects)} Objekt(e) extrahiert.")

    def add_preview(self, rgba, index):
        h, w, _ = rgba.shape
        image = QImage(rgba.data, w, h, 4 * w, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(image)
        lbl = QLabel()
        lbl.setPixmap(pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio))
        row = index // 4
        col = index % 4
        self.preview_layout.addWidget(lbl, row, col)

    def clear_preview(self):
        while self.preview_layout.count():
            child = self.preview_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def export_objects(self):
        if not self.processed_objects:
            return
        dir_path = QFileDialog.getExistingDirectory(self, "Exportziel wählen")
        if not dir_path:
            return
        count = 0
        for i, obj in enumerate(self.processed_objects):
            output_path = os.path.join(dir_path, f"{self.filename_base}_objekt_{i+1}.png")
            Image.fromarray(obj).save(output_path)
            count += 1
        self.clear_preview()
        self.processed_objects.clear()
        self.export_btn.setEnabled(False)
        self.status_label.setText(f"{count} Objekt(e) erfolgreich exportiert und Vorschau gelöscht.")
        QMessageBox.information(self, "Export abgeschlossen", f"{count} Objekt(e) wurden gespeichert.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ObjectExtractor()
    win.resize(1000, 700)
    win.show()
    sys.exit(app.exec())
