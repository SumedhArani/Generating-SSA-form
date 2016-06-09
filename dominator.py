import re

def find_leaders(str):
	#list of all the statements in the given 3 addr code intermediate representaion
	irs = (list(map(lambda x: x.strip(),str.split("\n"))))
	goto_statements = list(filter(lambda x: "goto" in x ,irs))
	#all tuples that immediately follow a goto statement is a leader
	followers = [irs[irs.index(x)+1] for x in goto_statements]
	blocks = [re.match(".*goto (.*)", x).group(1)+":" for x in goto_statements if re.match(".*goto (.*)", x).group(1)+":" not in followers]
	leaders = [irs[0]] + followers + blocks
	leaders.sort(key = lambda x: irs.index(x))
	leaders_index = [irs.index(x) for x in leaders]
	leader_set = zip(leaders, leaders_index)
	return list(leader_set), irs

def create_cfg(leader_set, irs):
	#go sequentially
	#if the last statement is not a conditional statement then the immediate block
	#following it is it's successor
	#if a conditional statement is at the end than find the leader corresponding to it and create an edge
	initial = leader_set[0]
	#graph is a list of 2-tuple having node A and node B
	graph =[]
	leaders= [x[0] for x in leader_set]
	leaders_index= [x[1] for x in leader_set]
	#handles first condition
	for x in leader_set[1:]:
		#checks for the last statement in the prev basic block
		#conditional goto statements
		#print(irs[x[1]-1])
		if 'goto' in irs[x[1]-1]:
			graph.append((leader_set.index(x)-1,leaders.index(re.match(".*goto (.*)", irs[x[1]-1]).group(1)+":")))
			if re.match("if.*", irs[x[1]-1]):
				graph.append((leader_set.index(x)-1, leader_set.index(x)))
		#if it is an unconditional goto statement
		else:
			graph.append((leader_set.index(x)-1, leader_set.index(x)))
	#print(graph)
	#print(leader_set)
	fout = open("out.dot",'w+')
	fout.write("digraph {\n")
	for each in graph:
		fout.write("{0} -> {1};\n".format(each[0],each[1]))
	fout.write("}")
	fout.close()
	return graph

def find_dom(graph, leader_set, irs):
	pass

def main():
	file = open("input.txt")
	leader_set, irs = find_leaders(file.read())
	file.close()
	graph = create_cfg(leader_set, irs)
	find_dom(graph, leader_set, irs)

if __name__ == '__main__':
	main()

'''
/ dominator of the start node is the start itself
 Dom(n0) = {n0}
 // for all other nodes, set all nodes as the dominators
 for each n in N - {n0}
     Dom(n) = N;
 // iteratively eliminate nodes that are not dominators
 while changes in any Dom(n)
     for each n in N - {n0}:
         Dom(n) = {n} union with intersection over Dom(p) for all p in pred(n)
'''