from pdfreader import PDFDocument, SimplePDFViewer

from .. import PDFContents


class ParserInterface:

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        fd = open(pdf_path, "rb")
        
        doc = PDFDocument(fd)
        self.viewer = SimplePDFViewer(fd)
        self.pages = [p for p in doc.pages()]


    def contains(self, msg: str, page: int) -> bool:
        self.viewer.navigate(page)
        self.viewer.render()
        if msg in self.viewer.canvas.strings:
            return True
        return False


    def process(self, show_progress: bool) -> PDFContents:
        pass
    