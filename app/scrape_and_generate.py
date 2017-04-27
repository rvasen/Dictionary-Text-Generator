import random, string

from utils import get_soup_object

# TODO: Fix the fact that this can't handle elipsises or quotes with the em dash particularly well

class Dictionary_generator:

    dictionaries = ['merriam-webster']
    methods = ['random']

    def __init__(self, dic_name, acceptable_parts_of_speech, method, init_text=None):
        # init_text is a string of at least one sentence where sentences are defined by periods. must end with a period. dic_name is name of dictionary.
        # acceptable_parts_of_speech is a list of strings of parts of speech with all lowercase starting letters
        self.dic_name = dic_name
        self.acceptable_PoS = acceptable_parts_of_speech
        self.method = method
        if not init_text:
            self.text = []
            self.words_used = []
            return
        if not isinstance(init_text, str):
            raise TypeError('initial text must be a string')
        if not init_text[-1] == '.':
            raise ValueError('initial text must end with a period')
        text = init_text.split('.')[:-1] # split but don't include last element which should be empty string given that the text ends with a period
        for i in range(0,len(text)): # add periods back
            text[i] = text[i] + '.'
        self.text = text
        self.words_used = [None] * len(self.text)
        #self.accepted_dic_names = ['merriam webster']

    def __str__(self):
        formatted_output = ''
        for sentence in self.text:
            if sentence[0] == ',':
                formatted_output = formatted_output[:-1]
                formatted_output = formatted_output + sentence
            else:
                formatted_output = formatted_output + ' ' + sentence
        return formatted_output

    def generate_story(self, num_sentences, next_word = None, prev_word = None):
        # acceptable_parts_of_speech is a list of strings of parts of speech with all lowercase starting letters
        '''
        if not isinstance(dic_name, str):
            raise TypeError('dictionary name must be a string')
        '''
        if num_sentences == '':
            raise ValueError('Must specify number of words')
        if not isinstance(num_sentences, int) or num_sentences < 0:
            raise ValueError('Number of sentences must be nonnegative integer')
        if not next_word and not self.text:
            raise ValueError('Must specify initial word if you havent generated or given any text')
        '''
        if dic_name not in accepted_dic_names:
            raise ValueError('dictionary name must be an accepted dictionary name')
        '''
        if num_sentences == 0:
            return
        if not prev_word:
            prev_word = next_word
        if not next_word:
            # choose last sentence from text, remove whitespace from before sentence, remove punctuation, split into list of words, remove last word used, 
            # and choose another word and a sentence with that word
            table = str.maketrans({key: None for key in string.punctuation})
            last_sentence_words = self.text[-1].lstrip().translate(table).split(' ')
            for word in last_sentence_words:
                if prev_word.lower() in word.lower() or word.lower() in prev_word.lower(): # made lower case to be case sensitive
                    last_sentence_words.remove(word)
            next_word, next_sentence = self.__choose_word_and_sentence(last_sentence_words)  
            if not next_word:
                '''
                print(self)
                print(self.words_used)
                raise ValueError('Last sentence in text contains no valid words based on acceptable parts of speech and dictionary used (or just no example sentences')
                '''
                num_sentences = num_sentences + len(self.words_used)
                next_word = self.words_used[0] # need to fix later; won't work if adding sentences
                self.text = []
                self.words_used = []
                next_sentence = self.__check_word(next_word)
        else:
            next_sentence = self.__check_word(next_word)
            if not next_sentence:
                return next_word 
                #raise ValueError('Word given is not valid based on acceptable parts of speech and dictionary used (or may just not have any example sentences)')
        self.text.append(next_sentence)
        self.words_used.append(next_word)
        num_sentences -= 1
        self.generate_story(num_sentences, None, next_word)

    def __choose_word_and_sentence(self,sentence):
        if not sentence:
            return (None,None)
        if self.method == 'random':
            candidate_word = random.choice(sentence)
        next_sentence = self.__check_word(candidate_word)
        if not next_sentence:
            sentence.remove(candidate_word)
            return self.__choose_word_and_sentence(sentence)
        else:
            return (candidate_word, next_sentence)

    def __check_word(self, word):
        # returns False if word is not valid (not in dictionary, not acceptable part of speech) and returns sentence associated with word if it is
        if self.dic_name == 'merriam-webster':
            if word.lower() == 'i' or word.lower() == 'a' or word.lower() == 'she': # manually remove 'a' and 'i' and 'she'
                return False
            soup = get_soup_object('http://www.merriam-webster.com/dictionary/{0}'.format(word))
            if soup.title.string == 'Result Not Found':
                return False
            all_part_of_speech_tags = list(soup.find_all('span',class_='main-attr'))
            sentences_list = []
            for tag in all_part_of_speech_tags:
                for part_of_speech in tag.stripped_strings:
                    if part_of_speech in self.acceptable_PoS:
                        parent = tag.find_parent('div', class_='card-box')
                        #print(parent)
                        sibling = parent.find_next_sibling('div', class_='modules clearfix')
                        #print(sibling)
                        #print(sibling.encode('utf-8'))
                        if sibling == None:
                            break
                        sentences = sibling.find_all('p', class_='definition-inner-item')
                        #print(sentences)
                        for sentence in sentences:
                            if sentence != None:
                                sentence_text = sentence.get_text()
                                sentence_text.translate({0x2014: '&'})
                                if sentence_text[0] == '<' and sentence_text[-1] == '>':
                                    l = list(sentence_text)
                                    l[0] = ''
                                    l[-1] = '.'
                                    l[1] = l[1].upper()
                                    sentence_text = ''.join(l)
                                elif not sentence_text[0].isupper() and sentence_text[-1] != '.':
                                    if not self.text or self.text[-1][-1] != '.':
                                        break
                                    l = list(sentence_text)
                                    l = [',', ' '] + l + ['.']
                                    sentence_text = ''.join(l)
                                if not (sentence_text[-1].isdigit() or sentence_text[-2].isdigit()): # workaround since i cant find em dashes in quotes; fix later
                                    sentences_list.append(sentence_text)
        #print(sentences_list)
        if not sentences_list:
            return False
        else:
            return random.choice(sentences_list)

if __name__ == '__main__':
    for i in range(0,10):
        test1 = Dictionary_generator('merriam-webster', ['noun', 'verb', 'adjective'], 'random')
        test2 = Dictionary_generator('merriam-webster', ['noun', 'verb', 'adjective'], 'random')
        test3 = Dictionary_generator('merriam-webster', ['noun', 'verb', 'adjective'], 'random')
        #test4 = Dictionary_generator('merriam-webster', ['noun', 'verb', 'adjective'])
        test1.generate_story(15, 'rape')
        print(test1)
        print(test1.words_used)
        test2.generate_story(15, 'loot')
        print(test2)
        print(test2.words_used)
        test3.generate_story(15, 'pillage')
        print(test3)
        print(test3.words_used)
        '''
        test4.generate_story(10, 'man')
        print(test4)
        print(test4.words_used)
    acceptable_PoS = ['noun', 'verb', 'adjective']
    soup = get_soup_object('http://www.merriam-webster.com/dictionary/mean')
    all_part_of_speech_tags = list(soup.find_all('span',class_='main-attr'))
    parts_of_speech = []
    count = 1
    good_part_of_speech_tags = []
    sentences_list = []
    for tag in all_part_of_speech_tags:
        count += 1
        for part_of_speech in tag.stripped_strings:
            if part_of_speech in acceptable_PoS: # add self here when transfering over
                good_part_of_speech_tags.append(tag)
                parent = tag.find_parent('div', class_='card-box')
                sibling = parent.find_next_sibling('div', class_='clearfix')
                #print(sibling.encode('utf-8'))
                sentences = sibling.find_all('p', class_='definition-inner-item')
                for sentence in sentences:
                    if sentence != None:
                        sentence_text = sentence.get_text()
                        sentence_text.translate({0x2014: '&'})
                        if sentence_text[0] == '<' and sentence_text[-1] == '>':
                            l = list(sentence_text)
                            l[0] = ''
                            l[-1] = '.'
                            l[1] = l[1].upper()
                            sentence_text = ''.join(l)
                        elif not sentence_text[0].isupper() and sentence_text[-1] != '.':
                            l = list(sentence_text)
                            l = [',', ' '] + l + ['.']
                            sentence_text = ''.join(l)
                        if not (sentence_text[-1].isdigit() or sentence_text[-2].isdigit()): # workaround since i can't find em dashes in quotes; fix later
                            sentences_list.append(sentence_text)
                        #elif index != -1:
                        #    sentence_text = sentence_text[0:index]
    print(sentences_list)
    '''
