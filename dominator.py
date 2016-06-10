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

def find_dom(graph, size):
	#wrapper function
	#size is the number of leaders
	initial = graph[0][0]
	#Dom(n) = {n} union with intersection over Dom(p) for all p in pred(n)
	#makes recursive calls to compute the dominators of a given node
	def dom(n):
		if n!=initial:
			dom_set = {n}
			pred = [x[0] for x in list(filter(lambda x: x[1]==n,graph))]
			dom_pred = dom(pred[0])
			#intersection of the dominators of its predecessors
			map(lambda x:dom_pred.update(dom_pred.intersection(dom(x))), pred)
			dom_set.update(dom_pred)
			return dom_set
		else:
			return {initial}
	dom_tree=[]
	dom_set=[]
	#finding immediate dom
	for x in range(1, size):
		#(idom(n),n)
		dom_tempset = dom(x)
		dom_tree.append((max(dom_tempset-{x}), x))
		dom_set.append(dom_tempset)
	#dotty representation
	fout = open("domtree.dot",'w+')
	fout.write("digraph {\n")
	for each in dom_tree:
		fout.write("{0} -> {1};\n".format(each[0],each[1]))
	fout.write("}")
	fout.close()
	return (dom_tree, dom_set)

def find_domfrontier(dom_tree, graph, dom_set):
	#wrapper function
	#dom_tree = [(idom(n), n)] #data-structure
	def df(n):
		def df_local(n):
			#df_local -> set of those succesors of n whose immediate dominator is not n
			succesors = [x[1] for x in filter(lambda x: x[0]==n,graph)]
			return (set(filter(lambda x: dom_tree[x-1][0]!=n,succesors)))

		def df_up(c):
			up_set = set()
			for w in df(c):
				if w not in dom_set[n-1]:
					up_set.update({w}) 
			return up_set
		dom_tset = set()
		temp = [x[1] for x in filter(lambda x: x[0]==n,dom_tree)]
		
		'''
		Neither of the below code worked
		Could you help me understand why?
		No matter how I try the dom_tset which is a temprory varible doesn't get affected
		map(lambda y: dom_tset.update({y}), temp)
		map(lambda y: dom_tset.update(df_up(y)), temp)
		I eventually had to use a for loop to do the same which worked smoothly
		'''
		for e in temp:
			dom_tset.update(df_up(e))

		return df_local(n).union(dom_tset)

	'''
	Dubious code
	def df_aliter(x):
		#dom_set begins with dominators for the first node and following and hence index begins with 0
		#y is the set of edges over which x dominates
		y = dom_set[x-1]
		#z is the set of nodes whose pred are dominated by x
		z = [x[1] for x in filter(lambda x: x[0] in y ,graph)]
		#these node should'nt be strictly dominated by x
		return set(filter(lambda x:x not in y-{x}, z))
	
	print(df_aliter(3))
	'''

def main():
	file = open("input.txt")
	leader_set, irs = find_leaders(file.read())
	file.close()
	graph = create_cfg(leader_set, irs)
	dom_tree, dom_set = find_dom(graph, len(leader_set))
	find_domfrontier(dom_tree, graph, dom_set)

if __name__ == '__main__':
	main()