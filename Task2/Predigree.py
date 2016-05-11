

# there are only to genders and traditional families for this task
# husband and farther are male and wife and mother are female
# it's not about tolerance - it's about system rules
# who to determine who are The Wachowskis without this rules?
class Gender(object):
    UNKNOWN, MALE, FEMALE = range(3)


class Relation(object):
    HUSBAND, WIFE, FATHER, MOTHER, SON, DAUGHTER, \
        SISTER, BROTHER, CHILD = range(9)


class Person(object):
    def __init__(self, name, gender=Gender.UNKNOWN,
                 parents=None, children=None, siblings=None, spouse=None):
        self.name = name
        self.gender = gender
        self.parents = parents
        self.children = children
        self.siblings = siblings
        self.spouse = spouse

    def __hash__(self):
        return hash((self.name, self.gender, self.parents,
                     self.children, self.siblings, self.spouse))

    def add_parent(self, parent):
        if Person.__add_to_group(self.parents, parent):
            if len(self.parents) == 2:
                raise Exception(self.name+" already have two parents")
            if parent.gender != Gender.UNKNOWN:
                for p in self.parents:
                    if parent.gender == p.gender:
                        raise Exception(self.name+" can't have two parents "
                                                  "with the same gender")
            self.parents.append(parent)

    def add_child(self, child):
        if Person.__add_to_group(self.children, child):
            self.children.append(child)

    def add_siblings(self, sibling):
        if Person.__add_to_group(self.siblings, sibling):
            self.siblings.append(sibling)

    def add_spouse(self, spouse):
        if not self.spouse:
            self.spouse = spouse
        elif spouse.gender != Gender.UNKNOWN and spouse.gender == self.gender:
            raise Exception(self.name+" Cant have spouse with the same gender")
        elif spouse.name == self.spouse.name:
            if self.spouse.gender == Gender.UNKNOWN:
                self.spouse.gender = spouse.gender
        else:
            raise Exception(self.name+" Already have a spouse")

    # we can have only two children/siblings with the same name,
    # they should have different genders, though
    @staticmethod
    def __add_to_group(where, who):
        for i in where:
            if i.name == who.name and i.gender == who.gender:
                return False
        if who.gender != Gender.UNKNOWN:
            for i in where:
                if i.name == who.name and i.gender == Gender.UNKNOWN:
                    i.gender = who.gender
                    return False
        return True





a = Person("Alex", Person.MALE)
b = Person("Alex", Person.FEMALE)

print(a.__hash__())
print(b.__hash__())
