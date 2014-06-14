#FLM: Dancing Shoes in FontLab
# -*- coding: cp1252 -*-

from dancingshoes import DancingShoes
from dancingshoes.helpers import GlyphNamesFromFontLabFont, SubstitutionsFromCSV
import string

f = fl.font

# Your features, in the order you want them in the font
features = ('aalt', 'locl', 'numr', 'dnom', 'frac', 'tnum', 'smcp', 'case', 'calt', 'liga', 'ss01', 'ss02', 'ss03')

# Initialize DancingShoes object, hand over glyph names and default features
shoes = DancingShoes(GlyphNamesFromFontLabFont(f), features)

# Add direct substitutions
directsubstitutions = (
	('smcp', '.sc'),
	('case', '.case'),
	('tnum', '.tf'),
	('ss01', '.ss01'),
	('ss02', '.ss02'),
	('ss03', '.ss03'),
	)
for feature, ending in directsubstitutions:
	shoes.AddSimpleSubstitutionFeature(feature, ending)

# Simple Substitutions from CSV file
csv = '/Users/yanone/Desktop/substitutions.csv'
for feature, source, target, script, language, lookupflag, comment in SubstitutionsFromCSV(csv):
	shoes.AddSubstitution(feature, source, target, script, language, lookupflag, comment)

# Fraction feature
if shoes.HasGroups(['.numr', '.dnom']) and shoes.HasGlyphs(['fraction']):
	shoes.AddSimpleSubstitutionFeature('numr', '.numr')
	shoes.AddSimpleSubstitutionFeature('dnom', '.dnom')

	# Add your personal contextual substitution fractions magic here with
	# shoes.AddGlyphsToClass() and
	# shoes.AddSubstitution()


# You can write contextual code for your script fonts using your own glyph name endings
if shoes.HasGroups(['.initial', '.final']):
	# Add contextual substitution magic here
	for target in shoes.GlyphsInGroup('.initial'):
		shoes.AddGlyphsToClass('@initialcontext', ('a', 'b', 'c'))
		shoes.AddSubstitution('calt', "@initialcontext %s'" % (shoes.SourceGlyphFromTarget(target)), target)

# You can theoretically write your own kern feature (which FontLab can also do for you upon font generation):
shoes.AddPairPositioning('kern', 'T A', -30)
shoes.AddPairPositioning('kern', 'uniFEAD uniFEEB', (-30, 0, -60, 0), 'arab', '', 'RightToLeft')


# Output code to FontLab
# Clean previous features of FontLab file
fl.output = ''

# Add all previously generated features to aalt-feature.
for feature in shoes.UsedFeatures():
	shoes.AddFeatureLookup('aalt', feature)

# Assign feature code back to FontLab's features list
from dancingshoes.helpers import AssignFeatureCodeToFontLabFont
AssignFeatureCodeToFontLabFont(f, shoes)


# Verbose output
if shoes.Infos():
	print shoes.Infos()
if shoes.Warnings():
	print shoes.Warnings()
if shoes.Errors():
	print shoes.Errors()
