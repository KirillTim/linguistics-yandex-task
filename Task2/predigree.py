

# there are only to genders and traditional families for this task
# husband and farther are male and wife and mother are female
# it's not about tolerance - it's about system rules
# who to determine who are The Wachowskis without this rules?
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

    @staticmethod
    def by_name(name):
        return ["husband", "wife", "father", "mother", "son", "daughter",
                "sister", "brother", "child"].index(name)


class Person(object):
    def __init__(self, name, gender=Gender.UNKNOWN,
                 parents=None, children=None, siblings=None, spouse=None):
        self.name = name
        self.gender = gender
        self.parents = parents.copy() if parents else list()
        self.children = children.copy() if children else list()
        self.siblings = siblings.copy() if siblings else [self]
        self.spouse = spouse

    def __hash__(self):
        return hash(self.name) ^ hash(self.gender)

    def __eq__(self, other):
        if not isinstance(other, Person):
            return False
        return self.name == other.name and self.gender == other.gender

    def __lt__(self, other):
        return self.__hash__() < other.__hash__()

    def add_parent(self, parent):
        print("add_parent("+parent.name+")")

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
            sibling.siblings = self.siblings
            Person.merge(self.siblings, [sibling])

    def add_spouse(self, spouse):
        if not self.spouse:
            self.spouse = spouse
        elif spouse.name != self.spouse.name:
            raise Exception(self.name + " Already have a spouse")
        elif spouse.gender != Gender.UNKNOWN and spouse.gender == self.gender:
            raise Exception(self.name + " Cant have spouse with the same gender")
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
                if i.name == j.name and j.gender == Gender.UNKNOWN:
                    j.gender = i.gender
                    ins = False
                    break
            if ins:
                list1.append(i)
        return list1


class PedigreeHolder(object):
    def __init__(self):
        self.people = []

    def add(self, statement):
        def find_node(node):
            persons = self.find_persons(node)
            if len(persons) > 1:
                raise Exception("Ambiguous name: " + node.name)
            elif len(persons) == 1:
                return persons[0]
            return None

        who_name, _is, whose_name, rel = statement.split()
        if _is != "is" or not whose_name.endswith('\'s'):
            raise Exception("Wrong input statement: "+statement)
        who = Person(who_name, Gender.by_relation(Relation.by_name(rel)))
        whose = Person(whose_name)

        node = find_node(who)
        if node:
            who = node

        node = find_node(whose)
        if node:
            self.people.remove(node)
            whose = node

        PedigreeHolder.__add_relation(who, whose, Relation.by_name(rel))

    def find_persons(self, who):
        persons = []
        for p in self.people:
            persons += p.find_all(who)
        return persons

    @staticmethod
    def __add_relation(who, whose, relation):
        if relation in [Relation.MOTHER, Relation.FATHER]:
            for p in who.children:
                p.add_sibling(whose)
            who.add_child(whose)

