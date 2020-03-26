# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re


class ArmouryPasswordDecoder(object):
	def __init__(self, mapper):
		self.mapper = mapper
		self.mapper.registerMudEventHandler("line", self.handle)
		self.words = [[] for i in range(9)]
		self.oldGuess = ""

	# def handle(self, line):
		# line is a starting line and is not reading
			# is reading = true and re initialise the array of lines
		# else if is reading
			# if is map line
				# store it
			# if is ending line
				# is reading = false
				# do the parsing stuff

	# def parseLines
		# for each line
			# for each magic in the line
				# store the x and y coordinates
		# print all coordinates
