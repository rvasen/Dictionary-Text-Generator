import sys

from scrape_and_generate import Dictionary_generator

from PyQt5.QtWidgets import (QMainWindow, QWidget, QDesktopWidget, QApplication, QVBoxLayout, QLabel, QGroupBox, 
        QFrame, QComboBox, QLineEdit, QPushButton, QMessageBox, QScrollArea, QSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator, QValidator

# TODO: Handle error in the case that one of the words given does not have any example sentences in dictionary

class MainPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dictionary Text Generator')
 
        screen_rect = QDesktopWidget().availableGeometry(self)
        screen_w, screen_h = screen_rect.width(), screen_rect.height()
        app_w = screen_w * .25
        app_h = screen_h * .75
        self.resize(app_w,app_h)       

        theWidge = MainWidget()
        self.setCentralWidget(theWidge)
        self.statusBar()
        self.show()

    def set_status_message(self,message):
        self.statusBar().showMessage(message)

    def clear_status_message(self):
        self.statusBar().clearMessage()

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.dict_gen = Dictionary_generator('merriam webster', ['noun', 'verb', 'adjective'], 'random')

        self.setWindowTitle('Dictionary Text Generator')

        screen_rect = QDesktopWidget().availableGeometry(self)
        screen_w, screen_h = screen_rect.width(), screen_rect.height()
        app_w = screen_w * .25
        app_h = screen_h * .75
        self.resize(app_w,app_h)

        selectDictionaryLabel = QLabel('Select dictionary to use:')
        selectDictionaryLabel.setAlignment(Qt.AlignTop)
        self.selectDictionaryDropdown = QComboBox()
        self.selectDictionaryDropdown.addItems(Dictionary_generator.dictionaries)

        selectMethodLabel = QLabel('Select method to use:')
        self.selectMethodDropdown = QComboBox()
        self.selectMethodDropdown.addItems(Dictionary_generator.methods)

        originWordLabel = QLabel('Choose origin word(s) (if multiple, use a comma separated list):')
        self.originWord = QLineEdit()
        regexp = QRegExp('^[a-zA-Z]+(,[ ][a-zA-Z]+)*')
        self.validator = QRegExpValidator(regexp)
        self.originWord.setValidator(self.validator)

        numberOfWordsLabel = QLabel('Choose number of words used per output:')
        self.numberOfWords = QSpinBox()
        self.numberOfWords.setMinimum(1)

        numberOfLoopsLabel = QLabel('Choose number of times to loop output:')
        self.numberOfLoops = QSpinBox()
        self.numberOfLoops.setMinimum(1)

        generateButton = QPushButton('Generate text')
        #generateButton.clicked.connect(self.generate_text)
        generateButton.clicked.connect(self.start_generation)

        noteText = QLabel('Note: Parts of speech used are noun, verb, and adjective')

        self.output = QLabel('')
        self.output.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.output.setWordWrap(True)
        self.output.setAlignment(Qt.AlignTop)

        outputScrollArea = QScrollArea()
        outputScrollArea.setWidget(self.output)
        outputScrollArea.setWidgetResizable(True)

        clearTextButton = QPushButton('Clear output')
        clearTextButton.clicked.connect(self.clear_text)

        parametersGroup = QGroupBox('Input Parameters:')
        outputGroup = QGroupBox('Output:')

        parametersLayout = QVBoxLayout()
        outputLayout = QVBoxLayout()

        parametersLayout.addWidget(selectDictionaryLabel)
        parametersLayout.addWidget(self.selectDictionaryDropdown)
        parametersLayout.addWidget(selectMethodLabel)
        parametersLayout.addWidget(self.selectMethodDropdown)
        parametersLayout.addWidget(originWordLabel)
        parametersLayout.addWidget(self.originWord)
        parametersLayout.addWidget(numberOfWordsLabel)
        parametersLayout.addWidget(self.numberOfWords)
        parametersLayout.addWidget(numberOfLoopsLabel)
        parametersLayout.addWidget(self.numberOfLoops)
        parametersLayout.addWidget(generateButton)
        parametersLayout.setAlignment(generateButton, Qt.AlignCenter)
        parametersLayout.addWidget(noteText)

        outputLayout.addWidget(outputScrollArea) 
        outputLayout.addWidget(clearTextButton)
        outputLayout.setAlignment(clearTextButton, Qt.AlignCenter)

        parametersGroup.setLayout(parametersLayout)
        parametersGroup.setMaximumHeight(app_h*.4)
        outputGroup.setLayout(outputLayout)

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(parametersGroup)
        mainLayout.addWidget(outputGroup)

        self.setLayout(mainLayout)

        #self.show()

    '''
    def generate_text(self):
        words = self.originWord.text().split(', ')
        numLoops = self.numberOfLoops.value()
        numWords = self.numberOfWords.value()
        self.dict_gen.dic_name = self.selectDictionaryDropdown.currentText()
        self.dict_gen.method = self.selectMethodDropdown.currentText()
        for _ in range(numLoops):
            for word in words:
                self.dict_gen.text= []
                self.dict_gen.words_used = []
                self.dict_gen.generate_story(numWords, word)
                curText = self.output.text()
                self.output.setText(curText + str(self.dict_gen) + '\n' + str(self.dict_gen.words_used) + '\n')
    '''

    def start_generation(self):
        lineedit_state = self.validator.validate(self.originWord.text(),0)[0]
        if lineedit_state != QValidator.Acceptable:
            message = 'Please make sure your input words are a proper comma separated list.'
            msgbox = QMessageBox()
            msgbox.setText(message)
            msgbox.setWindowTitle('Error')
            msgbox.exec()
            return
        self.words = self.originWord.text().split(', ')
        numLoops = self.numberOfLoops.value()
        numWords = self.numberOfWords.value()
        totalNum = numLoops * len(self.words)
        message = '0 outputs out of ' + str(totalNum) + ' generated'
        self.parent().set_status_message(message)
        self.dict_gen.dic_name = self.selectDictionaryDropdown.currentText()
        self.dict_gen.method = self.selectMethodDropdown.currentText()
        self.generation_thread = OutputText(words = self.words, numWords = numWords, numLoops = numLoops, dict_gen = self.dict_gen)
        self.generation_thread.updateProgress.connect(self.update_generation)
        self.generation_thread.errorEncountered.connect(self.show_error)
        self.generation_thread.start()

    def update_generation(self, outputs_done, text_generated, words_used):
        curNum = outputs_done
        totalNum = self.numberOfLoops.value() * len(self.words)
        message = str(curNum) + ' outputs out of ' + str(totalNum) + ' generated'
        self.parent().set_status_message(message)
        curText = self.output.text()
        self.output.setText(curText + text_generated + '\n' + words_used + '\n')

    # used in case that one of the words given does not have any appropriate example sentences in the dictionary
    def show_error(self, error_word):
        message = 'The word ' + error_word + ' does not have any available example sentences. Please try a different word.'
        msgbox = QMessageBox()
        msgbox.setText(message)
        msgbox.setWindowTitle('Error')
        msgbox.exec()

    def clear_text(self):
        self.output.setText('')
        self.parent().clear_status_message()

class OutputText(QThread):
    updateProgress = pyqtSignal(int, str, str)
    errorEncountered = pyqtSignal(str)
    def __init__(self, words, numLoops, numWords, dict_gen, parent = None):
        super().__init__()
        self.words = words
        self.numLoops = numLoops
        self.numWords = numWords
        self.dict_gen = dict_gen

    def run(self):
        for i in range(self.numLoops):
            for j, word in enumerate(self.words):
                self.dict_gen.text = []
                self.dict_gen.words_used = []
                error_word = self.dict_gen.generate_story(self.numWords, word)
                if not error_word:
                    self.updateProgress.emit(i*len(self.words)+(j+1), str(self.dict_gen), str(self.dict_gen.words_used))
                else:
                    self.errorEncountered.emit(error_word)
                    break

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainPage()
    sys.exit(app.exec_())
