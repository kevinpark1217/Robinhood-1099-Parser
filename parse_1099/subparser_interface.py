from pdfreader import PDFDocument, SimplePDFViewer
from pdfreader.viewer.canvas import SimpleCanvas
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
        canvas: SimpleCanvas = self.viewer.canvas # type: ignore
        if canvas.strings is not None and msg in canvas.strings:
            return True
        return False


    def process(self, show_progress: bool, contents: PDFContents = PDFContents()) -> PDFContents: # type: ignore
        pass
