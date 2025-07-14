# 🖼️ PNG Object Extractor

A simple desktop application to extract individual objects from a PNG image using alpha transparency and contour detection. Built with **PyQt6**, **OpenCV**, and **Pillow**.

---

## ✨ Features

- ✅ Drag-and-drop PNG import or file selection
- 🎛️ Adjustable threshold for contour detection
- 🔍 Scrollable preview grid of extracted objects
- 💾 Export extracted objects as individual PNG files (with alpha)
- 🌙/☀️ Dark and light theme toggle
- 📁 Automatic filename generation and sorting

---

## 📷 Use Case

This tool is ideal for:

- Game developers extracting sprites or UI elements
- Artists exporting assets from hand-drawn sheets
- Designers separating transparent objects from a composition

---

## 🚀 Installation

### Requirements

- Python 3.8+
- pip

### Install dependencies

```bash
pip install -r requirements.txt
```
 Usage

python object_extractor.py

    Click "PNG importieren" or drag a PNG file into the window.

    Adjust the threshold slider to fine-tune contour detection.

    Preview the extracted objects.

    Click "Objekte exportieren" to save them as individual PNGs.

    Toggle between dark/light mode using the 🌙 / ☀️ button.

📦 Output

    Exported files are saved as:
    original_filename_objekt_1.png, original_filename_objekt_2.png, etc.

🎯 Design Focus

    The extractor only supports PNG images with an alpha channel.

    This is a deliberate design choice to ensure precise and reliable object extraction based on transparency.

    Other formats like JPEG are not supported, as they lack alpha channel data and would lead to inaccurate results.

📃 License

MIT License © 2025 S. Macri


