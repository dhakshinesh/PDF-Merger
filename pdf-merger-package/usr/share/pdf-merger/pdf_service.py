from pathlib import Path
from datetime import datetime
from pypdf import PdfWriter


class PyPDFService:

    def merge_pdfs(self, pdf_paths, output_dir):

        if len(pdf_paths) < 2:
            raise ValueError("At least 2 PDFs are required")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"Merged_{timestamp}.pdf"

        merger = PdfWriter()

        for pdf in pdf_paths:
            merger.append(pdf)

        with open(output_path, "wb") as f:
            merger.write(f)

        merger.close()

        return str(output_path)