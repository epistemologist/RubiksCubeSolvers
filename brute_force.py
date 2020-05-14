# Brute force solver for puzzles with smaller search spaces
# Similar to ksolve+ and ksolve++, in fact we will use modified definition files provided by https://mzrg.com/rubik/ksolve+/

import re
from math import factorial
from collections import namedtuple

DEFINITION_PATH = "test.def"
MAX_ARRAY_SIZE = 10000000


# Nasty parser for the definition files
lines = open(DEFINITION_PATH).readlines()
lines = [line for line in lines if "#" not in line] # Removed commented lines
text = "".join(lines)
piece_types = [i.replace("Set",'').split() for i in re.findall("Set .*", text)]
piece_types = {i[0]:(int(i[1]),int(i[2])) for i in piece_types}
move_lines = lines[lines.index("BeginMoves\n"):lines.index("EndMoves\n")+1]
moves = []
temp = []
for line in move_lines:
	temp.append(line.strip())
	if "End" in line:
		moves.append(temp)
		temp = []
print(moves)
moves = [i[1:-1] for i in moves][:-1]
solved_state = moves[0]
cancellable_moves = [line.strip().split("\t") for line in lines[lines.index("BeginCancelMoves\n")+1:lines.index("EndCancelMoves\n")]]
cancellable_moves = {i[0]:i[1].split() for i in cancellable_moves}
print(cancellable_moves)
moves_list = {}
for move in moves:
	move_name, move = move[0].replace("Move", ""), move[1:]
	labels = [move.index(i) for i in move if not i.replace(" ","").isdigit()]
	splits = [(labels[i],labels[i+1]) for i in range(len(labels)-1)] + [(labels[-1],len(move))]
	print(move)
	moves_list[move_name.strip()] = ({move[i]:[list(map(int, s.split())) for s in move[i+1:j]] for i,j in splits})

# Utility functions for dealing with permutations

def to_lehmer_code(perm):
	return [sum([perm[j]<perm[i] for j in range(i+1,len(perm))]) for i in range(len(perm))]
def from_lehmer_code(code):
	out = []
	possible_numbers = list(range(len(code)))
	for i in code:
		out.append(possible_numbers[i])
		possible_numbers.remove(possible_numbers[i])
	return out
def factorial_base_encode(N):
	out = []
	i = 1
	while N != 0:
		out.append(N%i)
		N //= i
		i += 1
	return out[::-1]
def factorial_base_decode(arr):
	return sum([factorial(i)*j for i,j in enumerate(reversed(arr))])
def perm_encode(perm):
	return factorial_base_decode(to_lehmer_code(perm))
def perm_decode(N,length):
	lehmer_code = factorial_base_encode(N)
	while len(lehmer_code) != length:
		lehmer_code = [0] + lehmer_code
	return from_lehmer_code(lehmer_code)
def compose_permutations(perm1, perm2):
	out = [None for i in range(len(perm1))]
	for i in range(len(perm1)):
		out[perm2[i]] = perm1[i]
	return out

# Utility functions with dealing with orientations

def orientation_to_int(arr, states):
	return sum([j*states**i for i,j in enumerate(reversed(arr))])

def orientation_from_int(N, states):
	out = []
	while N != 0:
		out.append(N%states)
		N //= states
	return out[::-1]

def compose_orientations(orientation1, orientation2, states):
	return [(i+j)%states for i,j in zip(orientation1, orientation2)]

# Generation of move tables
def gen_move_tables():
	"""
	Returns a nested dictionary in following form
	{
		"Move Name" :
		{
			"Piece Type" : [Permutation Table],
			"Piece Type" : [Permutation Table, Orientation Table]
		},
		...
	}
	"""
	for piece_type in piece_types:
		n,m = piece_types[piece_type]
		if pow(n,m) > MAX_ARRAY_SIZE or factorial(n) > MAX_ARRAY_SIZE: return None
	move_table = {}
	for move in moves_list:
		current_move_tables = {}
		for piece_type in moves_list[move]:
			current_info = moves_list[move][piece_type]
			current_info[0] = list(map(lambda x: x-1, current_info[0])) # subtract 1 from the permutation of the move for proper execution of code
			n, orientations = piece_types[piece_type]
			permutation_table = [compose_permutations(perm_decode(i,n),current_info[0]) for i in range(factorial(n))]
			orientation_table = None
			if len(current_info) == 2:
				orientation_table = [compose_orientations(orientation_from_int(i, orientations),current_info[1],orientations) for i in range(n**orientations)]
			current_move_tables[piece_type] = [permutation_table, orientation_table]
		move_table[move] = current_move_tables
	return move_table

move_table = gen_move_tables()

Cube = namedtuple("Cube", "moves state")

# Function that applies a move to a cube
def apply_move(cube, move):
	new_state = {}
	if move_table:
		move_info = move_table[move]
		for piece_type in piece_types:
			n, orientations = piece_types[piece_type]
			new_state_pieces = []
			new_state_pieces.append(move_info[piece_type][0][perm_encode(cube.state[piece_type][0])]) # Update permutation information
			if len(move_info[piece_type]) != 2 or not move_info[piece_type][1]:
				new_state_pieces.append(cube.state[piece_type][1]) # No changes to orientation
			else:
				new_state_pieces.append(move_info[piece_type][1][orientation_to_int(cube.state[piece_type][1], orientations)])  # Update orientation information
			new_state[piece_type] = new_state_pieces
		return Cube(cube.moves + [move], new_state)
	else:
		move_info = moves_list[move]
		for piece_type in piece_types:
			n, orientations = piece_types[piece_type]
			new_state_pieces = []
			new_state_pieces.append(compose_permutations(cube.state[piece_type][0], move_info[piece_type][0])) # Update permutation information
			if len(move_info[piece_type]) != 2 or not move_info[piece_type][1]:
				new_state_pieces.append(cube.state[piece_type][1]) # No changes to orientation
			else:
				new_state_pieces.append(compose_orientations(cube.state[piece_type][1], move_info[piece_type][1], orientations)) # Update orientation information
			new_state[piece_type] = new_state_pieces
		return Cube(cube.moves + [move], new_state)
# Function to return a solved cube object
def get_solved_cube():
	state = {}
	for piece_type in piece_types:
		n = piece_types[piece_type][0]
		state[piece_type] = [list(range(n)),[0 for i in range(n)]]
	return Cube([], state)
# Test code
solved_cube = get_solved_cube()
print("cube with move table")
cube = apply_move(solved_cube, 'U')
print(cube)
print("cube with no move table")
move_table = None
cube = apply_move(solved_cube, 'U')
print(cube)
