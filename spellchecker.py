
import bs4
from bs4 import BeautifulSoup
import PyPDF2
from PyPDF2 import PdfReader

class Spellchecker():
    def __init__(self, reference_file, known_words_file):
        self.reference_file = reference_file
        self.known_words = self.get_known_words(known_words_file)
        self.unknown_word_count = 0
    def spell_check(self):
        words_to_check = self.reference_file.get_parsed_content()
        for word in words_to_check:
            if word not in self.known_words:
                <graphical interface>
                self.unknown_word_count += 1
    def get_known_words(self, known_words_file):
        with open(known_words_file, "rt") as known_file:
            return set(known_file.read().split())


class ReferenceFile():
    def __init__(self, text):
        self.text = text
    def parse(self):
        pass

class Suggester():
    def __init__(self, known_words=None):
        self.known_words = known_words or set()
    def checker(self, word):
        if word in self.known_words:
            return True
        else:
            return False
    def suggestions(self, word):
        "<Levenshtein, for later>"

class TextFile(ReferenceFile):
    def __init__(self, text):
        super().__init__(text)
    def parse(self):
        return self.text.split()

class HTMLFile(ReferenceFile):
    def __init__(self, text):
        super().__init__(text)
    def parse(self):
        soup = BeautifulSoup(self.text, "lxml")
        html_content = soup.get_text()
        return html_content.split()

class PDFFile(ReferenceFile):
    def __init__(self, text):
        super().__init__(text)
    def parse(self):
        pdf_reader = PyPDF2.PdfReader(self.text)
        pdf_content = ""
        for num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[num]
            pdf_content += page.extract_text()
        return pdf_content.split()
    
known_words_file = "words.txt"