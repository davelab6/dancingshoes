#!/usr/bin/python

"""

Dancing Shoes

Dancing Shoes is a Python library that provides
a friendly interface to create OpenType feature code
using simple instructions.

DEVELOPERS
Yanone

MORE INFO (AND DOCUMENTATION)
http://www.yanone.de/typedesign/code/dancingshoes/

LICENSE
Copyright (c) 2009, Yanone
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of the RoboFab Developers nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

import string, os, re, copy
import dancingshoes.opentypenames

__all__ = ['opentypenames', 'helpers']
__version__ = '0.1.3'




# Main class

class DancingShoes:
	def __init__(self, glyphnames, features):
		self.glyphnames = glyphnames # List of glyph names
		self.features = features # List four-digit feature name codes, in order preferred by the foundry/designer
		self.lookups = [] # List of OpenType lookups. This is the main list and will be filled later
		self.glyphgroups = CollectGlyphGroups(self.glyphnames) # Dict of groups. glyphgroups['.tosf'] = ['one.tosf', 'two.tosf', 'three.tosf' ...]
		self.classes = Ddict(dict) # Two dimensional array of classes.
		
		self.infos = []
		self.warnings = []
		self.errors = []

	def Info(self, string):
		self.infos.append(string)

	def Infos(self):
		if self.infos:
			return 'INFORMATIONS:\n' + '\n'.join(self.infos)
		else:
			return None

	def Warning(self, string):
		self.warnings.append(string)

	def Warnings(self):
		if self.warnings:
			return 'WARNINGS:\n' + '\n'.join(self.warnings)
		else:
			return None

	def Error(self, string):
		self.errors.append(string)

	def Errors(self):
		if self.errors:
			return 'ERRORS:\n' + '\n'.join(self.errors)
		else:
			return None


	def Glyphs(self):
		'''
		Returns self.glyphnames
		'''
		return self.glyphnames


	def HasGlyphs(self, glyphslist):
		'''
		Check, if a list of glyphnames is present in the collection of glyphnames of this object.
		Return True, if all submitted glyphs are present.
		'''
		if isinstance(glyphslist, str):
			if glyphslist in self.glyphnames:
				return True
				
		elif isinstance(glyphslist, list) or isinstance(glyphslist, tuple):

#			from sets import Set
#			if len(glyphslist) == len( list(Set(glyphslist) & Set(self.glyphnames)) ):
#				return True
#			else:
#				return False

			present = 0
			for glyph in glyphslist:
				if glyph in self.glyphnames:
#				if InList(self.glyphnames, glyph):
					present += 1

			if present == len(glyphslist):
				return True
			else:
				return False

	def Groups(self):
		'''
		Returns self.glyphgroups.keys()
		'''
		return self.glyphgroups.keys()


	def HasGroups(self, groupslist):
		'''
		Check, if a list of glyphnames is present in the collection of glyphnames of this object.
		Return True, if all submitted glyphs are present.
		'''
		if isinstance(groupslist, str):
			if groupslist in self.Groups():
				return True

		elif isinstance(groupslist, list) or isinstance(groupslist, tuple):
			present = 0
			for group in groupslist:
				if group in self.Groups():
					present += 1
			if present == len(groupslist):
				return True
			else:
				return False
		else:
			return False


	def HasClasses(self, classnames):
		
		if isinstance(classnames, str):
			if self.classes.has_key(classnames):
				return True

		elif isinstance(classnames, list) or isinstance(classnames, tuple):

			present = 0
			for classname in classnames:
				if self.classes.has_key(classname):
					present += 1
			
			if present == len(classnames):
				return True
			else:
				return False
		else:
			return False



	def GlyphsInGroup(self, ending):
		'''
		Returns self.glyphgroups[ending]
		'''
		if ending in self.Groups():
			return self.glyphgroups[ending]
		else:
			return []


	def GroupHasGlyphs(self, ending, glyphslist):
		'''
		Returns True if all glyphs are present in group
		'''
		if ending in self.Groups():

			if isinstance(glyphslist, str):
				if glyphslist in self.GlyphsInGroup(ending):
					return True

			elif isinstance(glyphslist, list) or isinstance(glyphslist, tuple):
				present = 0
				for glyph in glyphslist:
					if glyph in self.GlyphsInGroup(ending):
						present += 1
				if present == len(glyphslist):
					return True
				else:
					return False
		else:
			return False




	def SourceGlyphFromTarget(self, target):
		return os.path.splitext(target)[0]


	def UsedFeatures(self):
		'''
		Returns list of all four-digit feature code names that have been successfully registered so far.
		'''
		list = []
		for feature in self.features:
			for lookup in self.lookups:
				if feature == lookup.feature and not lookup.feature in list:
					list.append(lookup.feature)
		return list


	def UsedClasses(self):
		'''
		Returns list of all classes that have been successfully registered so far.
		'''
		return self.classes.keys()


	def UsedScripts(self, feature, includedefault = True, includeforeign = True):
		'''
		Returns list of all scripts that have been registered for given feature.
		"includedefault" and "includeforeign" are switches to distinguish between lookups that have
		been registered for a specific script/language or for all default scripts/languages(Used for the FDK version switch).
		'''
		list = []
		for lookup in self.lookups:
			if feature == lookup.feature and not lookup.script in list:
				if includedefault and lookup.script == '__DEFAULT__':
					list.append(lookup.script)
				if includeforeign and lookup.script != '__DEFAULT__':
					list.append(lookup.script)
		return list


	def UsedLanguages(self, feature, script, includedefault = True, includeforeign = True):
		'''	Returns list of all languages that have been registered for given feature and script.
		"includedefault" and "includeforeign" are switches to distinguish between lookups that have
		been registered for a specific script/language or for all default scripts/languages(Used for the FDK version switch).
		'''
		list = []
		for lookup in self.lookups:
			if feature == lookup.feature and script == lookup.script and not lookup.language in list:
				if includedefault and lookup.language == '__DEFAULT__':
					list.append(lookup.language)
				if includeforeign and lookup.language != '__DEFAULT__':
					list.append(lookup.language)
		return list


	def UsedLookUpFlags(self, feature, script, language):
		'''	Returns list of all lookupflags that have been registered for given feature and script and language.
		'''
		list = {}
		for lookup in self.lookups:
			if feature == lookup.feature and script == lookup.script and language == lookup.language:
				list[lookup.lookupflag] = 'used'
		return list.keys()


	def UsedLookups(self, feature, script, language, lookupflag):
		'''
		Returns list of all lookups that have been registered for given feature and script and language.
		'''
		list = []
		for lookup in self.lookups:
			if language == lookup.language and feature == lookup.feature and script == lookup.script and lookupflag == lookup.lookupflag:
				list.append(lookup)
		return list


	def UsedScriptsAndLanguages(self):
		'''
		Returns list of tuples of all script/language combinations that have been registered.
		'''
		list = []
		for lookup in self.lookups:
			if not (lookup.script, lookup.language) in list:
				list.append((lookup.script, lookup.language))

		# Add dflt/dflt and ltn/dflt
		if not ('__DEFAULT__', '__DEFAULT__') in list:
			list.append(('__DEFAULT__', '__DEFAULT__'))
		if not ('latn', '__DEFAULT__') in list:
			list.append(('latn', '__DEFAULT__'))

		return list


	## Add lookups

	def AddFeatureLookup(self, feature, lookupfeature, script = '', language = '', lookupflag = '', comment = ''):

		# Check if feature is present in main feature list
		if not feature in self.features:
			self.Warning('Attempting to add feature lookup to feature "%s", but the feature is not present in your features list' % (feature))

		if not lookupfeature in self.UsedFeatures():
			self.Info('Attempting to add feature "%s" lookup to feature "%s", but the feature is not in use (yet)' % (lookupfeature, feature))

		if not script:
			script = '__DEFAULT__'
		if not language:
			language = '__DEFAULT__'
		if not lookupflag:
			lookupflag = '__DEFAULT__'
		self.lookups.append(FeatureLookup(feature, script, language, lookupflag, lookupfeature, comment))


	def AddSimpleSubstitutionFeature(self, feature, ending):

		# Check if feature is present in main feature list
		if not feature in self.features:
			self.Warning('Attempting to add simple substitutions to feature "%s", but the feature is not present in your supplied features list' % (feature))

		if self.HasGroups([ending]):
			self.AddEndingToBothClasses(feature, ending)
			self.AddSubstitution(feature, '@' + feature + '_source', '@' + feature + '_target')
		else:
			self.Info('Attempting to add simple substitution feature "%s", but group "%s" is missing in your glyph repertoire.' % (feature, ending))

	def AddSubstitution(self, feature, source, target, script = '', language = '', lookupflag = '', comment = ''):

		# Check if feature is present in main feature list
		if not feature in self.features:
			self.Warning('Attempting to add substitution to feature "%s", but the feature is not present in your supplied features list' % (feature))

		if not script:
			script = '__DEFAULT__'
		if not language:
			language = '__DEFAULT__'
		if not lookupflag:
			lookupflag = '__DEFAULT__'


		# source and target sequence code is checked for presence
		if self.HasGlyphs(self.DeflateClassString(source)) and self.HasGlyphs(self.DeflateClassString(target)):
			self.lookups.append(GSUBLookup(feature, source, target, script, language, lookupflag, comment))
		else:
			self.Info('Attempting to add substitution glyph sequence to feature "%s", but glyphs from either the source ("%s") or the target ("%s") are missing in your glyph repertoire.' % (feature, source, target))
			

	#def AddDuplicateFeature(self, sourcefeature, targetfeature):
	#	self.AddFeatureLookup(targetfeature, '', '', '', sourcefeature, '')



	def AddSinglePositioning(self, feature, glyph, adjustment, script = '', language = '', lookupflag = '', comment = ''):

		if not script:
			script = '__DEFAULT__'
		if not language:
			language = '__DEFAULT__'
		if not lookupflag:
			lookupflag = '__DEFAULT__'
		
		# Check if feature is present in main feature list
		if not feature in self.features:
			self.Warning('Attempting to add single positioning lookup to feature "%s", but the feature is not present in your supplied features list' % (feature))

		if isinstance(adjustment, int) or isinstance(adjustment, str):
			adjustment = (int(adjustment), 0, 0, 0)
	
		if self.HasGlyphs(self.DeflateClassString(glyph)):
			self.lookups.append(GPOSLookupType1(feature, glyph, adjustment, script, language, lookupflag, comment))


	def AddPairPositioning(self, feature, pair, adjustment, script = '', language = '', lookupflag = '', comment = ''):

		if not script:
			script = '__DEFAULT__'
		if not language:
			language = '__DEFAULT__'
		if not lookupflag:
			lookupflag = '__DEFAULT__'

		# Check if feature is present in main feature list
		if not feature in self.features:
			self.Warning('Attempting to add pair positioning lookup to feature "%s", but the feature is not present in your supplied features list' % (feature))

		if isinstance(adjustment, int) or isinstance(adjustment, str):
			adjustment = (int(adjustment), 0, 0, 0)
	
		if self.HasGlyphs(self.DeflateClassString(pair)):
			self.lookups.append(GPOSLookupType2(feature, pair, adjustment, script, language, lookupflag, comment))


	## Classes

	def AddGlyphsToClass(self, classname, glyphnames):
		# init dict
		
#		if classname == '@ordn_source' and glyphnames == 'n':
#			print 'jetzt'
		
		if not classname.startswith('@'):
			classname = '@' + classname
		if not self.classes.has_key(classname):
#		if self.HasGlyphs(glyphnames) and not self.classes.has_key(classname):
			self.classes[classname] = []


		if isinstance(glyphnames, str):
			if self.HasGlyphs([glyphnames]):
				self.classes[classname].append(glyphnames)
		elif isinstance(glyphnames, tuple) or isinstance(glyphnames, list):
			for glyphname in glyphnames:
				if self.HasGlyphs([glyphname]):
					self.classes[classname].append(glyphname)


	def AddEndingToBothClasses(self, feature, ending):
		if ending in self.Groups():
			for glyph in self.GlyphsInGroup(ending):
				if self.HasGlyphs([glyph, self.SourceGlyphFromTarget(glyph)]):
					self.AddGlyphsToClass(feature + '_source', [self.SourceGlyphFromTarget(glyph)] )
					self.AddGlyphsToClass(feature + '_target', [glyph])

	def DuplicateFeature(self, source, target):
		
		# Check, if target feature is already in use
		if target in self.UsedFeatures():
			self.Warning("Duplicate feature '" + source + "' as '" + target + "'. The target feature '" + target + "' already contains some lookups. I appended the instructions of '" + source + "' to '" + target + "', but they should be completely separate.")

		newlookups = []
		for lookup in self.lookups:
			if lookup.feature == source:
				newlookup = copy.copy(lookup)
				newlookup.feature = target
				newlookups.append(newlookup)
		self.lookups.extend(newlookups)
		
				

	# NEW in 1.0.3, not yet documented
	def GlyphsInClass(self, classname):
		if self.classes.has_key(classname):
			return self.classes[classname]
		else:
			return None


	# NEW in 1.0.3, not yet documented
	def ClassHasGlyphs(self, classname, glyphnames):
		if self.classes.has_key(classname):
			if isinstance(glyphnames, str):
				if glyphnames in self.GlyphsInClass(classname):
					return True
			elif isinstance(glyphnames, tuple) or isinstance(glyphnames, list):
				present = 0
				for glyph in glyphnames:
					if glyph in self.GlyphsInClass(classname):
						present += 1
				if present == len(glyphnames):
					return True
				else:
					return False
		else:
			return False
		

	def DeflateClassString(self, string):
		'''
		Deflate string containing glyph names, groups or class names into a flat group of glyph names.
		[@fractionslashes @dnom_target] @numr_target'
		'''
		list = []
		string = string.replace("'", "")
		string = string.replace("[", "")
		string = string.replace("]", "")
		
		tokens = string.split(' ')
		
		for token in tokens:
			if token.startswith('@'): # is class, add members of class
				classname = token[1:]
				if self.classes.has_key(classname):
					list.extend(self.classes[classname])
			else:
				list.append(token)
		return list


	## Generate Feature Code

	def GetFDKCode(self, codeversion = None):
		'''
		Return feature code all in one string.
		Available codeversions so far:
		FDK2.3
		FDK2.5
		'''

		codeversion = GetFDKCodeVersion(codeversion)
		featurecode = []
	
		if codeversion == '2.3':
			defaultscript = 'dflt'
			defaultlanguage = 'dflt'
		elif codeversion == '2.5':
			defaultscript = 'DFLT'
			defaultlanguage = 'dflt'
	
		# Language System
		featurecode.append(self.GetFDKLanguageSystemCode(codeversion))


		# Classes
		featurecode.append(self.GetFDKClassesCode(codeversion))


		# Run through Features
		for feature in self.UsedFeatures():
			featurecode.append(self.GetFDKFeatureCode(feature, codeversion))


		return '\n'.join(featurecode)


	def GetFDKFeatureCode(self, feature, codeversion = None):
		'''
		Return feature code all in one string.
		Available codeversions so far:
		FDK2.3
		FDK2.5
		'''

		featurecode = []
	
		featurecode.append('feature %s {' % (feature))

		featurecode.append(self.GetFDKFeatureContent(feature, codeversion))

		featurecode.append('')
		featurecode.append('} %s;' % (feature))
		featurecode.append('')

		return '\n'.join(featurecode)


	def GetFDKFeatureContent(self, feature, codeversion = None):
		'''
		Return feature code all in one string.
		Available codeversions so far:
		FDK2.3
		FDK2.5
		'''

		codeversion = GetFDKCodeVersion(codeversion)
		featurecode = []
	
		if codeversion == '2.3':
			defaultscript = 'dflt'
			defaultlanguage = 'dflt'
		elif codeversion == '2.5':
			defaultscript = 'DFLT'
			defaultlanguage = 'dflt'


		featurecode.append('# %s' % (opentypenames.OTfeatures[feature]))
		featurecode.append('')

		# Default lookups
		
		usedscripts = self.UsedScripts(feature)
		usedlanguages = self.UsedLanguages(feature, '__DEFAULT__')
		usedlookupflags = self.UsedLookUpFlags(feature, '__DEFAULT__', '__DEFAULT__')

		# lookup has more than one script
		# put out dflt/dflt looklups directly here without script/language tags, if FDK version is 2.5
		if (codeversion == "2.3" and len(usedscripts) == 1 and usedscripts[0] == '__DEFAULT__' and len(usedlanguages) == 1 and usedlanguages[0] == '__DEFAULT__' and len(usedlookupflags) == 1 and usedlookupflags[0] == '__DEFAULT__') or codeversion != "2.3":
			featurecode.extend(FDKlookupcode(self.UsedLookups(feature, '__DEFAULT__', '__DEFAULT__', '__DEFAULT__'), 1))
			featurecode.append('')


		# put out all other scripts/languages, including dflt/dflt for 2.3	
		if ((len(usedscripts) == 1 and usedscripts[0] != '__DEFAULT__') or (len(usedlanguages) == 1 and usedlanguages[0] != '__DEFAULT__') or (len(usedlookupflags) == 1 and usedlookupflags[0] != '__DEFAULT__')) or (len(usedscripts) > 1 or len(usedlanguages) > 1 or len(usedlookupflags) > 1):

			# Script
			if codeversion == "2.3":
				usedscripts = self.UsedScripts(feature)
				usedscripts.sort(ScriptSort)
				lookupflagjoiner = ', '
			else:
				usedscripts = self.UsedScripts(feature, False, True)
				usedscripts.sort(ScriptSort)
				lookupflagjoiner = ' '
			
			for script in usedscripts:
				featurecode.append('  # %s' % (opentypenames.OTscripts[TranslateScript(script, defaultscript)]))
				featurecode.append('  script %s;' % (TranslateScript(script, defaultscript)))
	
				# Language
				usedlanguages = self.UsedLanguages(feature, script)
				usedlanguages.sort(LanguageSort)

				for language in usedlanguages:
					featurecode.append('    # %s' % (opentypenames.OTlanguages[TranslateLanguage(language, defaultlanguage)]))
					featurecode.append('    language %s;' % (TranslateLanguage(language, defaultlanguage)))
	
					# Lookups
					lookupflags = self.UsedLookUpFlags(feature, script, language)
					
					
					if len(lookupflags) == 1:
						if lookupflags[0] != '__DEFAULT__':
							featurecode.append('      lookupflag %s;' % (lookupflagjoiner.join(lookupflags[0].split(','))))
						featurecode.extend(FDKlookupcode(self.UsedLookups(feature, script, language, lookupflags[0]), 3))
					else:
						for i, lookupflag in enumerate(lookupflags):
							featurecode.append('')
							featurecode.append('      lookup %s_%s {' % (feature, i))
							if lookupflag != '__DEFAULT__':
								featurecode.append('        lookupflag %s;' % (lookupflagjoiner.join(lookupflag.split(','))))
							featurecode.extend(FDKlookupcode(self.UsedLookups(feature, script, language, lookupflag), 4))
							featurecode.append('      } %s_%s;' % (feature, i))
				featurecode.append('')


		return '\n'.join(featurecode)


	def GetFDKClassesCode(self, codeversion = None):
		'''
		Return classes code all in one string.
		'''

		codeversion = GetFDKCodeVersion(codeversion)
		featurecode = []
		
		if codeversion == '2.3':
			defaultscript = 'dflt'
			defaultlanguage = 'dflt'
		elif codeversion == '2.5':
			defaultscript = 'DFLT'
			defaultlanguage = 'dflt'
	

		# Classes

		classes = self.classes.keys()
		classes.sort()
		for classname in classes:
			if not classname.startswith('@'):
				classname = '@' + classname
			featurecode.append('%s = [' % (classname))
			featurecode.append('# ' + str(len(self.classes[classname])) + ' glyph(s)')
			featurecode.append(' '.join(self.classes[classname]))
			featurecode.append('];')
			featurecode.append('')


		featurecode.append('')
		return '\n'.join(featurecode) + '\n\n'


	def GetFDKLanguageSystemCode(self, codeversion = None):
		'''
		Return language system code all in one string.
		'''

		codeversion = GetFDKCodeVersion(codeversion)
		featurecode = []
		
		if codeversion == '2.3':
			defaultscript = 'dflt'
			defaultlanguage = 'dflt'
		elif codeversion == '2.5':
			defaultscript = 'DFLT'
			defaultlanguage = 'dflt'
	
		featurecode.append('# Dancing Shoes %s OpenType feature code generator by Yanone, Copyright 2009' % (__version__))
		featurecode.append('# Code generated for AFDKO version %s' % (codeversion))
		featurecode.append('')
		featurecode.append('')

		# Script, language systems		
		for script, language in self.UsedScriptsAndLanguages():
			featurecode.append('languagesystem %s %s; # %s, %s' % (TranslateScript(script, defaultscript), TranslateLanguage(language, defaultlanguage), opentypenames.OTscripts[TranslateScript(script, defaultscript)], opentypenames.OTlanguages[TranslateLanguage(language, defaultlanguage)]))

		featurecode.append('')
		featurecode.append('')

		featurecode.append('')
		return '\n'.join(featurecode) + '\n\n'



	
# Different Lookup types

# GSUB

class GSUBLookup:
	def __init__(self, feature, source, target, script, language, lookupflag, comment):
		self.type = 'GSUBLookup'
		self.lookupflag = lookupflag
		self.script = script
		self.language = language
		self.feature = feature
		self.source = source
		self.target = target
		self.comment = comment


class FeatureLookup: # AFDKO: feature smcp;
	def __init__(self, feature, script, language, lookupflag, lookupfeature, comment):
		self.type = 'FeatureLookup'
		self.lookupflag = lookupflag
		self.script = script
		self.language = language
		self.feature = feature
		self.lookupfeature = lookupfeature
		self.comment = comment

# GPOS

class GPOSLookupType1:
	def __init__(self, feature, glyphs, adjustment, script, language, lookupflag, comment):
		self.type = 'GPOSLookupType1'
		self.feature = feature
		self.glyphs = glyphs
		self.adjustment = adjustment # four touple (n, n, n, n)
		self.script = script
		self.language = language
		self.lookupflag = lookupflag
		self.comment = comment

class GPOSLookupType2:
	def __init__(self, feature, pair, adjustment, script, language, lookupflag, comment):
		self.type = 'GPOSLookupType2'
		self.feature = feature
		self.pair = pair
		self.adjustment = adjustment # four touple (n, n, n, n)
		self.script = script
		self.language = language
		self.lookupflag = lookupflag
		self.comment = comment



# Helper functions

def CollectGlyphGroups(glyphnames):

	list = Ddict(dict)

	for glyphname in glyphnames:
		if '.' in glyphname: # has ending, but is no ligature
			ending = os.path.splitext(glyphname)[1]
			if not list.has_key(ending):
				list[ending] = []
			list[ending].append(glyphname)
	
	return list

# write lines of FDK feature code

def FDKlookupcode(lookups, intendlevel):
	featurecode = []
	intend = '  '

	for lookup in lookups:
		if isinstance(lookup, GSUBLookup):
			comment = ''
			if lookup.comment: comment = '# ' + lookup.comment
			featurecode.append((intendlevel * intend) + 'sub %s by %s; %s' % (lookup.source, lookup.target, comment))

		elif isinstance(lookup, FeatureLookup):
			comment = ''
			if lookup.comment: comment = '# ' + lookup.comment
			featurecode.append((intendlevel * intend) + 'feature %s; %s' % (lookup.lookupfeature, comment))

		elif isinstance(lookup, GPOSLookupType1):
			comment = ''
			if lookup.comment: comment = '# ' + lookup.comment
			if lookup.adjustment[1] == 0 and lookup.adjustment[2] == 0 and lookup.adjustment[3] == 0:
				adjustmentcode = lookup.adjustment[0]
			else:
				adjustmentcode = '<%s %s %s %s>' % (lookup.adjustment[0], lookup.adjustment[1], lookup.adjustment[2], lookup.adjustment[3])
			featurecode.append((intendlevel * intend) + 'pos %s %s; %s' % (lookup.glyphs, adjustmentcode, comment))

		elif isinstance(lookup, GPOSLookupType2):
			comment = ''
			if lookup.comment: comment = '# ' + lookup.comment
			if lookup.adjustment[1] == 0 and lookup.adjustment[2] == 0 and lookup.adjustment[3] == 0:
				adjustmentcode = lookup.adjustment[0]
			else:
				adjustmentcode = '<%s %s %s %s>' % (lookup.adjustment[0], lookup.adjustment[1], lookup.adjustment[2], lookup.adjustment[3])
			featurecode.append((intendlevel * intend) + 'pos %s %s; %s' % (lookup.pair, adjustmentcode, comment))
	
	return featurecode


def TranslateLanguage(language, defaultlanguage):
	return language.replace('__DEFAULT__', defaultlanguage)

def TranslateScript(script, defaultlanguage):
	return script.replace('__DEFAULT__', defaultlanguage)



class Ddict(dict):
    def __init__(self, default=None):
        self.default = default
       
    def __getitem__(self, key):
        if not self.has_key(key):
            self[key] = self.default()
        return dict.__getitem__(self, key)


def GetFDKCodeVersion(codeversion):
	if not codeversion:
		try:
			import FL
			codeversion = "2.3"
		except:
			codeversion = "2.5"
	
	return codeversion

def ScriptSort(a, b):
	if a == 'latn':
		return -1
	else:
		return 0

def LanguageSort(a, b):
	if a == '__DEFAULT__':
		return -1
	else:
		return 0

def intersect(a, b):
	return list(set(a) & set(b))