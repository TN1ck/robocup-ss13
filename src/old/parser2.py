#!/usr/bin/env python2.7

import string

def pars(expr):
	tmpStr = ""
	found = 0
	expArgs = 0
	key = ""
	valuelist = []
	valuedict = {}
	complete = {}
	focuson = False

	for x in expr:
		if x == "(":
			if expArgs == 0: #except key
				tmpk = tmpStr.split() # cut whitespaces
				if len(tmpk) > 0:
					key = tmpk[0]
				tmpStr = ""
				if key == "time":
					expArgs = 1
					focuson = True
				elif key == "GS":
					focuson = True
					expArgs = 2
				elif key == "GYR":
					focuson = True
					expArgs = 2
				elif key == "ACC":
					focuson = True
					expArgs = 2
				elif key == "HJ":
					focuson = True
					expArgs = 2
				elif key == "FRP":
					focuson = True
					expArgs = 3
			found += 1

		elif x == ")":
			if focuson:
				if expArgs > 0: #end of value
					tmpl = tmpStr.split()
					tmpv = (tmpl[0],tmpl[1]) #make a key-value-pair for each parameter
					valuelist.append(tmpv)
					tmpStr = ""
					expArgs -= 1
				if expArgs == 0: #got all values for key
					if found > 0:
						valuedict = dict(valuelist) #creates a dictionary of the values
						complete[key] = valuedict #map it with key
						key = ""
						focuson = False
			found -= 1
			tmpStr = ""

		elif found > 0: #something else
				tmpStr += x

	if found != 0:
		return {}
	else:
		return complete

if __name__ == '__main__':
	sexp = '(spam 1 2 3)'
	print(pars(sexp))
