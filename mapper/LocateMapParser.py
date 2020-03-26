# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

verticleBordersRegex = re.compile(r"\+-+\+")


class Coordinate(object):
	def __init__(self, char, x, y):
		self.char = char
		self.x = x
		self.y = y
		self.xDir = ""
		self.yDir = ""


class LocateMapParser(object):
	def __init__(self, mapper):
		self.mapper = mapper
		self.mapper.registerMudEventHandler("line", self.handle)
		self.isParsing = False
		self.numCols = None
		self.numLines = 0
		self.coords = []

	def handle(self, line):
		"""handles input of type line
		if has seen top border and line is not a border, parses the line into coordinates and stores them
		if reading a map and line is a border, sets reading flag to false and prints all coordinates
		"""
		if line.startswith("+") and line.endswith("+") and verticleBordersRegex.match(line):
			# using startswith and endswith minimises the number of calls to regex
			if self.isParsing:
				self.mapper.clientSend("done parsing map")
				self.isParsing = False
				self.normaliseCoordinates()
				self.printCoordinates()
			else:
				self.isParsing = True
				self.numCols = len(line) - 2
				self.numLines = 0
				self.coords = []
		elif self.isParsing:
			if line.startswith("|") and line.endswith("|"):
				self.parseLine(line, self.numLines)
				self.numLines += 1
			else:
				self.mapper.clientSend("Unrecognisable map line. Terminating parsing.\r\n" + line)
				self.isParsing = False

	def parseLine(self, line, y):
		line = line[1:-1]
		numChars = len(line)
		for c in range(numChars):
			char = line[c]
			if char == "X" or char.isdigit():
				self.saveCoordinate(char, c, y)
			elif char in "*-= ?":
				pass
			else:
				self.mapper.clientSend("Unrecognised char '%s'" % char)

	def saveCoordinate(self, char, x, y):
		self.coords.append(Coordinate(char, x, y))

	def normaliseCoordinates(self):
		for coord in self.coords:
			coord.x -= int((self.numCols - 1) / 2)
			coord.y -= int((self.numLines - 1) / 2)
			coord.xDir = "west" if coord.x < 0 else "east" if coord.x > 0 else ""
			coord.yDir = "north" if coord.y < 0 else "south" if coord.y > 0 else ""
			coord.x = abs(coord.x)
			coord.y = abs(coord.y)

	def printCoordinates(self):
		for coord in self.coords:
			self.mapper.clientSend(
				"{char} {x} {xDir} {y} {yDir}".format(**coord.__dict__)
			)
