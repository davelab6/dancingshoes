What is Dancing Shoes?
------------------------

Dancing Shoes is a Python-library that provides a friendly interface to create OpenType feature code using simple instructions.
It lets you instruct it with your substitution and positioning lookups in an arbitrary order using simple functions and it will take care of outputting correct and nicely formatted feature code.

Since a lot of type designers and foundries use their own naming schemes for glyph names and the resulting feature code, Dancing Shoes cannot provide you with the perfect and professional feature code for your fonts.
You still have to come up with the features yourself. What it does is to provide you with easy means to tell it how you want your substitutions, and it will take care of the correct code output. Once you have gathered all substitutions for your glyph naming scheme, Dancing Shoes is your one-click feature code solution.

The main idea is that you can throw any amount of substitutions from your hard-coded files at it, and Dancing Shoes will only add those feature, whose participating glyphs are actually present in the font’s glyph repertoire, which you supply on each generation operation. This way you have to sit down once to harvest all the substitutions you want, including scripts to dynamically generate substitutions or positioning from the data source of your choice, and can apply this to all your fonts following your naming scheme as a recurring task.

Code documentation and release log at <http://www.yanone.de/typedesign/code/dancingshoes/>
