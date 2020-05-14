# Brute force solver for puzzles with smaller search spaces
# Similar to ksolve+ and ksolve++, in fact we will use modified definition files provided by https://mzrg.com/rubik/ksolve+/

import re

DEFINITION_PATH = "test.def"

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
moves = [i[1:-1] for i in moves][:-1]
solved_state = moves[0]
moves = moves[1:]
cancellable_moves = [line.strip().split("\t") for line in lines[lines.index("BeginCancelMoves\n")+1:lines.index("EndCancelMoves\n")]]
cancellable_moves = {i[0]:i[1].split() for i in cancellable_moves}
print(cancellable_moves)
moves_list = {}
for move in moves:
	move_name, move = move[0].replace("Move", ""), move[1:]
	labels = [move.index(i) for i in move if not i.replace(" ","").isdigit()]
	splits = [(labels[i],labels[i+1]) for i in range(len(labels)-1)] + [(labels[-1],len(move))]
	print(move)
	moves_list[move_name] = ({move[i]:[list(map(int, s.split())) for s in move[i+1:j]] for i,j in splits})

# Utility functions for dealing/encoding permutations

