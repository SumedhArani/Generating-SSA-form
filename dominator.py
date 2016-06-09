import re

def find_leaders(str):
	#list of all the statements in the given 3 addr code intermediate representaion
	irs = (list(map(lambda x: x.strip(),str.split("\n"))))
	goto_statements = list(filter(lambda x: "goto" in x ,irs))
	#all tuples that immediately follow a goto statement is a leader
	followers = [irs[irs.index(x)+1] for x in goto_statements]
	#all labels that are after a goto statement
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
	#dotty representaton
	fout = open("cfg.dot",'w+')
	fout.write("digraph {\n")
	for each in graph:
		fout.write("{0} -> {1};\n".format(each[0],each[1]))
	fout.write("}")
	fout.close()
	return graph

def find_dom(graph, leader_set, irs):
	#wrapper function
	initial = graph[0][0]
	#Dom(n) = {n} union with intersection over Dom(p) for all p in pred(n)
	#makes recursive calls to compute the dominators of a given node
	def dom(n):
		if n!=initial:
			dom_set = {n}
			pred = [x[0] for x in list(filter(lambda x: x[1]==n,graph))]
			dom_pred = dom(pred[0])
			#intersection of the dominators of its predecessors
			map(lambda x:dom_pred.intersection(dom(x)), pred)
			dom_set = dom_set.union(dom_pred)
			return dom_set
		else:
			return {initial}
	dom_tree=[]
	#finding immediate dom
	for x in range(1,len(leader_set)):
		dom_tree.append((max(dom(x)-{x}), x))
	#dotty representation
	fout = open("domtree.dot",'w+')
	fout.write("digraph {\n")
	for each in dom_tree:
		fout.write("{0} -> {1};\n".format(each[0],each[1]))
	fout.write("}")
	fout.close()
	return dom_tree

def main():
	file = open("input.txt")
	leader_set, irs = find_leaders(file.read())
	file.close()
	graph = create_cfg(leader_set, irs)
	dom_tree = find_dom(graph, leader_set, irs)

if __name__ == '__main__':
	main()