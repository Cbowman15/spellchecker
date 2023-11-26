

class Spellchecker():
    def __init__(self):
        <>
    def spell_check(self, ReferenceFile):
        <>

class ReferenceFile():
    def __init__(self, text):
        self.text = text
    def parse(self):
        <>

class Suggester():
    def __init__(self, known_words=None):
        self.known_words = known_words or {}
    def checker(self, word):
        if word is self.known_words:
            return True
        else:
            return False
    def suggestions(self, word):
        "<Levenshtein, for later>"

class TextFile(ReferenceFile):
    def __init__(self, text):
        super().__init__(text)
    def parse(self):
        <whatever method>

class HTMLFile(ReferenceFile):
    def __init__(self, text):
        super().__init__(text)
    def parse(self):
        <BeautifulSoup>

class PDFFile(ReferenceFile):
    def __init__(self, text):
        super().__init__(text)
    def parse(self):
        <PyPDF2>