from .parser_interface import ParserInterface

from pdfreader import SimplePDFViewer


class Parser2020(ParserInterface):
    
    def __init__(self, fd):
        self.viewer  = SimplePDFViewer(fd)
    
    def test(self):
        print(self.viewer.metadata)
        for canvas in self.viewer:
            # page_images = canvas.images
            # print(page_images)
            page_text = canvas.text_content
            if 'ABNB 12/24/2020 PUT $152.50' in page_text:
                print(page_text)

