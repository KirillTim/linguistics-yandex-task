# author: Kirill Timofeev
# implementation details and more:
# https://github.com/KirillTim/linguistics-yandex-task/tree/master/Task1
from collections import namedtuple

from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize, pos_tag, download


class Questioner(object):
    VERB_TAGS = ["MD", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
    FORMS_OF_BE = ["IS", "AM", "ARE", "WAS", "WERE", "WILL"]
    FORMS_OF_HAVE = ["HAVE", "HAS", "HAD"]

    Verb = namedtuple("Verb", ["ind", "word", "tag"])

    def __init__(self):
        # not the best solution, but I don't want to implement special
        # exceptions handler to catch `LookupError`, download resources
        # and re-run failed action
        # it should work. if not, please download `wordnet` module manually
        try:
            self.lemmatizer = WordNetLemmatizer()
        except LookupError as err:
            print("Resource 'corpora/wordnet' not found.")
            print("Downloading 'corpora/wordnet'...")
            download("wordnet")
            print("Done.")
            self.lemmatizer = WordNetLemmatizer()  # try again

    def request(self, statement):
        words = Questioner.remove_nt_ending(statement.strip().split())
        marked = self.get_marked_verbs(words)
        if not marked:
            raise Exception("Marked verbs not found")
        words = Questioner.remove_stars(words)
        tags = self.get_tags(" ".join(words))

        def append_tag(verb):
            index, word = verb
            tag = tags[index][1]
            if tag not in self.VERB_TAGS:
                raise Exception(word + " isn't a verb!")
            return Questioner.Verb(index, word, tag)

        marked = list(map(append_tag, marked))

        correct = self.make_question(words, marked)
        correct = Questioner.fix_capital_letters(correct)
        return " ".join(correct) + "?"

    def make_question(self, words, marked):
        if "MD" in list(map(lambda x: x.tag, marked)):
            return self.make_modal(words, marked)
        elif marked[0].word.upper() in self.FORMS_OF_BE:
            return self.make_be(words, marked)
        elif len(marked) == 1:
            return self.make_do(words, marked)
        elif marked[0].word.upper() in self.FORMS_OF_HAVE:
            return self.make_have(words, marked)

    @staticmethod
    def make_modal(words, marked):
        ind, *_ = [x.ind for x in marked if x.tag == "MD"]
        return Questioner.move_word(words, ind)

    @staticmethod
    def make_be(words, marked):
        ind = marked[0].ind
        return Questioner.move_word(words, ind)

    def make_do(self, words, marked):
        def to_infinitive(verb):
            return self.lemmatizer.lemmatize(verb, "v")

        verb = marked[0]
        if verb.tag == "VBD":  # past tense
            do = "Did"
        elif verb.tag == "VBZ":  # present tense, 3rd person singular
            do = "Does"
        else:  # present tense, not 3rd person singular
            do = "Do"

        rv = list(words)
        rv[verb.ind] = to_infinitive(rv[verb.ind])
        return [do] + rv

    @staticmethod
    def make_have(words, marked):
        ind = marked[0].ind
        return Questioner.move_word(words, ind)

    @staticmethod
    def remove_nt_ending(words):
        def remove_nt(word):
            return word[:-4] + "*" if word.endswith("n't*") else word

        return list(map(remove_nt, words))

    @staticmethod
    def remove_stars(words):
        def remove_star(word):
            return word[:-1] if word.endswith("*") else word

        return list(map(remove_star, words))

    @staticmethod
    def move_word(where, old, new=0):
        tmp = list(where)
        w = where[old]
        del tmp[old]
        return tmp[:new] + [w] + tmp[new:]

    @staticmethod
    def get_marked_verbs(words):
        verbs = filter(lambda x: x[1].endswith("*"), enumerate(words))
        return list(map(lambda x: (x[0], x[1][:-1]), verbs))

    @staticmethod
    def get_tags(statement):
        text = word_tokenize(statement)
        return pos_tag(text)

    # will fix capital letters in most cases
    @staticmethod
    def fix_capital_letters(words):
        def all_upper(word):
            return all(c.isupper() for c in word)
        fixed = list(words)
        prev = fixed[1]  # first word in input statement
        cur = fixed[0]  # first word now
        if not prev[0].isupper():  # no need to make upper
            return words
        else:
            if not all_upper(prev):
                fixed[1] = prev[0].lower() + prev[1:]  # so ugly :(
            fixed[0] = cur[0].upper() + cur[1:]
        return fixed


q = Questioner()
# mark all parts of a compound verb
# sentence shouldn't be in UPPER CASE
assert q.request("Somebody couldn't* like programming") == "Could somebody like programming?"
assert q.request("He is* a student") == "Is he a student?"
assert q.request("He is* playing* chess") == "Is he playing chess?"
assert q.request("Everyone likes* programming") == "Does everyone like programming?"
assert (q.request("I like* programming"))
# I can fix capital letters to!
assert q.request("I liked* playing chess") == "Did I like playing chess?"
assert q.request("USSR was* strong") == "Was USSR strong?"
assert q.request("small letters are* OK") == "are small letters OK?"
assert q.request("I went* to school") == "Did I go to school?"
assert q.request("I am* going* to the university") == "Am I going to the university?"
assert q.request("My father isn't* going* to the university") == "Is my father going to the university?"
assert q.request("He had* finished* his job") == "Had he finished his job?"

