from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from app.core.config import get_settings


class CertificateService:
    def __init__(self, storage_dir: str | None = None) -> None:
        self.storage_dir = Path(storage_dir or get_settings().storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, *, certificate_id: str, recipient_name: str, event_name: str, certificate_title: str) -> str:
        safe_filename = f"{certificate_id}.pdf"
        output_path = self.storage_dir / safe_filename
        page_width, page_height = landscape(A4)

        pdf = canvas.Canvas(str(output_path), pagesize=(page_width, page_height))
        pdf.setTitle(certificate_title)

        # Simple reusable template: intentionally generated in code so the repository has no binary dependency.
        pdf.setStrokeColor(colors.HexColor("#1f4e79"))
        pdf.setLineWidth(4)
        pdf.rect(28, 28, page_width - 56, page_height - 56)
        pdf.setLineWidth(1)
        pdf.rect(42, 42, page_width - 84, page_height - 84)

        pdf.setFillColor(colors.HexColor("#1f4e79"))
        pdf.setFont("Helvetica-Bold", 28)
        pdf.drawCentredString(page_width / 2, page_height - 120, certificate_title.upper())

        pdf.setFillColor(colors.black)
        pdf.setFont("Helvetica", 14)
        pdf.drawCentredString(page_width / 2, page_height - 165, "This certificate is proudly presented to")

        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont("Helvetica-Bold", 30)
        pdf.drawCentredString(page_width / 2, page_height - 220, recipient_name)

        pdf.setFillColor(colors.black)
        pdf.setFont("Helvetica", 15)
        pdf.drawCentredString(page_width / 2, page_height - 265, f"for successful participation in {event_name}")

        pdf.setStrokeColor(colors.HexColor("#9ca3af"))
        pdf.line(page_width / 2 - 160, 105, page_width / 2 + 160, 105)
        pdf.setFillColor(colors.HexColor("#4b5563"))
        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(page_width / 2, 88, f"Certificate ID: {certificate_id}")

        pdf.save()
        return str(output_path)
