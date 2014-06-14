#!/usr/bin/python

import re, os
# input files

# read simple substitutions from a comma-delimited, quote-embraced CSV file
def SubstitutionsFromCSV(path):
	list = []
	csv = open(path, 'r')
	for line in csv:
		lineparts = re.findall('(".+?")?,?', line)
		lineparts = map(unquote, lineparts)
		lineparts = lineparts[0:7]
		if lineparts[0] and lineparts[1] and lineparts[2]: # first three fields (feature, source and target) are required
			list.append(lineparts)
	csv.close()

	return list



def GlyphNamesFromFontLabFont(f):
	list = []
	for g in f.glyphs:
		list.append(g.name)
	return list

def GlyphNamesFromGlyphsFont(f):
	list = []
	for g in f.glyphs:
		list.append(g.name)
	return list

def GlyphNamesFromRoboFabFont(f):
	list = []
	for g in f:
		list.append(g.name)
	return list


def AssignFeatureCodeToFontLabFont(f, shoes):
	try:
		import FL
	
		f.features.clean() # clean all previous features first
		for feature in shoes.UsedFeatures():
			f.features.append(FL.Feature(feature, shoes.GetFDKFeatureCode(feature)))
		f.ot_classes = shoes.GetFDKClassesCode() + shoes.GetFDKLanguageSystemCode()
		f.modified = 1
		FL.fl.UpdateFont()
	except:
		shoes.Error("You're not within FontLab.")

def AssignFeatureCodeToGlyphsFont(f, shoes):
	
	from GlyphsApp import NewClass, NewFeature
	
	while len(f.classes) > 0:
		del(f.classes[0])
	
	while len(f.features) > 0:
		del(f.features[0])

	for feature in shoes.UsedFeatures():
		Feature = NewFeature()
		Feature.name = feature
		Feature.automatic = False # The Feature will not be removed on the next autogenerate run.
		Feature.code = shoes.GetFDKFeatureContent(feature)
		f.features.append(Feature)

	for otclass in shoes.UsedClasses():
		newClass = NewClass(otclass)
		newClass.name = otclass
		newClass.code = ' '.join(shoes.GlyphsInClass(otclass))
		newClass.automatic = False # The Class will not be removed on the next autogenerate run.
		f.classes.append(newClass)


def AssignFeatureCodeToRoboFabFont(f, shoes):
	f.features.text = shoes.GetFDKCode()
	
def unquote(string):
	regex = re.search('"(.+)"', string)
	if regex:
		if not regex.group(1).startswith('#'): # cancel out comments
			return regex.group(1)
		else:
			return ''
	else: return ''

