import pprint
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood
from itertools import permutations

# Encoding that will store all of your constraints
E = Encoding()

PROPOSITIONS = []

COL_COUNT = 4
ROW_COUNT = 2

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
    def __str__(self):
        return f"C:col:{self.col},row:{self.row},colour:{self.colour}"
    def __hash__(self):
        return hash(str(self))
    def __eq__(self, other):
        return hash(self) == hash(other)
    


@proposition(E)
class Answer():
    def __init__(self, col: int, colour: str):
        self.col = col
        self.colour = colour
    def __repr__(self):
        return f"Answer: {self.colour} @ ({self.col})"
    def __str__(self):
        return f"A:col:{self.col},colour:{self.colour}"
    def __hash__(self):
        return hash(str(self))
    def __eq__(self, other):
        return hash(self) == hash(other)
    

class Feedback(Base):
    pass

@proposition(E)
class WhiteFeedbackPos(Feedback): # Unconfirmed
    def __repr__(self):
        return f"White Feedback @ ({self.row}, {self.col})"
    def __str__(self):
        return f"W:col:{self.col},row:{self.row}"
    def __hash__(self):
        return hash(str(self))
    def __eq__(self, other):
        return hash(self) == hash(other)
    


@proposition(E)
class BlackFeedbackPos(Feedback): # Confirmed 
    def __repr__(self):
        return f"Black Feedback @ ({self.row}, {self.col})"
    def __str__(self):
        return f"B:col:{self.col},row:{self.row}"
    def __hash__(self):
        return hash(str(self))
    def __eq__(self, other):
        return hash(self) == hash(other)



@proposition(E)
class EmptyFeedbackPos(Feedback): # Wrong
    def __repr__(self):
        return f"Empty Feedback @ ({self.row}, {self.col})"
    def __str__(self):
        return f"E:col:{self.col},row:{self.row}"
    def __hash__(self):
        return hash(str(self))
    def __eq__(self, other):
        return hash(self) == hash(other)
    def __hash__(self):
        return hash(str(self))


# Define a preset board for testing
example_colour_board = [
    ['yellow', 'teal', 'purple', 'orange'],
    ['purple', 'orange', 'green', 'red']
    # ['orange', 'purple', 'teal', 'red']
]
answer = ['yellow', 'teal', 'green', 'red']
example_peg_board = [
    ['b', 'b', 'e', 'e'],
    ['e', 'e', 'b', 'b']
    # ['e', 'e', 'w', 'b']
]
# Colour board
for row in ROWS:
    for col in COLS:
        E.add_constraint(ColourPos(col, row, example_colour_board[row][col]))

# Feedback Board
for row in ROWS:
    for col in COLS:
        if example_peg_board[row][col] == 'b':
            E.add_constraint(BlackFeedbackPos(col, row))
        elif example_peg_board[row][col] == 'w':
            E.add_constraint(WhiteFeedbackPos(col, row))
        elif example_peg_board[row][col] == 'e':
            E.add_constraint(EmptyFeedbackPos(col, row))

# Each guess spot can only have ONE colour
for row in ROWS:
    for col in COLS:
        constraint.add_exactly_one(
            E, [ColourPos(colour, col, row) for colour in COLOURS])


# Each answer spot can only have ONE colour
for col in COLS:
    constraint.add_exactly_one(
        E, [Answer(col, colour) for colour in COLOURS])

# constraint.add_implies_all

# Each feedback can only have ONE type of feedback (white, black empty)
for row in ROWS:
    for col in COLS:
        constraint.add_exactly_one(
            E, [WhiteFeedbackPos(col, row),
                EmptyFeedbackPos(col, row),
                BlackFeedbackPos(col, row)])

# Each row must not contain duplicate colours
for row in ROWS:
    for colour in COLOURS:
        for col1 in COLS:
            for col2 in COLS:
                if col1 != col2:
                    E.add_constraint((~ColourPos(col1, row, colour) | ~ColourPos(col2, row, colour)))

# Answer cannot contain duplicate colours
for colour in COLOURS:
    for col1 in COLS:
        for col2 in COLS:
            if col1 != col2:
                E.add_constraint(~Answer(col1, colour) | ~Answer(col2, colour))

# #Testing Purposes - Make board all one colour with black feedbacks (should only be one solution)
# for row in ROWS:
#     for col in COLS:
#         E.add_constraint(BlackFeedbackPos(col, row))
#         E.add_constraint(ColourPos(col, row, COLOURS[0]))
# for col in COLS:
#     E.add_constraint(Answer(col, COLOURS[0]))




## Colour + Feedback >> Answer

# Black feedback peg constraints
for row in ROWS:
    for col in COLS:
        for colour in COLOURS:
            E.add_constraint((BlackFeedbackPos(col, row) & ColourPos(col, row, colour)) >> Answer(col, colour))
    E.add_constraint(~BlackFeedbackPos(0, row) | ~BlackFeedbackPos(1, row) | ~BlackFeedbackPos(2, row) | ~BlackFeedbackPos(3, row)) # Every row must have at least one non-black peg


# # White feedback pegs constraints
for row in ROWS:
    for col in COLS:
        for colour in COLOURS:
            E.add_constraint((WhiteFeedbackPos(col, row) & ColourPos(col, row, colour)) >> (Answer(0, colour) | Answer(1, colour) | Answer(2, colour) | Answer(3, colour) & ~Answer(col, colour)))

# Empty feedback pegs constraints
for row in ROWS:
    for col in COLS:
        for colour in COLOURS:
            E.add_constraint((EmptyFeedbackPos(col, row) & ColourPos(col, row, colour)) >> (~Answer(0, colour) & ~Answer(1, colour) & ~Answer(2, colour) & ~Answer(3, colour)))





## Colour + answer >> feedback

# Black peg must exist if guess coincides with answer
for row in ROWS:
    for col in COLS:
        for color in COLOURS:
            E.add_constraint((ColourPos(col, row, colour) & Answer(col, colour)) >> BlackFeedbackPos(col, row))

# # White peg must exist if guess slot in in answer, but is in incorrect posiition
for row in ROWS:
    for colour in COLOURS:
        for col1 in COLS:
            for col2 in COLS:
                if col1 != col2:
                    E.add_constraint((ColourPos(col1, row, colour) & Answer(col2, colour)) >> WhiteFeedbackPos(col1, row))

# No peg can exist if colour does not exist in answer
for row in ROWS:
    for col in COLS:
        for colour in COLOURS:
            E.add_constraint((ColourPos(col, row, colour) & (~Answer(0, colour) & ~Answer(1, colour) & ~Answer(2, colour) & ~Answer(3, colour))) >>
                EmptyFeedbackPos(col, row))


## Feedback + answer >> colour

# Black feedback peg with respective answer determines that respective guess slot
for row in ROWS:
    for col in COLS:
        for colour in COLOURS:
            E.add_constraint((BlackFeedbackPos(col, row) & Answer(col, colour)) >> ColourPos(col, row, colour))

# # White feedback peg with respective answer determines that respective guess slot
# for row in ROWS:
#     for col in COLS:
#         for colour in COLOURS:
#             E.add_constraint((WhiteFeedbackPos(col, row) & Answer(col, colour)) >> ~ColourPos(col, row, colour))

# Empty feedback peg with respective answer determines that respective guess slot
for row in ROWS:
    for col in COLS:
        for colour in COLOURS:
            for col2 in COLS:
                E.add_constraint((EmptyFeedbackPos(col, row) & Answer(col2, colour)) >> ~ColourPos(col, row, colour))






#a # Proposition for guesses
# @proposition(E)
# class Guess:
#     def __init__(self, val):
#         self.val = val
#     def __repr__(self):
#         return f"Guess: {' '.join(self.val)}"



        
# Generate all valid guesses (no duplicate colours per guess)
all_valid_guesses = permutations(COLOURS, 4) 



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
    # sol = T.solve()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    # print("   Solution: %s" % T.solve())
    print("Len is:", len(list(all_valid_guesses)))
    print (len('8933463857385268217578842664615280640'))
    # print("\nVariable likelihoods:")
    # for v,vn in zip([a, b, c, x, y, z], 'abcxyz'):
    #     # Ensure that you only send these functions NNF formulas
    #     # Literals are compiled to NNF here
    #     print(" %s: %.2f" % (vn, likelihood(T, v)))
    # print()

    