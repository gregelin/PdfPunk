#!/usr/bin/python
"""A little experiment usin Python and pdftotext to translate a PDF to text.

   Maybe one day will grow into a whole toolkit.

"""

import os
import fnmatch
import re
import pprint
import subprocess
import math


# Config
dirhead = "/codedata/FCC/projects/pdfpunk/examples"
file_path_examples = "/codedata/FCC/projects/pdfpunk/examples"
pp = pprint.PrettyPrinter(indent=4)


# Utilities

def write_file(content,file_path):
	f = open(file_path, 'w')
	f.write(content)
	f.close()

# xml 1.0 valid characters:
#    Char ::= #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
# so to invert that, not in Char ::
#       x0 - x8 | xB | xC | xE - x1F
#       (most control characters, though TAB, CR, LF allowed)
#       | #xD800 - #xDFFF
#       (unicode surrogate characters)
#       | #xFFFE | #xFFFF |
#       (unicode end-of-plane non-characters)
#       >= 110000
#       that would be beyond unicode!!!
_illegal_xml_chars_RE = re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')

def escape_xml_illegal_chars(val, replacement='?'):
	"""Filter out characters that are illegal in XML.
	Looks for any character in val that is not allowed in XML
    and replaces it with replacement ('?' by default).
	>>> escape_illegal_chars("foo \x0c bar")
	'foo ? bar'
	"""
	return _illegal_xml_chars_RE.sub(replacement, val)

def fix_smart_quotes(text):
	u = text.decode("utf-8") 
	clean =  u.translate(dict.fromkeys([0x201c, 0x201d, 0x2018, 0x2019]))
	text_clean = clean.encode("utf-8") 
	return text_clean

def to_html_pre(text_clean):
	html_doc_header = """<html>
<head>
</head>
<body style="font-family;courrier;">
	<pre id="pdftext" class="pdftext">
	"""
	
	html_doc_footer = """	</pre>
</body>
</html>
	"""
	return "%s\n%s\n%s" % (html_doc_header,text_clean,html_doc_footer)


# Main
# print a blank line
print " "

for root, dirs, files in os.walk(dirhead):
	# print root, dirs, files
	for file in files:
		if re.match("\.", file):
			continue
		if re.search("pdf", file):
			print "---"
			print "converting %s to html" % file
			file_name, file_ext = os.path.splitext(file)
			filein_abs_path = root + "/" + file
			
			# ETL PDF Document
			text = subprocess.Popen(['pdftotext', '-layout', filein_abs_path,"-"], stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
			text = escape_xml_illegal_chars(text)
			text = fix_smart_quotes(text)
			# Save new text file
			fileout_ext = "html"
			doc = to_html_pre(text)
			# print doc
			fileout_path_doc = file_path_examples + "/" + file_name + "." + fileout_ext
			print "Writing file %s" % (file)
			write_file(doc,fileout_path_doc)
	
