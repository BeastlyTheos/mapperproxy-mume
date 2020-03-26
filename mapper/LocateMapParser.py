# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

verticleBordersRegex = re.compile("\+-+\+")
lineRegex = "\|?(?P<chars>[-?X]+)\|"


class LocateMapParser(object):
	def __init__(self, mapper):
		self.mapper = mapper
		self.mapper.registerMudEventHandler("line", self.handle)

	# def handle(self, line):
		# line is a starting line and is not reading
			# is reading = true and re initialise the array of lines
		# else if is reading
			# if starts and ends with verticle bars ||
				# call parse line
			# if is ending line
				# is reading = false
				# print coordinates

	# def parseLines
			# for each char in the line
				# if else statements to handle the char
				# if magic char, store coordinates
				# if recognised non-magic char, skip
				# else print a non-interuptive error
