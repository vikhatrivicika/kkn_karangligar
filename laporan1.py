from fpdf import FPDF
import os
from datetime import datetime

def generate_pdf(nama, umur, alamat, info_id):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.cell(200, 10, txt="Informasi Masyarakat", ln=True, align='C')
        pdf.ln(10)
        
        pdf.cell(100, 10, txt=f"Nama: {nama}", ln=True)
        pdf.cell(100, 10, txt=f"Umur: {umur}", ln=True)
        pdf.cell(100, 10, txt=f"Alamat: {alamat}", ln=True)
        pdf.cell(100, 10, txt=f"Info ID: {info_id}", ln=True)
        
        output_dir = 'output_pdfs'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        pdf_filename = f"{nama}_{timestamp}_info.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        pdf.output(pdf_path)
        return pdf_path, timestamp
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None, None
