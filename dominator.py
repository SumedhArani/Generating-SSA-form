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
	leader_set = list(set(leader_set))
	leader_set.sort(key = lambda x: x[1])
	return list(leader_set), irs

def create_cfg(leader_set, irs):
	#go sequentially
	#if the last statement is not a conditional statement then the immediate block
	#following it is it's successor
	#if a conditional statement is at the end than find the leader corresponding to it and create an edge
	initial = leader_set[0]
	graph =[]
	leaders= [x[0] for x in leader_set]
	leaders_index= [x[1] for x in leader_set]
	#handles first condition
	for x in leader_set[1:]:
		#checks for the last statement in the prev basic block
		#conditional goto statements
		if 'goto' in irs[x[1]-1]:
			#if a jump statement
			graph.append((leader_set.index(x)-1,leaders.index(re.match(".*goto (.*)", irs[x[1]-1]).group(1)+":")))
			#if ends in conditional
			if re.match("if.*", irs[x[1]-1]):
				graph.append((leader_set.index(x)-1, leader_set.index(x)))
		#if it is not a  goto statement
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

def create_domtree(graph, size):
	#size is the number of leaders
	initial = graph[0][0]
	#Dom(n) = {n} union with intersection over Dom(p) for all p in pred(n)
	dom_temp = []
	for i in range(size):
		dom_temp.append({initial, i})
	#recursion was the initial approach, changed algorithm
	def dom(n):
			dom_set = dom_temp[n]
			pred = [x[0] for x in list(filter(lambda x: x[1]==n,graph))]
			dom_check = [dom_temp[x] for x in pred]
			dom_inter = dom_check[0]
			for each in dom_check:
				dom_inter = dom_inter.intersection(each)
			#intersection of the dominators of its predecessors
			#list(map(lambda x:dom_set.update(dom_set.intersection(dom_temp[x])), pred))
			dom_set.update(dom_inter)
			dom_temp[n].update(dom_set)
			return dom_set
	
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
	#dom_tree = [(idom(n), n)] #data-structure
	dom_set.insert(0,{0})
	dom_tree.insert(0,(-1,0))

	df_set = []
	for x in range(len(dom_set)):
		df_set.append(set())

	for node in [x[1] for x in dom_tree]:
		#if num of pred greater than 1
		pred = [x[0] for x in filter(lambda x: x[1]==node,graph)]
		for each_pred in pred:
			runner = each_pred
			while runner!=dom_tree[node][0]:
				df_set[runner].update({node})
				runner = dom_tree[runner][0]

	return df_set


def find_var_origin(irs, leader_set):
	#re.match('(.*)=.* ',s).group(1).strip()
	#var_origin is the set of variables along with the line num in which they're
	var_origin = [(re.match('(.*)=.* ',s).group(1).strip(), irs.index(s)) for s in irs if re.match('(.*)=.* ',s)]
	var_origin = list(filter(lambda x: 'if' not in x[0], var_origin))
	#using the indexes from which basic blocks begin and end find to which blocks have variables been defined in
	leader_set_index = [x[1] for x in leader_set]
	leader_set_index.append(len(irs))
	varnode_origin = [leader_set_index.index(max(leader_set_index, key = lambda x: x>s[1]))-1 for s in var_origin]
	varlist_temp = list(zip([x[0] for x in var_origin], varnode_origin))
	varlist_origin = {}
	for x in range(len(leader_set)):
		varlist_origin[x] = []
	for each in varlist_temp:
		varlist_origin[each[1]].append(each[0])
	return varlist_origin, varlist_temp

def insert_phi_func(graph, irs, df_list, varlist_origin, var_tuple):
	#dict def_sites = {'var':set of nodes}
	#var_phi = {node_num:variable}
	#varlist_origin = {node num: var} 
	def_sites = {}
	var_phi = {}
	phi_func = {}
	for var, node in var_tuple:
		if var not in def_sites:
			def_sites[var] = {node}
			var_phi[var] = set()
		else:
			def_sites[var].update({node})
	for n in range(len(df_list)):
		phi_func[n] = set()
	for var in def_sites:
		temp_list = list(def_sites[var])
		while len(temp_list)!=0:
			n = temp_list.pop()
			for y in df_list[n]:
				if y not in var_phi[var]:
					#insert the phi function with as many parameters as the pred of y in b node y
					phi_func[y].update({(var, len(list(filter(lambda x: x[1]==y,graph))))})
					#it denotes in which node is the phi_func to be inserted and of which variable
					var_phi[var].update({y})
					if y not in varlist_origin[n]:
						temp_list.append(y)
	return def_sites, var_phi, phi_func

def rename(irs, leader_set, graph, dom_tree, phi_func):
	var_list = [re.match('(.*)=.* ',s).group(1).strip() for s in irs if re.match('(.*)=.* ',s)]
	var_list = list(filter(lambda x: 'if' not in x, var_list))
	var_dict = {}
	#var_dict[variable] -> count, stack
	for var in var_list:
		var_dict[var] = [0,[0]] 
	phi_func_mod = {}
	phi_func_temp = {}
	for each in phi_func:
		if each not in phi_func_temp:
			phi_func_temp[each] = []
			phi_func_mod[each] = []
		for t in phi_func[each]:
			phi_func_temp[each].append([t[0] for m in range(t[1])])

	leader_set.append(('',len(irs)))
	blocks = [((leader_set[x][1], leader_set[x+1][1]),x) for x in range(len(leader_set[:-1]))]

	def rename_block(block):
		block_line_nums, block_num = block[0], block[1]
		block_lines = irs[block_line_nums[0]:block_line_nums[1]]
		#if a phi func in the block
		for each in phi_func[block_num]:
			#inc count
			var_dict[each[0]][0] = var_dict[each[0]][0] + 1
			#add it to the stack
			var_dict[each[0]][1].append(var_dict[each[0]][0])
			add = (each[0].replace(each[0], each[0]+'('+str(var_dict[each[0]][0])+')'))
			n_each = list(each)
			n_each.append(add)
			phi_func_mod[block_num].append(n_each)
		#cases where there are no phi functions
		for count, each_line in enumerate(block_lines):
			def_var = []
			var_use = []
			#find all defs in each line
			if re.match('(.*)=.* ',each_line):
				def_var = [re.match('(.*)=.* ', each_line).group(1).strip()]
				def_var = list(filter(lambda x: 'if' not in x, def_var))
			for each_var in def_var:
				#count++
				var_dict[each_var][0] = var_dict[each_var][0] + 1
				var_dict[each_var][1].append(var_dict[each_var][0])
				#replace defn of each_var with var_dict[each_var][0]
				if not re.match('(.*)\((.*)',each_line):
					each_line = each_line.replace(each_var, each_var+'('+str(var_dict[each_var][0])+')')
				irs[block_line_nums[0]+count] = each_line

			var_loc = False
			#find all uses in each line
			if re.match('(.*)=(.*)',each_line):
				var_loc = re.match('(.*)=(.*)',each_line)
			elif re.match('(.*)<(.*)',each_line):
				var_loc = re.match('(.*)<(.*)',each_line)
			elif re.match('(.*)>(.*)',each_line):
				var_loc = re.match('(.*)>(.*)',each_line)

			if var_loc:
				var_use_lhs = var_loc.group(1)
				if 'if' in var_use_lhs:
					var_use_lhs = re.findall('[a-zA-Z]+[0-9]*', var_use_lhs)
					var_use_lhs = [x for x in var_use_lhs if 'if' not in x] 
				else:
					var_use_lhs =[]
				var_use_rhs = var_loc.group(2)
				var_use_rhs = re.findall('[a-zA-Z]+[0-9]*',var_use_rhs)
				var_use_rhs = [x for x in var_use_rhs if 'loop' not in x]
				var_use_rhs = [x for x in var_use_rhs if 'if' not in x]
				var_use_rhs = [x for x in var_use_rhs if 'goto' not in x]
				var_use = var_use_lhs + var_use_rhs

			for each_use in var_use:
				#replace the use of each_use with var_dict[each_var][1][-1] i.e top of the stack
				if each_use not in var_dict:
					var_dict[each_use] = [0,[0]]
				if re.match('(.*)\((.*)',each_line):
					pass
				else:
					each_line = each_line.replace(each_use, each_use+'('+str(var_dict[each_use][1][-1])+')')
				irs[block_line_nums[0]+count] = each_line

		for succ in [x[1] for x in filter(lambda x: x[0]==block_num,graph)]:
			pred = [x[0] for x in list(filter(lambda x: x[1]==succ,graph))]
			# n is the jth predecessor of the successor
			j = pred.index(block_num)
			for func in phi_func_temp[block_num]:
				a = func[j]
				if re.match('(.*)\((.*)',a):
					a = re.match('(.*)\((.*)',a).group(1)
				else:
					func[j] = func[j]+'('+str(var_dict[a][1][-1])+')'
				#replaced variable

		child = [x[1] for x in list(filter(lambda x: x[0]==block_num,dom_tree))]
		list(map(lambda each_child: rename_block(blocks[each_child]), child))

		for each_line in block_lines:
			if re.match('(.*)\((.*)=.* ', each_line):
				def_var_temp = re.match('(.*)\((.*)=.* ', each_line).group(1).strip()
				if 'if' not in def_var_temp:
					var_dict[def_var_temp][1].pop()
			elif re.match('(.*)=.* ',each_line):
				def_var_temp = re.match('(.*)=.* ', each_line).group(1).strip()
				if 'if' not in def_var_temp:
					var_dict[def_var_temp][1].pop()

	rename_block(blocks[0])

def main():
	file = open("input.txt")
	leader_set, irs = find_leaders(file.read())
	file.close()
	graph = create_cfg(leader_set, irs)
	dom_tree, dom_set = create_domtree(graph, len(leader_set))
	df_list = find_domfrontier(dom_tree, graph, dom_set)
	varlist_origin, var_tuple = find_var_origin(irs, leader_set)
	def_sites, var_phi, phi_func = insert_phi_func(graph, irs, df_list, varlist_origin, var_tuple)
	
	rename(irs, leader_set, graph, dom_tree, phi_func)
	block_lines = irs[:]
	fout = open('output.txt','w')
	for each_line in block_lines:
		fout.write(each_line+'\n')
	fout.close()
	
if __name__ == '__main__':
	main()