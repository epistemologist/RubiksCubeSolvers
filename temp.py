f = open("test","r")
g = open("out","w")

text = f.readlines()
for line in text:
	if "#" not in line and "".join(line.split()).isdigit():
		line_ = " ".join(map(str, [int(i)-1 for i in line.split()])) + "\n"
	else: line_ = line
	g.write(line_)

