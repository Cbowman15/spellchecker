# Spellchecker 2.14.0 README

Spellchecker 2.14.0 (Python-based) is a program designed to be an all-in-one text editor. It identifies and corrects misspelled words in text files. It allows translation of text to various languages. It displays many of the
common features of a normal text editor.

## Prereqs

Before beginning, please make sure that you have the following installed on
your system:
-[Python 3.11](https://www.python.org/downloads/)

## Dependencies

The application requires the use of the following Python libraries:
-'beautifulsoup4': for parsing HTML files
-'PyMuPDF': for parsing PDF files
-'python-docx': for parsing DOCX/Word files
-'regex': for regex operations, within text processing
-'python-Levenshtein': for calculating word similarity
-'fuzzywuzzy': for calculating closest word, by similarity
-'googletrans': for text translation features

As such, below are the installation commands for the libraries:
- pip install beautifulsoup4
- pip install PyMuPDF
- pip install python-docx
- pip install regex
- pip install python-Levenshtein
- pip install fuzzywuzzy
- pip install googletrans==4.0.0-rc1

In addition, the program uses the following Python Standard Library modules:
- 'tkinter': for the graphical interface
- 'time': for function timing
- 'os': for interactions with the operating system
- 'threading': for the management of simultaneous operations

-[INSTALLATION](#installation)
-[USAGE](#usage)
-[CONFIGURATION](#configuration)
-[SUPPORTED FORMATS](#supported-formats)
-[COREDITS](#credits)

## INSTALLATION

To install Spellchecker 2.14.0, do the following:
1. Clone the repository or download the source code for the application
    - bash git https://github.com/Cbowman15/spellchecker.git cd spellchecker
2. Install the above external dependencies, using the given commands.

## USAGE

To use Spellchecker 2.14.0, run the following argument in the command line:
- bash python spellchecker.py

This command initializes the graphical interface, allowing for the instant
ability to access all features. However, it is recommended that the following
is run from the command line, to allow for successful usage of the program:
- bash python spellchecker.py --words <words_file_path> --pd <personal_dictionary_path>
  --ignored <ignored_words_file_path> --ex <example_text_file>

### Arguments
- '--words <known_words_file_path>': specifies the path to your file of known words
- '--pd <personal_dict_file_path>': specifies the path to your personal dictionary file
- '--ignored <ignored_words_file_path>': specifies the path to your file of ignored words
- '--ex <example_text_file>': specifies the path of an example text file for initial startup

### GUI FEATURES
- Open text files for editing and spellchecking
- Recieve and choose between suggestions for correcting misspelled words
- Add words to a personal dictionary
- Ignore words during spell checks
- Navigation between misspelled words with the 'NEXT' and 'PREVIOUS' buttons
- Undo and redo text edits
- Translate highlighted text, via Google Translate
- Save files and perform Save As action
- Keyboard-oriented navigation between misspelled words
- Keyboard command shortcuts
- Optional ability to set as real-time application

#### TEXT EDITING + SPELLCHECKING
Upon highlighting the text, and using the spellchecker file menu option (Ctrl+q), the application performs a spell check on the current contents of the file:
  - Highlights misspelled words
  - Current selected word is highlighted a color different from rest of misspelled words
  - Right-click on a highlighted word shows a menu
    - **Ignore**: skips word for current session
    - **Suggestions**: submenu that lists suggestions for correction of word
    - **Add to Dictionary**: adds word to personal dictionary

#### TRANSLATION FEATURE
The application's translation feature is accessible through the 'TRANSLATE' button. To
access, use Tools menu option or use command Ctrl+t:
 1. Select part of text that is to be translated
 2. Type intended translation language into the entry bar on the bottom of layout
 3. Press 'TRANSLATE' to replace selected text with translation
 4. To close translation feature, press 'CLOSE TRANSLATE'

#### FILE MANAGEMENT
Files can be managed through the 'File' menu option at the top of the application layout:
 - **Open**: Opens file dialog for user to select a file for application use
 - **Save**: Saves changes to currently opened file
 - **Save As**: Opens file dialog for user to save current text to new file

#### KEYBOARD SHORTCUTS
The following keyboard shortcuts are currently available:
 - **Ctrl + o**: Opens a file
 - **Ctrl + s**: Saves current file
 - **Ctrl + s + Shift**: Saves current file as new file
 - **Ctrl + z**: Undo last action
 - **Ctrl + y**: Redo last action
 - **Ctrl + t**: Translate currently selected text
 - **Ctrl + q**: Refresh spell check
 - **Ctrl + c**: Copy currently selected text
 - **Ctrl + v**: Paste currently selected text
 - **Ctrl + a**: Select all file contents

#### ARROW MODE NAVIGATION
Arrow mode turns focus away from manual mouse clicks, toward friendlier, arrow key
presses.

##### ACTIVATING ARROW MODE
To enable:
 - Press the 'Up' arrow key three times, while holding the 'Shift' key. This changes
   the behavior of the arrow keys.

##### USING ARROW MODE
Once active:
 - The 'Left' arrow key will move cursor to previous misspelled word on page
 - The 'Right' arrow key will move cursor to next misspelled word on page
 - Suggestions for currently selected word are displayed in a listbox at the
   bottom center of the application layout (display-only)
 - The 'NEXT', 'PREVIOUS', 'UNDO', and 'REDO' buttons toggle off. A '+DICTIONARY'
   button toggles on.

##### DEACTIVATING ARROW MODE
To disable:
 - Press the 'Down' arrow key three times, while holding the 'Shift' key. The
   behavior of the arrow keys are then returned to normal.
 - The 'NEXT', 'PREVIOUS', 'UNDO', and 'REDO' buttons toggle back on. The '+DICTIONARY'
   button toggles off.

##### BENEFITS OF ARROW MODE
 - Faster workflow for spellchecking
 - Reduced mouse usage

## CONFIGURATION
Here is information to adjust the current program to meet your needs.

### DICTIONARIES SETUP
Below are the dictionaries used for the main application.
 - **Main Dictionary**: Main dictionary file; a list of correctly spelled words; adjust
   by adding or removing entries; 'words.txt'
 - **Personal Dictionary**: A list of words, unique to the user, for which the spellchecker
   ignores; adjust by adding or removing entries; 'personal_dict.txt'
- **Ignored Words**: A list of words, which the user flags as not misspelled (jargon, etc.);
  adjust by adding or removing entries; 'ign_words.txt'

### LANGUAGES SETUP
The application provides a translation feature, which is set by default to English.
The spellchecker words, by default, in English.

### SPELLCHECK PREFERENCE
There is an ability to make the application work in real-time. The open_file_one function
must be edited, slightly; un-comment the refresh function call

## SUPPORTED FORMATS
Spellchecker 2.14.0 provides support for various text-based file formats:
 - Plain-text files (**.txt**): standard, unformatted plain text file
 - Microsoft Word Docs (**.docx**): an XML format document, used by Microsoft Word
 - Hypertext Markup Language (**.html** and **.htm**): files used for webpages, handles HTML tags
 - Portable Document Format (**.pdf**): file type, created by PDF software

 **Note**: spellchecking accuracy may vary, based on complexities of given file

## CREDITS
Spellchecker 2.14.0 was created by:

**Project Lead and Main Developer:**
 - Chance Bowman - [@Cbowman15](https://github.com/Cbowman15)
