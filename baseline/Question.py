# -*- coding: utf-8 -*-
class Questioner(object):
    @staticmethod
    def is_aux_verb(word):
        return word.upper() in "AM IS ARE".split()

    def get_question_word(self, word):
        if word != self.get_verb_lemma(word):
            return 'DOES'
        else:
            return 'DO'

    @staticmethod
    def has_es_ending(word):
        return word[-3] in 'AEIOUSYXZ'

    def get_verb_lemma(self, word):
        word = word.upper()
        if word.endswith('ES') and self.has_es_ending(word):
            return word[:-2]
        elif word.endswith('S') and not word.endswith('SS'):
            return word[:-1]
        else:
            return word

    def request(self, statement):
        request = []
        for word in statement.strip().upper().split():
            if word.endswith('*'):
                word = word[:-1]
                if self.is_aux_verb(word):
                    request.insert(0, word)
                else:
                    request.insert(0, self.get_question_word(word))
                    request.append(self.get_verb_lemma(word))
            else:
                request.append(word)
        return ' '.join(request) + '?'

if __name__ == "__main__":
    q = Questioner()
    assert q.request("KATE GOES* TO SCHOOL") == "DOES KATE GO TO SCHOOL?"
    assert q.request("ALEX IS* TALL") == "IS ALEX TALL?"
    assert q.request("WINTER USUALLY COMES* LATE") == "DOES WINTER USUALLY COME LATE?"
    assert q.request("STUDENTS OFTEN COME* LATE") == "DO STUDENTS OFTEN COME LATE?"
    assert q.request("I HAVE* A CAR") == "DO I HAVE A CAR?"
    assert q.request("LIBRARY OF CONGRESS POSSESSES* BOOKS") == "DOES LIBRARY OF CONGRESS POSSESS BOOKS?"
    assert q.request("I MISS* MY DOG") == "DO I MISS MY DOG?"
    assert q.request("THEY FIX* EVERYTHING") == "DO THEY FIX EVERYTHING?"
