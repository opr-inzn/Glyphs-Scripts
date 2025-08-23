# MenuTitle: Add Duplicate Node on Top

for i in range(len(Layer.paths)-1,-1,-1):
	p = Layer.paths[i]
	for j in range(len(p.nodes)-1,-1,-1):
		n = p.nodes[j]
		if n.selected and n.type!=GSOFFCURVE:
			p.insertNode_atIndex_(GSNode(n.position),j+1)