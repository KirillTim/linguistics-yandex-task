from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize, pos_tag
from pprint import pprint


class Questioner(object):
    VERB_TAGS = ['MD', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

    def request(self, statement):
        line = statement.strip().upper()
        marked = self.get_marked_verbs(line)
        clean = line.replace('*', '')
        tags = self.get_tags(clean)

        def append_tag(verb):
            if tags[verb[0]][1] not in self.VERB_TAGS:
                raise Exception(verb[1] + " isn't a verb!")
            return verb[0], verb[1], tags[verb[0]][1]
        marked = list(map(append_tag, marked))

        pprint(marked)

        pprint(self.make_question(clean.split(), marked))

    def make_question(self, words, marked):
        if 'MD' in list(map(lambda x: x[2], marked)):
            return self.make_modal(words, marked)

    def make_modal(self, words, marked):
        ind = [x[0] for x in marked if x[2] == 'MD'][0]
        return Questioner.move_word(words, ind)

    @staticmethod
    def move_word(where, old, new=0):
        tmp = list(where)
        w = where[old]
        del tmp[old]
        return tmp[:new]+[w]+tmp[new:]

    def get_marked_verbs(self, statement):
        words = statement.split()
        verbs = filter(lambda x: x[1].endswith('*'), enumerate(words))
        return list(map(lambda x: (x[0], x[1][:-1]), verbs))

    def get_tags(self, statement):
        text = word_tokenize(statement)
        return pos_tag(text)

q = Questioner()
q.request("somebody like* programming")