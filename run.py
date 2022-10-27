from enum import Enum
import pprint
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# Encoding that will store all of your constraints
E = Encoding()

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding


class COLOUR(Enum):
    PURPLE = "P"
    RED = "R"
    GREEN = "G"
    YELLOW = "Y"
    TEAL = "T"

@proposition(E)
@constraint.at_least_one(E)
class ColourPropositions:

    def __init__(self, colour: COLOUR, col: int, row: int):
        self.colour = colour
        self.col = col
        self.row = row

    def __repr__(self):
        return f"Colour: {self.colour} @({self.col}, {self.row})"

@proposition(E)
@constraint.at_least_one(E)
class FeedbackPropositions:

    def __init__(self, feedback, col, row):
        self.colour = colour
        self.col = col
        self.row = row

    def __repr__(self):
        return f"FeedBack: {self.colour} @ {self}"


@proposition(E)
class FancyPropositions:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"

# Call your variables whatever you want

colours = {
    # Teal
    "T": [],
    # Yellow
    "Y": [],
    # Orange
    "O": [],
    # Green
    "G": [],
    # Purple
    "P": [],
    # Red
    "R": []
}

for colour in colours:
    # "P" = [[],[],[],[],[],[],[],[],[]]
    # colors[key].append([True, False, False])
    for i in range(11):
        propositions = []
        for j in range(4):
            prop = ColourPropositions(colour,j,i)
            propositions.append(prop)
        colours[colour].append(propositions)

pprint.pprint(colours)


a = BasicPropositions("P11")
b = BasicPropositions("b")   
c = BasicPropositions("c")
d = BasicPropositions("d")
e = BasicPropositions("e")
# At least one of these will be true
x = FancyPropositions("x")
y = FancyPropositions("y")
z = FancyPropositions("z")


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    # Add custom constraints by creating formulas with the variables you created. 
    E.add_constraint((a | b) & ~x)
    # Implication
    E.add_constraint(y >> z)
    # Negate a formula
    E.add_constraint((x & y).negate())
    # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    constraint.add_exactly_one(E, a, b, c)

    return E


if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()
