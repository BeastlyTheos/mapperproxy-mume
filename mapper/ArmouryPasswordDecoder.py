# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

startOfPasswordLine = "Barely visible in a corner of the page is the strange word: "


class ArmouryPasswordDecoder(object):
	def __init__(self, mapper):
		self.mapper = mapper
		self.mapper.registerMudEventHandler("line", self.handle)

	# def handle(self, line):
		# check if the line starts with lineStart
		# use regex to extract the word
		# if no word, send error to client
		# else process the word

	# def processPassword(self, word):
		# add to the list of all passwodrs seen so far
		# find the most common letter for each index in the word
		# compile new guess
		# output guess
		# compare to old guess and output how much it has changed
