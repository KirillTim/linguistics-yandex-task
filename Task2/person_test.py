import unittest
from predigree import Person, Gender, Relation


class PersonTest(unittest.TestCase):

    def test_add_parent_1(self):
        c1 = Person("Alex")
        p1 = Person("Bob")
        c1.add_parent(p1)

        self.assertEqual(c1.parents, [p1])
        self.assertEqual(p1.children, [c1])

    def test_add_parent_2(self):
        c1 = Person("c1")
        p1 = Person("p1")
        c1.add_parent(p1)
        c2 = Person("c2")
        c2.add_parent(p1)

        self.assertListEqual(c1.parents, [p1])
        self.assertListEqual(c2.parents, [p1])
        self.assertListEqual(sorted(p1.children), sorted([c1, c2]))
        self.assertListEqual(sorted(c1.siblings), sorted([c1, c2]))
        self.assertListEqual(sorted(c2.siblings), sorted([c1, c2]))

    def test_add_parent_3(self):
        c1 = Person("c1")
        pm = Person("pm", Gender.MALE)
        p1 = Person("p1", Gender.UNKNOWN)
        c1.add_parent(pm)
        c1.add_parent(p1)

        self.assertEqual(pm.gender, Gender.MALE)
        self.assertEqual(p1.gender, Gender.FEMALE)
        self.assertListEqual(sorted(c1.parents), sorted([p1, pm]))
        self.assertEqual(p1.spouse, pm)
        self.assertEqual(pm.spouse, p1)
        self.assertEqual(p1.children, [c1])
        self.assertEqual(pm.children, [c1])

    def test_add_parent_4(self):
        c1 = Person("c1")
        p1 = Person("p1", Gender.UNKNOWN)
        p2 = Person("p1", Gender.MALE)
        c1.add_parent(p1)
        c1.add_parent(p2)

        self.assertEqual(c1.parents, [Person("p1", Gender.MALE)])

    def test_add_parent_5(self):
        c1 = Person("c1")
        p1 = Person("p1", Gender.MALE)
        p2 = Person("p1", Gender.UNKNOWN)
        c1.add_parent(p1)
        c1.add_parent(p2)

        self.assertEqual(c1.parents, [Person("p1", Gender.MALE)])

    def test_add_parent6(self):
        c1 = Person("c1")
        p1 = Person("pa", Gender.MALE)
        p2 = Person("pa", Gender.FEMALE)
        c1.add_parent(p1)
        c1.add_parent(p2)

        self.assertEqual(c1.parents, [p1, p2])

    def test_add_sibling(self):
        c1 = Person("c1")
        p1 = Person("p1")
        c1.add_parent(p1)
        c2 = Person("c2")
        c1.add_sibling(c2)

        self.assertListEqual(c1.parents, [p1])
        self.assertListEqual(c2.parents, [p1])
        self.assertListEqual(sorted(p1.children), sorted([c1, c2]))
        self.assertListEqual(sorted(c1.siblings), sorted([c1, c2]))
        self.assertListEqual(sorted(c2.siblings), sorted([c1, c2]))

    def test_add_spouse(self):
        c1 = Person("c1")
        p1 = Person("p1", Gender.FEMALE)
        p2 = Person("p2", Gender.UNKNOWN)

        c1.add_parent(p1)
        p1.add_spouse(p2)

        self.assertListEqual(sorted(c1.parents), sorted([p1, p2]))
        self.assertListEqual(p2.children, [c1])
        self.assertEqual(p1.spouse, p2)
        self.assertEqual(p2.spouse, p1)

    def test_add_children(self):
        p1 = Person("p1")
        c1 = Person("c1")
        c2 = Person("c2")
        p1.add_child(c1)
        p1.add_child(c2)

        self.assertEqual(c2.parents, [p1])
        self.assertListEqual(sorted(p1.children), sorted([c1,c2]))
        self.assertListEqual(sorted(c1.siblings), sorted([c1,c2]))
        self.assertListEqual(sorted(c2.siblings), sorted([c1,c2]))

if __name__ == '__main__':
    unittest.main()
