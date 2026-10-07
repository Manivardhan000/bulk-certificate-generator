from pathlib import Path
from app.services.certificate_service import CertificateService


def test_certificate_generation(tmp_path):
    service = CertificateService(str(tmp_path))
    path = service.generate(
        certificate_id="abc123",
        recipient_name="Abhinav Sai",
        event_name="Python Workshop",
        certificate_title="Certificate of Completion",
    )
    assert Path(path).is_file()
    assert Path(path).stat().st_size > 0
    with open(path, "rb") as pdf:
        data = pdf.read()
    assert data.startswith(b"%PDF")
    assert b"%%EOF" in data
