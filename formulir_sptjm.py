from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# Function to create PDF form
def create_pdf_form(filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2.0, height - 2 * cm, "FORMULIR DESA")

    # Form fields
    c.setFont("Helvetica", 12)
    
    # Nama
    c.drawString(0* cm, height - 4 * cm, "Nama:")
    c.line(5 * cm, height - 4 * cm, 15 * cm, height - 4 * cm)
    
    # Alamat
    c.drawString(2 * cm, height - 5 * cm, "Alamat:")
    c.line(5 * cm, height - 5 * cm, 15 * cm, height - 5 * cm)
    
    # Tanggal Lahir
    c.drawString(2 * cm, height - 6 * cm, "Tanggal Lahir:")
    c.line(5 * cm, height - 6 * cm, 15 * cm, height - 6 * cm)
    
    # Other form fields can be added similarly
    
    c.save()

# Create the PDF
create_pdf_form("formulir_desa_output.pdf")
