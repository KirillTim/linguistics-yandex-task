# -*- coding: utf-8 -*-
class Person(object):
    GND_UNKNOWN = 0
    GND_MASC = 1
    GND_FEMN = 2

    def __init__(self, name, gender=GND_UNKNOWN):
        self.name = name
        self.gender = gender
        self.children = set()
        self.parents = set()
        self.siblings = set()
        self.spouse = None
        #print("new person named " + name + ", gnd = " + str(self.gender))

    def __hash__(self):
        return self.name.__hash__()

    def add_link(self, other, rel_type):
        if rel_type in ['son', 'daughter']:
            self.add_parent(other)
            other.add_child(self)
        elif rel_type in ['father', 'mother']:
            self.add_child(other)
            other.add_parent(self)
        elif rel_type in ['husband', 'wife']:
            self.spouse = other
            other.spouse = self
        elif rel_type in ['brother', 'sister']:
            self.siblings.add(other)
            other.siblings.add(self)
        else:
            raise Exception("Unknown relation type: " + rel_type)

    def add_parent(self, other):
        self.parents.add(other)

    def add_child(self, other):
        self.children.add(other)

    def parent_request(self, gender):
        for parent in self.parents:
            if parent.gender == gender:
                return parent.name

    def child_request(self, gender):
        return ', '.join(self.child_request_helper(gender))

    def child_request_helper(self, gender):
        answer = set()
        for child in self.children:
            #print(child.name)
            if gender == self.__class__.GND_UNKNOWN:
                answer.add(child.name)
            elif child.gender == self.__class__.GND_UNKNOWN:
                answer.add(child.name + "?")
            elif child.gender == gender:
                answer.add(child.name)
        return answer

    def sibling_request(self, gender):
        #print("SR")
        for parent in self.parents:
            ans = parent.child_request_helper(gender)
            #print(ans)
            for name_ in [self.name, self.name + '?']:
                if name_ in ans:
                    ans.remove(name_)
            return ', '.join(ans)

    def spouse_request(self, gender):
        if self.spouse:
            if self.spouse.gender == gender:
                return self.spouse.name


class PedigreeHolder(object):

    DEFAULT_ANSWER = "Don't know"

    def __init__(self):
        self.people = {}

    def add(self, statement):
        who, _, whose, rel = statement.split()
        assert whose.endswith('\'s')
        self.add_relative(who, whose[:-2], rel)

    def request(self, question):
        req_parts = question.split()
        if req_parts[0] == 'Is' and req_parts[2] == 'a':
            return self.gender_request(req_parts[1], req_parts[3][:-1])
        elif tuple(req_parts[0:2]) == ('Who', 'is') and req_parts[2].endswith('\'s'):
            return self.relative_request(req_parts[2][:-2], req_parts[3][:-1])
        else:
            raise Exception("Unknown request type")

    def add_relative(self, who_name, whose_name, rel_type):
        who_gender, whose_gender = self.get_genders_by_reltype(rel_type)
        if who_name not in self.people:
            self.people[who_name] = Person(who_name, who_gender)
        if whose_name not in self.people:
            self.people[whose_name] = Person(whose_name, whose_gender)
        self.people[who_name].add_link(self.people[whose_name], rel_type)
        self.check_relatives()

    def check_relatives(self):
        """ Make sure all spouses share children
        and all siblings share parents
        """
        for name in self.people:
            person = self.people[name]
            if person.spouse:
                person.children.update(person.spouse.children)
                for child in person.children:
                    child.parents.add(person.spouse)
            for sibling in person.siblings:
                person.parents.update(sibling.parents)
                for parent in person.parents:
                    parent.children.add(sibling)
                sibling.parents.update(person.parents)
                for parent in sibling.parents:
                    parent.children.add(person)

    def relative_request(self, name, rel_type):
        try:
            person = self.people[name]
            gender, _ = self.get_genders_by_reltype(rel_type)
            if rel_type in ['father', 'mother']:
                return person.parent_request(gender) or self.__class__.DEFAULT_ANSWER
            if rel_type in ['child', 'son', 'daughter']:
                return person.child_request(gender) or self.__class__.DEFAULT_ANSWER
            if rel_type in ['husband', 'wife']:
                return person.spouse_request(gender) or self.__class__.DEFAULT_ANSWER
            if rel_type in ['brother', 'sister']:
                return person.sibling_request(gender) or self.__class__.DEFAULT_ANSWER
        except KeyError:
            return self.__class__.DEFAULT_ANSWER

    def gender_request(self, name, gender_word):
        if name not in self.people:
            return self.__class__.DEFAULT_ANSWER

        gender = self.people[name].gender
        if gender == Person.GND_UNKNOWN:
            return self.__class__.DEFAULT_ANSWER

        if gender_word == 'man':
            asked_gender = Person.GND_MASC
        else:
            asked_gender = Person.GND_FEMN

        if gender == asked_gender:
            return "Yes"
        else:
            return "No"

    @staticmethod
    def get_genders_by_reltype(rel_type):
        if rel_type == 'husband':
            return Person.GND_MASC, Person.GND_FEMN
        if rel_type == 'wife':
            return Person.GND_FEMN, Person.GND_MASC
        if rel_type in ['mother', 'daughter', 'sister', 'grandmother', 'granddaughter']:
            return Person.GND_FEMN, Person.GND_UNKNOWN
        if rel_type in ['father', 'son', 'brother', 'grandson', 'grandfather']:
            return Person.GND_MASC, Person.GND_UNKNOWN
        return Person.GND_UNKNOWN, Person.GND_UNKNOWN


if __name__ == "__main__":
    ph = PedigreeHolder()
    ph.add("Carol is Ann's daughter")
    ph.add("Ann is Brett's wife")
    ph.add("Darren is Brett's son")
    ph.add("Brett is Darren's father")
    ph.add("Carol is Frank's sister")
    ph.add("Emily is Carol's daughter")
    assert ph.request("Is Carol a woman?") == "Yes"
    assert ph.request("Is Frank a man?") == "Don't know"
    assert ph.request("Is Brett a woman?") == "No"
    assert ph.request("Who is Rose's father?") == "Don't know"
    assert ph.request("Who is Brett's father?") == "Don't know"
    assert ph.request("Who is Ann's husband?") == "Brett"
    assert ph.request("Who is Carol's father?") == "Brett"
    assert ph.request("Who is Emily's father?") == "Don't know"
    assert ph.request("Who is Carol's daughter?") == "Emily"

    assert set(ph.request("Who is Brett's son?").split(", ")) == {"Darren", "Frank?"}
    assert set(ph.request("Who is Ann's child?").split(", ")) == {"Carol", "Darren", "Frank"}

    assert set(ph.request("Who is Darren's sister?").split(", ")) == {"Carol", "Frank?"}
    assert ph.request("Who is Frank's brother?") == "Darren"
    assert ph.request("Who is Darren's brother?") == "Frank?"
    #assert ph.request("Who is Emily's grandfather?") == "Brett"
    #assert ph.request("Who is Ann's grandson?") == "Don't know"
    #assert ph.request("Who is Ann's grandchild?") == "Emily"