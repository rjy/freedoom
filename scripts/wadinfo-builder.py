#!/usr/bin/env python
#
# Wadinfo builder, rewritten in Python :)
#
# Copyright (c) 2006 Simon Howard.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   * Redistributions of source code must retain the above copyright 
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright 
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of Simon Howard nor the names of its contributors
#     may be used to endorse or promote products derived from this
#     software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import glob
import os
import sys
import re

dummy = False

# Given a file name, get the resource name for it:

def resource_for_filename(filename):
	if "." in filename:
		return filename[0:filename.index(".")]
	else:
		return filename

# Build look-up table, mapping section and resource name to filename.

def build_lookup_table():
	result = {}

	for filename in glob.glob("*/*"):
		section = os.path.dirname(filename)
		basename = os.path.basename(filename)

		resource = resource_for_filename(basename)

		result[(section, resource)] = filename

	return result

# Given a file base name, eg. "HEADE5", find the file to be used for
# that resource.  If the file cannot be found, None is returned.

def find_file(section, name):
	key = (section, name)

	if key in file_lut:
		return file_lut[key]
	else:
		return None

# Warning header displayed at the top of an output file.

def print_warning_header():
	print "; This file is automatically generated."
	print "; Do not edit it directly!"
	print

# Remove comments beginning with "#" or ";"

def remove_comments(text):
	if "#" in text:
		return text[0:text.index("#")]
	elif ";" in text:
		return text[0:text.index(";")]
	else:
		return text

# Get the name of a dummy lump to use as a stand-in for the 
# given resource.

def get_dummy_name(resource):
	if resource.lower().startswith("demo"):
		return "fakedemo"
	else:
		return  "dummy"

# Parse an assignment statement.

def parse_assignment(section, line, match):
	resource = match.group(1).lower()
	override = match.group(3)

	# allow "= filename.ext" to override the filename used

	if override is not None:
		filename = find_file(section, override)
	else:
		filename = find_file(section, resource)

	# File not found?

	if filename is None:

		# This resource hasn't been submitted yet, so either
		# comment the line out, or use a dummy resource,
		# depending on configuration.

		if dummy:
			dummy_name = get_dummy_name(resource)

			result = "%s = %s" % (resource, dummy_name)
		else:
			result = "; " + line
	else:
		# Resource found.

		result = line

	return result

# Parse data from the given input stream.

def parse_stream(stream):

	section_re = re.compile(r'\[(.*)\]')
	assignment_re = re.compile(r'\s*(\S+)[^\=]*(\s*\=\s*(\S+))?')

	print_warning_header()

	section = None

	# Parse each line of the input file, possibly changing things as we go.

	for line in stream:

		# Strip newline

		line = line[0:len(line) - 1]

		# Remove comments

		line = remove_comments(line)

		# start of new section?

		match = section_re.search(line)

		if match:
			section = match.group(1)

			if section == "texture1" or section == "texture2":
				section = "textures"

		else:
			# Possibly comment out assignments.

			match = assignment_re.match(line)

			if match:
				line = parse_assignment(section, line, match)

		print line

# Parse command line options:

for arg in sys.argv:
	if arg == "-dummy":
		dummy = True

# Build look-up table for files:

file_lut = build_lookup_table()

# Parse the input stream:

parse_stream(sys.stdin)
