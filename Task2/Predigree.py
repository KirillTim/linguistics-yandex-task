

# there are only to genders and traditional families for this task
# husband and farther are male and wife and mother are female
# it's not about tolerance - it's about system rules
# who to determine who are The Wachowskis without this rules?
class Gender(object):
    UNKNOWN, MALE, FEMALE = range(3)

    @staticmethod
    def by_relation(relation):
        if relation == Relation.HUSBAND or relation == Relation.FATHER \
                or relation == Relation.SON or relation == Relation.BROTHER:
            return Gender.MALE
        elif relation == Relation.WIFE or relation == Relation.MOTHER \
                or relation == Relation.DAUGHTER or relation == Relation.SISTER:
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
        self.parents = parents
        self.children = children
        self.siblings = siblings
        self.spouse = spouse

    def __hash__(self):
        return hash(self.name) ^ hash(self.gender)

    def __eq__(self, other):
        return self.name == other.name and self.gender == other.gender

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

    def add_sibling(self, sibling):
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


class PedigreeHolder(object):
    def __init__(self):
        self.people = []

    def add(self, statement):
        def find_node(node):
            persons = self.find_person(node)
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



    def find_person(self, who):
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

a = Person("Alex", Person.MALE)
b = Person("Alex", Person.FEMALE)

print(a.__hash__())
print(b.__hash__())
