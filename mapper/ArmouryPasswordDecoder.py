# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

startOfPasswordLine = "Barely visible in a corner of the page is the strange word: "
passwordRegex = "(?P<password>[A-Za-z]{9})"
lineRegex = re.compile("^" + startOfPasswordLine + passwordRegex + "$")


class ArmouryPasswordDecoder(object):
	def __init__(self, mapper):
		self.mapper = mapper
		self.mapper.registerMudEventHandler("line", self.handle)

	def handle(self, line):
		if line.startswith(startOfPasswordLine):
			m = lineRegex.match(line)
			if m:
				self.handlePassword(m.group("password"))
			else:
				self.mapper._client.sendall(
					"Error in armoury password decoder: cannot parse a password from preceding line."
				)

	def handlePassword(self, word):
		pass
		# add to the list of all passwodrs seen so far
		# find the most common letter for each index in the word
		# compile new guess
		# output guess
		# compare to old guess and output how much it has changed
