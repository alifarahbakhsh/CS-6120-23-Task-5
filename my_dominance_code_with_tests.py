import json
import sys
import copy

def get_basic_blocks(_code):
	"""
	Returns a dictionary of blocks, separated by the function name.
	Each block is a dictionary itself, with keys "instrs" and "successors".
	The "succesors" key will be used when constructing the cfg.
	"""
	blocks = dict()
	for func in _code["functions"]:
		blocks[func["name"]] = {}
		new_block = {"instrs": [], "predecessors": [], "successors": [], "dominators": []}
		fun_len = len(func["instrs"]) - 1
		unnamed_blocks_cntr = 0
		cur_label = ""
		for instr_idx, instr in enumerate(func["instrs"]):
			if "label" in instr:
				if not new_block["instrs"] == []:
					to_append = new_block.copy()
					if cur_label == "":
						### Name the entry block as "entry", not "b0". If not the entry,
						### use the convention and name it bn for the right n.
						if unnamed_blocks_cntr == 0:
							cur_label = "entry"
						else:
							cur_label = "b" + str(unnamed_blocks_cntr)
							unnamed_blocks_cntr += 1
					blocks[func["name"]][cur_label] = to_append
				new_block = {"instrs": [], "predecessors": [], "successors": [], "dominators": []}
				new_block["instrs"] = [instr]
				cur_label = instr["label"]
				continue
			new_block["instrs"].append(instr)
			if is_breaking_block(instr):
				if cur_label == "":
					### Name the entry block as "entry", not "b0". If not the entry,
					### use the convention and name it bn for the right n.
					if unnamed_blocks_cntr == 0:
						cur_label = "entry"
					else:
						cur_label = "b" + str(unnamed_blocks_cntr)
						unnamed_blocks_cntr += 1
				to_append2 = new_block.copy()
				blocks[func["name"]][cur_label] = to_append2
				new_block = {"instrs": [], "predecessors": [], "successors": [], "dominators": []}
				continue
			if instr_idx == fun_len:
				if cur_label == "":
					### Name the entry block as "entry", not "b0". If not the entry,
					### use the convention and name it bn for the right n.
					if unnamed_blocks_cntr == 0:
						cur_label = "entry"
					else:
						cur_label = "b" + str(unnamed_blocks_cntr)
						unnamed_blocks_cntr += 1
				to_append3 = new_block.copy()
				blocks[func["name"]][cur_label] = to_append3
				new_block = {"instrs": [], "predecessors": [], "successors": [], "dominators": []}
				continue
		if not new_block["instrs"] == []:
			to_append4 = new_block.copy()
			blocks[func["name"]][cur_label] = to_append4
	return blocks

def is_breaking_block(_instr):
	is_breaking = False
	if _instr["op"] == "jmp" or _instr["op"] == "br" or _instr["op"] == "ret":
		is_breaking = True
	return is_breaking

def get_cfg(_blocks):
	for _, func in enumerate(_blocks):
		for block_idx, block in enumerate(_blocks[func]):
			#print(block)
			if "op" in _blocks[func][block]["instrs"][-1]:
				if _blocks[func][block]["instrs"][-1]["op"] == "jmp" or _blocks[func][block]["instrs"][-1]["op"] == "br":
					_blocks[func][block]["successors"] = _blocks[func][block]["instrs"][-1]["labels"]
					for label in _blocks[func][block]["instrs"][-1]["labels"]:
						_blocks[func][label]["predecessors"].append(block)
				else:
					if block_idx < len(_blocks[func]) - 1:
						temp = list(_blocks[func].keys())
						_blocks[func][block]["successors"].append(temp[block_idx + 1])
						_blocks[func][temp[block_idx + 1]]["predecessors"].append(block)
	return _blocks

def print_cfg(_cfg):
	for func in _cfg:
		for block in _cfg[func]:
			print(block)
			print(_cfg[func][block]["predecessors"])
			print(_cfg[func][block]["successors"])

def get_dominators(_cfg):
    dominators = dict()
    dominatees = dict()
    for _, func in enumerate(_cfg):
        ### Initialize the dominators set.
        dominators[func] = dict()
        dominatees[func] = dict()
        block_names = list(_cfg[func].keys())
        for name in block_names:
            if name == "entry":
                dominators[func][name] = ["entry"]
                dominatees[func][name] = ["entry"]
            else:
                dominators[func][name] = block_names
                dominatees[func][name] = []

        has_changed = True
        while has_changed:
            #print("going again")
            has_changed = False
            for _, block in enumerate(dominators[func]):
                if block == "entry":
                    continue
                res = intersection(block, _cfg[func][block]["predecessors"], dominators[func])
                #print(f"block is {block}, res is {res}, doms are {dominators[func][block]}")
                if not res == dominators[func][block]:
                    has_changed = True
                dominators[func][block] = res
        for _, block in enumerate(dominators[func]):
            for dom in dominators[func][block]:
                #print(f"dom is {dom}, block is {block}, res is {res}")
                dominatees[func][dom].append(block)
    return dominators, dominatees



def intersection(_block, _preds, _dominators):
	res = list(_dominators.keys())
	for pred in _preds:
		res = list(set(_dominators[pred]) & set(res))
	if not _block in res:
		res.append(_block)
	return res


def eliminate_back_edges(_dominators, _cfg):
	for _, func in enumerate(_cfg):
		for _, block in enumerate(_cfg[func]):
			for succ in _cfg[func][block]["successors"]:
				if succ in _dominators[func][block]:
					_cfg[func][block]["successors"].remove(succ)
					_cfg[func][succ]["predecessors"].remove(block)
	return _cfg

def get_paths(_cfg):
    paths = dict()
    for _, func in enumerate(_cfg):
        ### Initialize the paths.
        paths[func] = dict()
        block_names = list(_cfg[func].keys())
        for name in block_names:
            if name == "entry":
                paths[func][name] = [["entry"]]
            else:
                paths[func][name] = []
        #print(f"paths is {paths}")		
        for name in block_names:
            paths = recurse(name, func, paths, _cfg)
    return paths

def recurse(_block, _func, _paths, _cfg):
	if _block == "entry":
		return _paths
	res = []
	for pred in _cfg[_func][_block]["predecessors"]:
		if _paths[_func][pred] == []:
			_paths = recurse(pred, _func, _paths, _cfg)
		paths_copy = copy.deepcopy(_paths)
		temp = paths_copy[_func][pred].copy()
		for idx in range(len(temp)):
			temp[idx].append(_block)
		res = union(res, temp)
		_paths[_func][_block] = res
	return _paths

def union(a, b):
	res = a
	for val in b:
		if not b in res:
			res.append(val)
	return res

def verify_dominators(_dominators, _paths):
    for _, func in enumerate(_dominators):
        for _, block in enumerate(_dominators[func]):
            is_correct = True
            if block == "entry":
                if not _paths[func][block] == [["entry"]]:
                    is_correct = False
            else:
                for dom in _dominators[func][block]:
                    for path in _paths[func][block]:
                        if not dom in path:
                            print(f"Verification - dom is {dom}, block is {block}, path is {path}")
                            is_correct = False
            if is_correct == False:
                return False
    return True

def get_dominance_tree(_dominators, _dominatees):
	tree = dict()
	for _, func in enumerate(_dominators):
		tree[func] = dict()
		for name in list(_dominatees[func].keys()):
			tree[func][name] = {"parent": [], "children": []}
		for _, block in enumerate(_dominatees[func]):
			#tree[func][block] = {"parent": [], "children": []}
			for dom in _dominatees[func][block]:
				if dom == block:
					continue
				is_immediate = True
				for dom2 in _dominatees[func][block]:
					if dom2 in dominators[func][dom] and (not dom2 == dom) and (not dom2 == block):
						is_immediate = False
				if is_immediate:
					tree[func][block]["children"].append(dom)
					tree[func][dom]["parent"].append(block)
	return tree

def verify_dominance_tree(_tree, _dominators):
	for _, func in enumerate(_tree):
		for _, block in enumerate(_tree[func]):
			is_correct = True
			for child in _tree[func][block]["children"]:
				if not block in _dominators[func][child]:
					is_correct = False
	return is_correct

def get_dominance_frontier(_dominatees, _cfg):
    frontier = dict()
    for _, func in enumerate(_dominatees):
        frontier[func] = dict()
        for _, block in enumerate(_dominatees[func]):
            frontier[func][block] = []
            for domee in _dominatees[func][block]:
                for succ in _cfg[func][domee]["successors"]:
                    if not succ in _dominatees[func][block]:
                        frontier[func][block].append(succ)
    return frontier
			
				

if __name__ == "__main__":
    code = json.load(sys.stdin)
    blocks = get_basic_blocks(code)
    cfg = get_cfg(blocks)
    #print("The CFG:")
    #print_cfg(cfg)
    dominators, dominatees = get_dominators(cfg)
    #print("The dominators:")
    #print(dominators)
    #print("The dominatees:")
    #print(dominatees)
    dom_tree = get_dominance_tree(dominators, dominatees)
    #print("The dominance tree:")
    #print(dom_tree)
    cfg_removed_backedges = eliminate_back_edges(dominators, cfg)
    #print_cfg(cfg_removed_backedges)
    paths = get_paths(cfg_removed_backedges)
    #print("The paths:")
    #print(paths)
    frontier = get_dominance_frontier(dominatees, cfg)
    #print("The frontier:")
    #print(frontier)
    print(verify_dominators(dominators, paths))
    print(verify_dominance_tree(dom_tree, dominators))
	
