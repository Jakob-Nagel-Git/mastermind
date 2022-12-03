import pprint
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood
from itertools import permutations

# Encoding that will store all of your constraints
E = Encoding()

COL_COUNT = 4
ROW_COUNT = 5

# Creates an 11x4 matrix of 0s
empty_board = [[0]*COL_COUNT for _ in range(ROW_COUNT)]

COLOURS = ["purple", "red", "green", "yellow", "teal", "orange"]
COLS = range(COL_COUNT)
ROWS = range(ROW_COUNT)



class Base:
    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row


# Proposition for a peg of a particular color in a particular position
@proposition(E)
class ColourPos(Base):

    def __init__(self,  col: int, row: int, colour: str):
        super().__init__(col, row)
        self.colour = colour

    def __repr__(self):
        return f"Colour: {self.colour} @({self.row}, {self.col})"


class Feedback(Base):
    pass

@proposition(E)
class WhiteFeedbackPos(Feedback):
    def __repr__(self):
        return f"White Feedback @ ({self.row}, {self.col})"

@proposition(E)
class BlackFeedbackPos(Feedback):
    def __repr__(self):
        return f"Black Feedback @ ({self.row}, {self.col})"

@proposition(E)
class EmptyFeedbackPos(Feedback):
    def __repr__(self):
        return f"Empty Feedback @ ({self.row}, {self.col})"


# Each spot can only have ONE colour
for row in ROWS:
    for col in COLS:
        constraint.add_exactly_one(
            E, [ColourPos(colour, col, row) for colour in COLOURS])




# Each feedback can only have ONE type of feedback (white, black empty)
for row in ROWS:
    for col in COLS:
        constraint.add_exactly_one(
            E, [WhiteFeedbackPos(col, row),
                EmptyFeedbackPos(col, row),
                BlackFeedbackPos(col, row)])





# Proposition for guesses
@proposition(E)
class Guess:
    def __init__(self, val):
        self.val = val
    def __repr__(self):
        return f"Guess: {' '.join(self.val)}"

        

# Generate all valid guesses (no duplicate colours per guess)
all_valid_guesses = permutations(COLOURS, 4) 


# Each guess must must not contain duplicate colours
for row in ROWS:
    constraint.add_exactly_one(E, [Guess(val) for val in all_valid_guesses])

# Guesses and answer cannot contains duplicate colours.
# for row in ROWS:
#     for col in COLS:
        


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    # Add custom constraints by creating formulas with the variables you created
    E.add_constraint((a | b) & ~x)
    # Implication
    E.add_constraint(y >> z)
    # Negate a formula# Call your variables whatever you want


if __name__ == "__main__":

    T = E.compile()
    # Don't compile until you're finished adding all your constraints!
    sol = T.solve()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())
    print("Len is:", len(list(all_valid_guesses)))
    print("\nVariable likelihoods:")
    for v,vn in zip([a, b, c, x, y, z], 'abcxyz'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()

    