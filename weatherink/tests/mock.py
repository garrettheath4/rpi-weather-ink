class InkyPHAT:
    WIDTH = 212
    HEIGHT = 104
    BLACK = 1
    RED = 1
    YELLOW = 2

    def __init__(self, color):
        self.color = color
        self.border = None
        self.rotation = None
        self.image = None

    def set_border(self, color):
        self.border = color

    def set_rotation(self, degrees):
        self.rotation = degrees

    def set_image(self, image):
        self.image = image

    @staticmethod
    def show():
        print("Warning: InkyPhat().show() is mocked/fake")
        pass


class BeautifulSoup:
    def __init__(self, html_content, library):
        self.htmlContent = html_content
        self.library = library

    def find(self, tag=None, attribute=None, **kwargs):
        print("Warning: BeautifulSoup().find() is mocked/fake")
        pass

