
import bs4 #may not have downloaded correctly? (yellow underline)
from bs4 import BeautifulSoup
import PyPDF2
from PyPDF2 import PdfReader

class Spellchecker():
    def __init__(self, reference_file, known_words_file, sim_score_file):
        self.reference_file = reference_file
        self.known_words = self.get_known_words(known_words_file)
        self.unknown_word_count = 0 #remember to print at the end
        self.sim_score = self.get_sim_score(sim_score_file)
    def spell_check(self):
        words_to_check = self.reference_file.parse() #check this phrase
        for word in words_to_check:
            if word not in self.known_words:
                suggestions = Suggester.get_suggestions(word, self.known_words)
                <graphical interface> #work on GUI, but get Levenshtein first
                self.unknown_word_count += 1
    def get_known_words(self, known_words_file):
        with open(known_words_file, "rt") as known_file:
            return set(known_file.read().split())
    def get_sim_score(self, sim_score_file):
        with open(sim_score_file, 'rt') as sim_score_file:
            sim_score = {}
            exec(sim_score_file.read(), {}, sim_score)
        return sim_score


class ReferenceFile():
    def __init__(self, text):
        self.text = text
    def parse(self):
        pass #research implies is good to use, may be redundant (check later)

class Suggester():
    @staticmethod
    def get_suggestions(word, known_words, sim_score): #work on this NEXT!
        suggestions = sorted(known_words, key=lambda known_word:Suggester.levenshtein_distance(
            word, known_word, sim_score))
        return suggestions[:3]
    
    def __init__(self, known_words=None):
        self.known_words = known_words or set()
    def checker(self, word):
        if word in self.known_words:
            return True
        else:
            return False
    def levenshtein_distance(self, word1, word2, sim_score):
        min_edit_dist = range(len(word1)+1)
        index1 = 0
        for letters1 in word1:
            calc_dist = [index1]
            index2 = 0
            for letters2 in word2:
                if letters2 == letters1:
                    calc_dist.append(min_edit_dist[index2])
                else:
                    cost = sim_score.get((letters1,letters2))
                    calc_dist.append(cost+min(min_edit_dist[index2], min_edit_dist[index2+1], 
                                          calc_dist[-1]))
                    if (index1>0) and (index2>0) and (word2[index2] == letters1) and (word2[index2-1] == letters2):
                        calc_dist[-1] = min(calc_dist[-1], min_edit_dist[index2-1]+cost)
                index2 += 1
            min_edit_dist = calc_dist
            index1 += 1
        return min_edit_dist[-1]


class TextFile(ReferenceFile):
    def __init__(self, text):
        super().__init__(text)
    def parse(self):
        return self.text.split()

class HTMLFile(ReferenceFile): #depending on how I want command line, may
    def __init__(self, text):  #have to use a 'with open'
        super().__init__(text)
    def parse(self):
        soup = BeautifulSoup(self.text, "lxml") #may have done wrong, importing
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
sim_scores_file = "similarity_scores.py"
#rest of globals