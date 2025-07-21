from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import os

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.cover_added = False

    def header(self):
        if not self.cover_added:
            return
        self.set_fill_color(255, 190, 64) # yellow
        self.set_text_color(12, 41, 77) # blue
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 12, "Solar Calculator Report", ln=True, fill=True)
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def add_cover_page(self):
        self.add_page()
        logo_path = os.path.join(os.path.dirname(__file__), "logo_blue_yellow.png")
        if os.path.exists(logo_path):
            self.set_y(90)
            self.image(logo_path, x=(210 - 100) / 2, w=100)
        self.set_y(160)
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 10, "Solar Energy System Report", ln=True, align="C")
        self.set_font("Helvetica", "", 12)
        self.cell(0, 10, datetime.today().strftime("%B %d, %Y"), ln=True, align="C")
        self.cover_added = True

    def section_title(self, title):
        self.set_fill_color(230, 230, 230)
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, f" {title}", ln=True, fill=True)
        self.ln(2)

    def add_user_info(self, info):
        self.section_title("Client Information")
        self.set_font("Helvetica", size=10)
        self.cell(0, 8, f"Name: {info.get('first_name', '')} {info.get('last_name', '')}", ln=True)
        self.cell(0, 8, f"Email: {info.get('email', '')}", ln=True)
        self.cell(0, 8, f"Phone: {info.get('phone', '')}", ln=True)
        self.cell(0, 8, f"Address: {info.get('address', '')}", ln=True)
        self.cell(0, 8, f"Coordinates: {info.get('latitude', '')}, {info.get('longitude', '')}", ln=True)
        self.ln(5)

    def add_results(self, energy, financial):
        self.section_title("Energy Results")
        self.set_font("Helvetica", size=10)
        for label, value in energy.items():
            self.cell(90, 8, f"{label}", border=0)
            self.set_font("Helvetica", "B", 10)
            self.cell(0, 8, f"{value}", ln=True)
            self.set_font("Helvetica", "", 10)
        self.ln(4)

        self.section_title("Financial & Environmental Metrics")
        for label, value in financial.items():
            self.cell(90, 8, f"{label}", border=0)
            self.set_font("Helvetica", "B", 10)
            self.cell(0, 8, f"{value}", ln=True)
            self.set_font("Helvetica", "", 10)
        self.ln(5)
    
    def add_image(self, image_path, title=""):
        if os.path.exists(image_path):
            if title:
                self.set_font("Helvetica", "B", 12)
                self.cell(0, 10, title, ln=True)
            self.image(image_path, w=180)
            self.ln(10)

    def save_to_buffer(self):
        buffer = BytesIO()
        self.output(buffer)
        buffer.seek(0)
        return buffer
