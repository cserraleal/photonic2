from fpdf import FPDF
from datetime import datetime
import os

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Solar Calculator Report", ln=True, align="C")
        self.ln(5)

    def add_user_info(self, info):
        self.set_font("Helvetica", size=10)
        self.multi_cell(0, 10,
            f"Name: {info.get('first_name')} {info.get('last_name')}\n"
            f"Email: {info.get('email')}\n"
            f"Phone: {info.get('phone')}\n"
            f"Address: {info.get('address')}\n"
            f"Coordinates: {info.get('latitude')}, {info.get('longitude')}"
        )
        self.ln(5)

    def add_results(self, energy, financial):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "Results", ln=True)
        self.set_font("Helvetica", size=10)
        for label, value in energy.items():
            self.cell(0, 8, f"{label}: {value}", ln=True)
        self.ln(5)
        for label, value in financial.items():
            self.cell(0, 8, f"{label}: {value}", ln=True)
        self.ln(5)

    def add_image(self, image_path, title=""):
        if os.path.exists(image_path):
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 10, title, ln=True)
            self.image(image_path, w=180)
            self.ln(10)

    def save_pdf(self, path):
        self.output(path)
