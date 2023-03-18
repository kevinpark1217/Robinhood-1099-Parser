from pdfreader import PDFDocument, SimplePDFViewer
from io import BufferedReader

from .pdf_contents import PDFContents

class SubparserInterface:

    def __init__(self, pdf_file: BufferedReader):
        doc = PDFDocument(pdf_file)
        self.viewer = SimplePDFViewer(pdf_file)
        self.pages = [p for p in doc.pages()]

    def contains(self, msg: str, page: int) -> bool:
        self.viewer.navigate(page)
        self.viewer.render()
        if msg in self.viewer.canvas.strings:
            return True
        return False


    def process(self, show_progress: bool, contents: PDFContents = PDFContents()) -> PDFContents:
        pass
