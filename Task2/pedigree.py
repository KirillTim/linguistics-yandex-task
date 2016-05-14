# there are only to genders and families are traditional for this task
# husband and farther are males and wife and mother are females
# it's not about tolerance - it's about system rules
# how to determine who are the Wachowskis without these rules?


class Gender(object):
    UNKNOWN, MALE, FEMALE = range(3)

    @staticmethod
    def opposite(gender):
        if gender == Gender.MALE:
            return Gender.FEMALE
        elif gender == Gender.FEMALE:
            return Gender.MALE
        else:
            return Gender.UNKNOWN

    @staticmethod
    def by_relation(relation):
        if relation in [Relation.HUSBAND, Relation.FATHER, Relation.SON,
                        Relation.BROTHER]:
            return Gender.MALE
        elif relation in [Relation.WIFE, Relation.MOTHER, Relation.DAUGHTER,
                          Relation.SISTER]:
            return Gender.FEMALE
        else:
            return Gender.UNKNOWN


# little more OOP to improve extensibility
class Relation(object):
    HUSBAND, WIFE, FATHER, MOTHER, SON, DAUGHTER, \
        SISTER, BROTHER, CHILD = range(9)
    names = ["husband", "wife", "father", "mother", "son", "daughter",
             "sister", "brother", "child"]

    @staticmethod
    def by_name(name):
        return Relation.names.index(name)


class Person(object):
    def __init__(self, name, gender=Gender.UNKNOWN,
                 parents=None, children=None, siblings=None, spouse=None):
        self.name = name
        self.gender = gender
        self.parents = list(parents or [])
        self.children = list(children or [])
        self.siblings = list(siblings or [self])
        self.spouse = spouse

    def __hash__(self):
        return hash(self.name) ^ hash(self.gender)

    def __eq__(self, other):
        if not isinstance(other, Person):
            return False
        return self.name == other.name and self.gender == other.gender

    def __lt__(self, other):
        return hash(self) < hash(other)

    def add_parent(self, parent):
        def try_to_set_gender(old, new):
            if old.name == new.name:
                if old.gender == Gender.UNKNOWN:
                    old.gender = new.gender
                    return True
                if new.gender == Gender.UNKNOWN:
                    return True
            return False

        if not self.parents:
            self.parents.append(parent)
        elif parent in self.parents:
            pass
        elif parent.name not in [p.name for p in self.parents] \
                and len(self.parents) == 2:
            raise Exception(self.name + " already have two parents")
        elif parent.gender != Gender.UNKNOWN \
                and parent.gender in [p.gender for p in self.parents]:
            raise Exception(self.name + " can't have two parents "
                                        "with the same gender")

        elif len(self.parents) == 1:
            if not try_to_set_gender(self.parents[0], parent):
                self.parents.append(parent)
        elif len(self.parents) == 2:
            if not (try_to_set_gender(self.parents[0], parent) or
                    try_to_set_gender(self.parents[1], parent)):
                raise Exception("Bad parent "+parent.name+" for "+self.name)

        if len(self.parents) == 2:
            Person.try_fix_genders(self.parents)
        children = Person.merge(self.siblings, parent.children)
        for ch in children:
            ch.parents = self.parents
            ch.siblings = children
        if len(self.parents) == 2:
            for i in [0, 1]:
                self.parents[i].spouse = self.parents[1-i]
                self.parents[i].children = children
        else:
            self.parents[0].children = children

    def add_child(self, child):
        child.add_parent(self)  # lol

    def add_sibling(self, sibling):
        if sibling.parents:
            for i in sibling.parent:
                self.add_parent(i)
        else:
            sibling.parents = self.parents
        Person.merge(self.siblings, sibling.siblings)
        for s in sibling.siblings:
            s.siblings = self.siblings

    def add_spouse(self, spouse):
        if not self.spouse:
            self.spouse = spouse
        elif spouse.name != self.spouse.name:
            raise Exception(self.name + " Already have a spouse")
        elif spouse.gender != Gender.UNKNOWN and spouse.gender == self.gender:
            raise Exception(self.name+" Cant have spouse with the same gender")
        Person.try_fix_genders([self, self.spouse])
        spouse.spouse = self
        Person.merge(self.children, spouse.children)
        spouse.children = self.children
        for ch in self.children:
            ch.parents = [self, spouse]

    @staticmethod
    def try_fix_genders(parents):
        if len(parents) < 2:
            return
        for i in [0, 1]:
            if parents[i].gender != Gender.UNKNOWN:
                if parents[1-i].gender == parents[i].gender:
                    raise Exception("can't have two parents with the same gender")
                else:
                    parents[1-i].gender = Gender.opposite(parents[i].gender)
                    break

    def find_all(self, what):
        def person_eq(this, that):
            return this.name == that.name and \
                   this.gender in [that.gender, Gender.UNKNOWN]
        rv = []
        if person_eq(self, what):
            rv.append(self)
        for data in [self.siblings, self.children, [self.spouse]]:
            if not data:
                continue
            for i in data:
                if not i:
                    continue
                rv += i.find_all(what)
        return rv

    # we can have only two children/siblings with the same name,
    # they should have different genders, though
    @staticmethod
    def merge(list1, list2):
        for i in list2:
            ins = True
            for j in list1:
                if i.name == j.name and (j.gender == Gender.UNKNOWN or
                                         j.gender == i.gender):
                    j.gender = i.gender
                    ins = False
                    break
            if ins:
                list1.append(i)
        return list1

    def comp_gender(self, gender):
        if gender == Gender.UNKNOWN:
            return True
        if gender == self.gender:
            return True
        if self.gender == Gender.UNKNOWN:
            return True
        return False


class PedigreeHolder(object):
    DONT_KNOW = "Don't know"

    def __init__(self):
        self.people = {}

    def add(self, statement):
        who_name, _is, whose_name, rel = statement.split()
        if _is != "is" or not whose_name.endswith('\'s'):
            raise Exception("Wrong input statement: " + statement)
        whose_name = whose_name[:-2]
        who_gender = Gender.by_relation(Relation.by_name(rel))
        who = Person(who_name, who_gender)
        if who_name in self.people:
            who = self.people[who_name]
            if who.gender == Gender.UNKNOWN:
                who.gender = who_gender
        else:
            self.people[who_name] = who

        whose = Person(whose_name)
        if whose_name in self.people:
            whose = self.people[whose_name]
        else:
            self.people[whose_name] = whose

        PedigreeHolder.__add_relation(who, whose, Relation.by_name(rel))

    @staticmethod
    def __add_relation(who, whose, relation):
        if relation in [Relation.MOTHER, Relation.FATHER]:
            who.add_child(whose)
        elif relation in [Relation.SON, Relation.DAUGHTER, Relation.CHILD]:
            who.add_parent(whose)
        elif relation in [Relation.WIFE, Relation.HUSBAND]:
            who.add_spouse(whose)
        elif relation in [Relation.SISTER, Relation.BROTHER]:
            who.add_sibling(whose)

    def request(self, question):
        req_parts = question.split()
        if req_parts[0] == 'Is' and req_parts[2] == 'a':
            return self.gender_request(req_parts[1], req_parts[3][:-1])
        elif tuple(req_parts[0:2]) == ('Who', 'is') and req_parts[2].endswith('\'s'):
            return self.relative_request(req_parts[2][:-2], req_parts[3][:-1])
        else:
            raise Exception("Unknown request type")

    def gender_request(self, name, gender):
        if gender == "man":
            req = Gender.MALE
        elif gender == "woman":
            req = Gender.FEMALE
        else:
            raise Exception("Unknown gender: " + gender)
        if name not in self.people:
            raise Exception(name + " not found")
        person = self.people[name]
        if person.gender == Gender.UNKNOWN:
            return self.DONT_KNOW
        elif person.gender == req:
            return "Yes"
        else:
            return "No"

    def relative_request(self, name, relation):
        if name not in self.people:
            raise Exception(name + " not found")
        grand = "grand"
        count = 0
        who = self.people[name]
        while relation.startswith(grand):
            count += 1
            relation = relation[len(grand):]
        if relation not in Relation.names:
            raise Exception("Unknown relation: " + relation)
        rel = Relation.by_name(relation)
        gender = Gender.by_relation(rel)
        if rel in [Relation.CHILD, Relation.SON, Relation.DAUGHTER]:
            return PedigreeHolder.generate_string(
                PedigreeHolder.find_child(who, count, gender), gender)
        elif rel in [Relation.FATHER, Relation.MOTHER]:
            return PedigreeHolder.generate_string(
                PedigreeHolder.find_parent(who, count, gender), gender)
        elif rel in [Relation.SISTER, Relation.BROTHER]:
            if count > 0:
                raise Exception("Unknown relation: " + relation)
            return PedigreeHolder.generate_string(who.siblings, gender)
        elif rel in [Relation.HUSBAND, Relation.WIFE]:
            if count > 0:
                raise Exception("Unknown relation: " + relation)
            if who.gender == gender:
                raise Exception("can't have spouse with the same gender")
            elif not who.spouse:
                return PedigreeHolder.DONT_KNOW
            else:
                rv = who.spouse.name
                if who.spouse.gender == Gender.UNKNOWN:
                    rv += "?"
                return rv

    @staticmethod
    def generate_string(people, gender):
        if not people:
            return PedigreeHolder.DONT_KNOW
        rv = ""
        for i in people:
            if gender == Gender.UNKNOWN or gender == i.gender:
                rv += i. name + ", "
            elif i.gender == Gender.UNKNOWN and gender != Gender.UNKNOWN:
                rv += i. name + "?, "
        return rv[:-2]

    @staticmethod
    def find_child(who, depth, gender):
        if depth == 0:
            return list(filter(lambda obj: Person.comp_gender(obj, gender),
                               who.children))
        rv = list()
        for i in who.children:
            rv += PedigreeHolder.find_child(i, depth-1, gender)
        return rv

    @staticmethod
    def find_parent(who, depth, gender):
        if depth == 0:
            return list(filter(lambda obj: Person.comp_gender(obj, gender),
                               who.parents))
        rv = list()
        for i in who.parents:
            rv += PedigreeHolder.find_parent(i, depth-1, gender)
        return rv

if __name__ == "__main__":
    ph = PedigreeHolder()
    ph.add("Fred is Ann's brother")
    ph.add("Alice is Ann's sister")
    ph.add("Fred is Alice's sister")
    ph.add("P1 is Fred's mother")
    ph.add("P2 is Fred's father")
    ph.add("GP1 is P1's father")
    print(ph.request("Who is Fred's sister?"))
    print(ph.request("Who is Alice's brother?"))
    print(ph.request("Who is Ann's brother?"))
    print(ph.request("Who is P2's wife?"))
    print(ph.request("Who is Alice's father?"))
    print(ph.request("Who is Fred's mother?"))
    print(ph.request("Who is P1's daughter?"))
    print(ph.request("Who is P2's child?"))
    print(ph.request("Who is GP1's grandson?"))
    print(ph.request("Who is GP1's granddaughter?"))
    print(ph.request("Who is Alice's grandmother?"))
    # ph.add("Fred is Jon's father")
    # ph.add("Ann is Jon's sister")
    # ph.add("Jon is Maria's son")

    # print(ph.request("Is Jon a man?"))
    # print(ph.request("Is Fred a woman?"))
    # print(ph.request("Is Maria a man?"))
    # print(ph.request("Is Ann a woman?"))
