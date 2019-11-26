# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

exitRegexpString =\
r"(?P<isNone>none)|[-=~]?[\[(#{/\\]?(?P<dir>north|east|south|west|up|down)[\])#{/\\]?[-=~]?"

exitRegexp = re.compile("^" + exitRegexpString + "$")
autoexitRegexp = re.compile(r"Exits: (?P<exits>(" + exitRegexpString + r"(, )?)+)\.")
exitCommandRegexp = re.compile(
	r"(?P<exits>( *" + exitRegexpString + " +- [^\r]+(\r\n)?)+)"
)


class ExitsSubstituter(object):
	def __init__(self, mapper):
		self.mapper = mapper
		self.mapper.registerMudEventHandler("exits", self.handle)

	def handle(self, exits):
		hiddenExits = []
		for exit in self.mapper.currentRoom.exits:
			if "hidden" in exit.doorFlags:
				hiddenExits.append(exit)
		if not hiddenExits:
			self.output(exits)
		m = autoexitRegexp.match(exits)
		if m:
			self.handleAutoExits(m)

	def handleAutoExits(self, regexpMatch):
		# get exits list 
		# get current room's exits
		# for every one of the current room's exits that is not in the regexp list, add it
		self.mapper.output("Exits: none.")
