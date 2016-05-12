

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
                 parents=list(), children=list(), siblings=list(), spouse=None):
        self.name = name
        self.gender = gender
        self.parents = parents
        self.children = children
        self.siblings = [self] if not siblings else siblings
        self.spouse = spouse

    def __hash__(self):
        return hash(self.name) ^ hash(self.gender)

    def __eq__(self, other):
        return self.name == other.name and self.gender == other.gender

    def add_parent(self, parent):
        print("add_parent("+parent.name+")")

        def try_to_set_gender(old, new):
            if old.gender == Gender.UNKNOWN and old.name == new.name:
                old.gender = new.gender
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
            Person.merge(self.children, [sibling])

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

