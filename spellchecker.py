
import bs4 #may not have downloaded correctly? (yellow underline)
from bs4 import BeautifulSoup
import PyPDF2
from PyPDF2 import PdfReader
import tkinter as tk
import Levenshtein
import re
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
                suggestions = Suggester.get_suggestions(word, self.known_words, self.sim_score)
                self.unknown_word_count += 1
    def get_known_words(self, known_words_file):
        with open(known_words_file, "rt") as known_file:
            return set(known_file.read().split())
    def get_sim_score(self, sim_score_file):
        with open(sim_score_file, 'rt') as sim_score_file:
            sim_score = {}
            exec(sim_score_file.read(), {}, sim_score)
            print("sim_score:", sim_score)
        return sim_score


class ReferenceFile():
    def __init__(self, text):
        self.text = text
    def parse(self):
        pass #research implies is good to use, may be redundant (check later)

class Suggester():
    @staticmethod
    def get_suggestions(word, known_words, sim_score): #work on this NEXT!
        suggestions = sorted(known_words, key=lambda known_word:Levenshtein.distance(word, known_word))
        return suggestions[:3]
    
    def __init__(self, known_words=None):
        self.known_words = known_words or set()
    def checker(self, word):
        if word in self.known_words:
            return True
        else:
            return False
    @staticmethod
    def levenshtein_distance(word1, word2, sim_score):
        min_edit_dist = list(range(len(word1)+1))
        for index1, letters1 in enumerate(word1,1):
            calc_dist = [index1]
            for index2, letters2 in enumerate(word2, 1):
                print("letters1: {}, letters2: {}".format(letters1, letters2))
                cost = sim_score.get((letters1, letters2), 0)
                print("Cost: {}".format(cost))
                if letters2 == letters1:
                    calc_dist.append(min_edit_dist[index2-1])
                else:
                    calc_dist.append(cost+min(min_edit_dist[index2], min_edit_dist[index2-1], calc_dist[-1]))
                    if (index1>0) and (index2>0) and (word2[index2-1]==letters1) and (word2[index2]==letters2):
                        calc_dist[-1]=min(calc_dist[-1], min_edit_dist[index2-1]+cost)
            min_edit_dist = calc_dist
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

class SpellcheckerApp:
    def __init__(self, window, spellchecker):
        self.window = window
        self.window.title("Spellchecker EECE2140")
        self.frm = tk.Frame(self.window)
        self.frm.pack()
        self.text = tk.Text(self.frm, wrap="word", width=80, height=30)
        self.text.pack(expand=True, fill='both', padx=30, pady=15)

        with open("example.txt", 'rt') as example_text_file:
            text_content = example_text_file.read()
            

        text_content = ' ' + text_content
        self.text.insert(tk.END, text_content)
        self.unknown_words = []
        self.current_unknown_index = 0
        self.btn_next_unknown = tk.Button(self.frm, text="NEXT UNKNOWN", command=self.next_unknown)
        self.btn_next_unknown.pack()
        self.spellchecker = spellchecker
        self.text.tag_config("highlight", background="yellow")
        self.text.tag_config("selected", background="blue")
        self.text.bind("<Button-3>", self.show_menu)
        self.text.bind("<ButtonRelease-3>", self.show_menu)
        self.text.tag_bind("highlight", "<Button-3>", self.show_menu)
        self.text.tag_bind("selected", "<ButtonRelease-3>", self.show_menu)
        spellchecker.spell_check()
        self.highlight_unknown()

    def show_menu(self, event):
        curr_index = self.text.index(tk.CURRENT)
        word = self.text.get(curr_index+" wordstart", curr_index+" wordend")
        self.text.tag_remove("selected", "1.0", tk.END)
        if "highlight" in self.text.tag_names(curr_index):
            self.text.tag_add("selected", curr_index+" wordstart", curr_index+" wordend")
            self.text.tag_config("selected", background="blue")
            if word in self.unknown_words:
                self.text.tag_remove("highlight", curr_index+" wordstart", curr_index+" wordend")
                if self.text.tag_ranges("highlight") and (curr_index in self.text.tag_ranges("highlight")):
                    self.text.tag_configure("selected", background="blue")
                    self.text.tag_add("selected", curr_index+" wordstart", curr_index+" wordend")
                    menu = tk.Menu(self.text, tearoff=1)
                    menu.add_command(label="Ignore", command=self.ignore_unknown)
                    menu.add_command(label="Get Suggestion", command=self.accept_suggestion)
                    menu.add_command(label="Delete", command=self.delete_unknown)
                    menu.post(event.x_root, event.y_root)

    def next_unknown(self):
        if self.unknown_words:
            if self.current_unknown_index < (len(self.unknown_words)-1):
                self.current_unknown_index += 1
            else:
                self.current_unknown_index = 0
            self.highlight_unknown()

    def highlight_unknown(self):
        def remove_punct(word):
            return word.rstrip('.?!:\n ') in self.spellchecker.known_words and word.lstrip('.?!:\n ') in self.spellchecker.known_words
        start_text = "1.0"
        end_text = tk.END
        self.text.tag_remove("highlight", start_text, end_text)
        for line_num in range(1, int(self.text.index(tk.END).split('.')[0])+1):
            line_start= "{}.0".format(line_num)
            line_end= "{}.end".format(line_num)
            line_text = self.text.get(line_start, line_end)
            for word in re.findall(r'\b\w+[.?!:]?\b', line_text):
                if not remove_punct(word):
                    start_pos = self.text.search(r'\y{}\y'.format(word), line_start, line_end, regexp=True)
                    while start_pos:
                        end_pos = self.text.index('{}+{}c'.format(start_pos, len(word)))
                        self.text.tag_add("highlight", start_pos, end_pos)
                        start_pos=self.text.search('r\y{}\y'.format(word), end_pos, line_end, regexp=True)
        self.text.tag_config("highlight", background="yellow")
    def ignore_unknown(self):
        unknown_word = self.unknown_words[self.current_unknown_index]
        self.unknown_words.remove(unknown_word)
        self.unknown_word_count -= 1
        self.next_unknown()
    
    def accept_suggestion(self):
        if self.unknown_words:
            unknown_word = self.unknown_words[self.current_unknown_index]
            suggestions = Suggester.get_suggestions(unknown_word, self.spellchecker.known_words,
                                                    self.spellchecker.sim_score)
            if suggestions:
                self.suggestion_menu(unknown_word, suggestions)
    
    def suggestion_menu(self, unknown_word, suggestions):
        menu = tk.Menu(self.text, tearoff=0)
        for suggestion in suggestions[:3]:
            menu.add_command(label=suggestion, command=self.get_a_suggestion(unknown_word, suggestion))
        menu.post(self.text.winfo_pointerx(), self.text.winfo_pointery()) #will need to check on this--not sure about it
    
    def get_a_suggestion(self, unknown_word, suggestion):
        return lambda: self.replace_unknown(unknown_word, suggestion)
    def replace_unknown(self, unknown_word, suggestion):
        start_text = "1.0"
        end_text = tk.END
        start_text = self.text.search(r'\y{}\y'.format(unknown_word), start_text, end_text, regexp=True)
        while start_text:
            end_text = self.text.index('{}+{}c'.format(start_text, len(unknown_word))) #have REALLY got to check on this (come back when debugging)
            self.text.delete(start_text, end_text)
            self.text.insert(start_text, suggestion)
            start_text = self.text.search(r'\y{}\y'.format(unknown_word), end_text, end_text, regexp=True)
        self.unknown_words[self.current_unknown_index] = suggestion
        
    def delete_unknown(self):
        unknown_word = self.unknown_words[self.current_unknown_index]
        self.text.delete("insert-1c wordstart", "insert")
        self.text.insert("insert", "<REPLACE>")
        self.unknown_word_count -= 1
        self.next_unknown()

with open("example.txt", 'rt') as example_text_file:
    text_content = example_text_file.read()

reference_file = TextFile(text_content)
known_words_file = "words.txt"
sim_scores_file = "similarity_scores.py"
window = tk.Tk()
spellchecker = Spellchecker(reference_file,known_words_file,sim_scores_file)
app = SpellcheckerApp(window, spellchecker)
window.mainloop()
#rest of globals