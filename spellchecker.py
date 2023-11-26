

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
    def __init__(self, known_words):
        <>
    def checker(self, word):
        <>
    def suggestions(self, word):
        <>

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