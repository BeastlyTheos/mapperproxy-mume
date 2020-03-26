# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

verticleBordersRegex = re.compile(r"\+-+\+")


class LocateMapParser(object):
	def __init__(self, mapper):
		self.mapper = mapper
		self.mapper.registerMudEventHandler("line", self.handle)
		self.isReadingMap = False

	def handle(self, line):
		"""handles input of type line
		if has seen top border and line is not a border, parses the line into coordinates and stores them
		if reading a map and line is a border, sets reading flag to false and prints all coordinates
		"""
		pass
		# line starts with +, ends with +, and other chars are -. is a starting line and is not reading
			# is reading = true and re initialise the array of lines
		# else if is reading
			# if starts and ends with verticle bars ||
				# call parse line
			# if is ending line
				# is reading = false
				# print coordinates
			# else
				# error about unrecognised map line
				# set isReading to false

	def parseLine(self, line):
		pass
			# for each char in the line
				# if else statements to handle the char
				# if magic char, store coordinates
				# if recognised non-magic char, skip
				# else print a non-interuptive error

	def printCoordinates(self, line):
		pass
