# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

verticleBordersRegex = re.compile(r"\+-+\+")


class LocateMapParser(object):
	def __init__(self, mapper):
		self.mapper = mapper
		self.mapper.registerMudEventHandler("line", self.handle)
		self.isParsing = False

	def handle(self, line):
		"""handles input of type line
		if has seen top border and line is not a border, parses the line into coordinates and stores them
		if reading a map and line is a border, sets reading flag to false and prints all coordinates
		"""
		if line.startswith("+") and line.endswith("+") and verticleBordersRegex.match(line):
			# using startswith and endswith minimises the number of calls to regex
			if self.isParsing:
				self.isParsing = False
				self.printCoordinates()
			else:
				self.isParsing = True
				# re initialise the array of lines
		elif self.isParsing:
			if line.startswith("|") and line.endswith("|"):
				self.parseLine(line)
			else:
				self.mapper._client.sendall("Unrecognisable map line. Terminating parsing.")
				self.isParsing = False

	def parseLine(self, line):
		line = line[1:-1]
		numChars = len(line)
		for c in range(numChars):
			char = line[c]
			if char == "X" or char.isdigit():
				self.saveCoordinate(char, c)
			elif char in "-=?":
				pass
			else:
				self.mapper._client.sendall("Unrecognised char '%s'" % char)

	def printCoordinates(self, line):
		pass
