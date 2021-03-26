from __future__ import annotations
import warnings

class Parent:
    """ A parent (or child) which tracks its (optional) parents and children. (effectively a digraph with two 'roots').

    Initializing a parent with no ancestors is done with constructor base_parent and has parents None, None. All other
    instances should have 2 parents.

    Creating children is done with breed(partner) to return a child and tracks this coupling in a list: self.couplings.

    Identity is tracked by a class wide incrementor, starting at 1. It is planned to allow for storing objects to wrap
    more complex data. The class provides methods for identifying
    """

    id_counter = 0

    def __init__(self, object=None, parent1=None, parent2=None,):
        self.object = object
        self.parent1 = parent1
        self.parent2 = parent2
        self.couplings = []
        Parent.id_counter += 1
        self.id = Parent.id_counter
        self.generation = 0
        if parent1 is not None and parent2 is not None:
            self.generation = max(parent1.generation, parent2.generation) + 1

    def __repr__(self):
        return f"<id:{self.id};gen:{self.generation}{' '+str(self.object) if self.object is not None else ''}>"

    @classmethod
    def base_parent(cls, object=None) -> Parent:
        return cls(object, None, None)

    def is_base_parent(self) -> bool:
        if self.parent1 == self.parent2 is None:
            return True
        else:
            return False

    def breed(self, partner) -> Parent:
        try:
            child_object = self.object.breed(partner.object)
        except AttributeError as e:
            if partner.object is not None:
                warnings.warn("Object does not have a breed(x) method.")
            child_object=None
        child = Parent(child_object, parent1=self, parent2=partner)
        coupling = Coupling(partner, child)
        self.couplings.append(coupling)
        partner.couplings.append(coupling)

        return child

    def parents(self) -> list[Parent]:
        if self.is_base_parent():
            return []
        else:
            return [self.parent1, self.parent2]

    def ancestors(self) -> list[Parent]:
        ancestry = self.parents()
        for parent in self.parents():
            ancestry.extend(parent.ancestors())
        return list(set(ancestry))

    def children(self) -> list[Parent]:
        return [coupling.child for coupling in self.couplings]

    def descendants(self) -> list[Parent]:
        descendants = self.children()
        for child in self.children():
            descendants.extend(child.children())
        return list(set(descendants))

    def siblings(self) -> list[Parent]:
        siblings = []
        for p in self.parents():
            siblings.extend(p.children())
        siblings = set(siblings) - {self}
        return list(siblings)

    def direct_relatives(self) -> list[Parent]:
        relatives = []
        relatives.extend(self.parents())
        relatives.extend(self.children())
        return relatives


class Coupling:

    def __init__(self, parent, child):
        self.partner = parent
        self.child = child


class FamilyTree:
    """Basic graph structure which has two 'root' parents.

    Has methods for listing all elements of the family tree. More traditional Node/Edge pairs can be returned from
    members() and directed_edges() functions.
    """

    def __init__(self, parent1:Parent, parent2:Parent):
        self.parent1 = parent1
        self.parent2 = parent2
        self.parent1.breed(self.parent2)

    def __repr__(self):
        members = self.members()
        return f"<FamilyTree: {len(members)} members, {max(m.generation for m in members)} generations>"

    @classmethod
    def from_objects(cls, parent1, parent2):
        return cls(Parent(parent1), Parent(parent2))

    def members(self):
        members = FamilyTree._members(self.parent1)
        for member in members:
            del member.__visited
        return members

    def _members(parent: Parent):
        members = [parent]
        parent.__visited = None
        ## Ordering like this:children then parents gives "deeper" depth first ordering
        drs = parent.children()
        drs.extend(parent.parents())
        for dr in drs:
            try:
                dr.__visited is None
            except AttributeError:
                members.extend(FamilyTree._members(dr))
        return members

    def originators(self):
        return [x for x in self.members() if x.is_base_parent()]

    # def directed_edges(self):
    #     parents = self.originators()
    #     edges = []
    #     while parents:
    #         p = parents.pop(0)
    #         edges.extend([(p,c) for c in p.children()])
    #         parents.extend(p.children())
    #     return list(set(edges))

    def directed_edges(self):
        edges = []
        for p in self.members():
            edges.extend([(p,c) for c in p.children()])
        return edges


if __name__ == "__main__":
    p1 = Parent.base_parent("a")
    p2 = Parent.base_parent("b")
    children = []
    t = FamilyTree(p1, p2)
    p3 = p1.breed(p2)
    children.append(p3)
    p4 = p3.breed(p1)
    children.append(p4)
    p5 = Parent.base_parent()
    p6 = p3.breed(p5)
    children.append(p6)
    p7 = Parent.base_parent()
    p8 = p4.breed(p7)
    children.append(p8)
    p9 = p8.breed(p6)


    print(f"{t.parent1} parents:")
    print(t.parent1.parents())
    print(f"{t.parent1} children:")
    print(t.parent1.children())
    print(f"{t.parent1} descendants:")
    print(t.parent1.descendants())
    print()

    c1 = children[0]
    print(f"{c1} parents:")
    print(c1.parents())
    print(f"{c1} children:")
    print(c1.children())
    print(f"{c1} descendants:")
    print(c1.descendants())
    print()

    c2 = children[1]
    print(f"{c2} parents:")
    print(c2.parents())
    print(f"{c2} children:")
    print(c2.children())
    print(f"{c2} descendants:")
    print(c2.descendants())
    print()

    print(f"{p8} parents:")
    print(p8.parents())
    print(f"{p8} children:")
    print(p8.children())
    print(f"{p8} ancestors")
    print(p8.ancestors())
    print()

    print(f"{p5} ancestors:{p5.descendants()}")

    print()
    print("All children")
    print(children)
    print()

    print("Tree members:")
    members = t.members()
    print(members)
    members.sort(key=lambda x:x.id)
    print(members)
    print("Origininators:")
    print(t.originators())
    print("Edges:")
    print()
    edges = t.directed_edges()
    print(len(edges))

    edges.sort(key=lambda x:x[0].id)
    for e in edges:
        print(e[0].id, e[1].id)