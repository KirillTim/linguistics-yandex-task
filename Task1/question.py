from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize, pos_tag, download
from pprint import pprint


class Questioner(object):
    VERB_TAGS = ['MD', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    FORMS_OF_BE = ['IS', "AM", "ARE", "WAS", "WERE", "WILL"]
    FORMS_OF_HAVE = ["HAVE", "HAS", "HAD"]

    def __init__(self):
        Questioner.download_modules()

    def request(self, statement):
        words = Questioner.remove_nt_ending(statement.strip().split())
        marked = self.get_marked_verbs(words)
        if not marked:
            raise Exception("Marked verbs not found")
        words = Questioner.remove_stars(words)
        tags = self.get_tags(" ".join(words))
        pprint(tags)

        def append_tag(verb):
            if tags[verb[0]][1] not in self.VERB_TAGS:
                raise Exception(verb[1] + " isn't a verb!")
            return verb[0], verb[1], tags[verb[0]][1]

        marked = list(map(append_tag, marked))

        pprint(marked)

        correct = self.make_question(words, marked)
        pprint(" ".join(correct) + "?")

    def make_question(self, words, marked):
        if 'MD' in list(map(lambda x: x[2], marked)):
            return self.make_modal(words, marked)
        elif marked[0][1].upper() in self.FORMS_OF_BE:
            return self.make_be(words, marked)
        elif len(marked) == 1:
            return self.make_do(words, marked)
        elif marked[0][1].upper() in self.FORMS_OF_HAVE:
            return self.make_have(words, marked)

    def make_modal(self, words, marked):
        ind = [x[0] for x in marked if x[2] == 'MD'][0]
        return Questioner.move_word(words, ind)

    def make_be(self, words, marked):
        ind = marked[0][0]
        return Questioner.move_word(words, ind)

    def make_do(self, words, marked):
        def to_infinitive(verb):
            lemmatizer = WordNetLemmatizer()
            return lemmatizer.lemmatize(verb, "v")

        verb = marked[0]
        if verb[2] == 'VBD':  # past tense
            do = "Did"
        elif verb[2] == 'VBZ':  # present tense, 3rd person singular
            do = "Dose"
        else:  # present tense, not 3rd person singular
            do = "Do"

        rv = list(words)
        rv[verb[0]] = to_infinitive(rv[verb[0]])
        return [do] + rv

    def make_have(self, words, marked):
        ind = marked[0][0]
        return Questioner.move_word(words, ind)

    @staticmethod
    def remove_nt_ending(words):
        def fun(word):
            return word[:-4] + '*' if word.endswith("n't*") else word

        return list(map(fun, words))

    @staticmethod
    def remove_stars(words):
        def fun(word):
            return word[:-1] if word.endswith("*") else word

        return list(map(fun, words))

    @staticmethod
    def move_word(where, old, new=0):
        tmp = list(where)
        w = where[old]
        del tmp[old]
        return tmp[:new] + [w] + tmp[new:]

    def get_marked_verbs(self, words):
        verbs = filter(lambda x: x[1].endswith('*'), enumerate(words))
        return list(map(lambda x: (x[0], x[1][:-1]), verbs))

    def get_tags(self, statement):
        text = word_tokenize(statement)
        return pos_tag(text)

    # not the best solution, but I don't want to implement special exceptions
    # handler to catch `LookupError`, download resources
    # and re-run failed action
    @staticmethod
    def download_modules():
        try:
            lemmatizer = WordNetLemmatizer()
        except LookupError as err:
            print("Resource 'corpora/wordnet' not found.")
            print("Downloading 'corpora/wordnet'...")
            download("wordnet")
            print("Done.")

#TODO: download nltk modules on first start if needed

q = Questioner()
q.request("Somebody couldn't* like programming")
q.request("He is* a student")
q.request("He is* playing* chess")
q.request("Everyone likes* programming")
q.request("I like* programming")
q.request("I liked* playing chess")
q.request("I went* to school")
q.request("I am* going* to the university")
q.request("My father isn't* going* to the university")
q.request("He had* finished* his job")
