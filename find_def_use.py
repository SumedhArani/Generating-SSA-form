		'''
		Finds var_defs and var_uses in the whole block
		which is meaningless
		def_var = [re.match('(.*)=.* ',s).group(1).strip() for s in block_lines if re.match('(.*)=.* ',s)]
		def_var = list(filter(lambda x: 'if' not in x, def_var))
		var_loc = [re.match('(.*)=(.*)',s) for s in block_lines if re.match('(.*)=.* ',s)]
		var_use_lhs = [x.group(1) for x in var_loc]
		var_use_lhs = filter(lambda x: 'if' in x, var_use_lhs)
		var_use_lhs = [re.findall('[a-zA-Z]+[0-9]',x) for x in var_use_lhs]
		var_use_lhs = [x for y in var_use_lhs for x in y]
		var_use_rhs = [x.group(2) for x in var_loc]
		var_use_rhs = [re.findall('[a-zA-Z]+[0-9]',x) for x in var_use_rhs]
		var_use_rhs = [x for y in var_use_rhs for x in y ]
		var_use_rhs = [x for x in var_use_rhs if 'loop' not in x]
		var_use_rhs = [x for x in var_use_rhs if 'if' not in x]
		var_use = var_use_lhs + var_use_rhs
		print(var_use)
		'''


#find all uses in each line
			if re.match('(.*)=(.*)',each_line):
				var_loc = re.match('(.*)=(.*)',each_line)
			elif re.match('(.*)<(.*)',each_line):
				var_loc = re.match('(.*)<(.*)',each_line)
			elif re.match('(.*)>(.*)',each_line):
				var_loc = re.match('(.*)>(.*)',each_line)