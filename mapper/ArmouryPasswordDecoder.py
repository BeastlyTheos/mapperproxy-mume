# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re
from statistics import mode

startOfPasswordLine = "Barely visible in a corner of the page is the strange word: "
passwordRegex = "(?P<password>[A-Za-z]{9,12})"
lineRegex = re.compile("^" + startOfPasswordLine + passwordRegex + "$")


class ArmouryPasswordDecoder(object):
	def __init__(self, mapper):
		self.mapper = mapper
		self.mapper.registerMudEventHandler("line", self.handle)
		self.words = [[] for i in range(9)]
		self.oldGuess = ""

	def handle(self, line):
		if line.startswith(startOfPasswordLine):
			m = lineRegex.match(line)
			if m:
				self.decodePassword(m.group("password"))
			else:
				self.mapper.clientSend(
					"Error in armoury password decoder: cannot parse a password from preceding line."
				)

	def decodePassword(self, word):
		for i in range(9):
			self.words[i].append(word[i])
		guess_asList = [mode(i) for i in self.words]
		guess = "".join(guess_asList)
		self.mapper.clientSend("guess is " + guess)
		# print("guess is " + guess)
		if self.oldGuess:
			identicalLetters = 0
			for i in range(9):
				if guess[i] == self.oldGuess[i]:
					identicalLetters += 1
			self.mapper.clientSend("This has %d letters in common with the last guess." % identicalLetters)
			# print("This has %d letters in common with the last guess." % identicalLetters)
		self.oldGuess = guess
