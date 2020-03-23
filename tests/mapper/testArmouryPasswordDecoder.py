# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from unittest.mock import Mock

from mapper.ArmouryPasswordDecoder import ArmouryPasswordDecoder, startOfPasswordLine
from mapper.mapper import Mapper


class TestArmouryPasswordDecoder(unittest.TestCase):
	def testNothingHappensWhenReceivingIrrelevantLines(self):
		Mapper.loadRooms = Mock()  # to speed execution of tests
		mapper = Mapper(
			client=Mock(),
			server=None,
			outputFormat=None,
			interface="text",
			promptTerminator=None,
			gagPrompts=None,
			findFormat=None,
			isEmulatingOffline=None,
		)
		mapper.daemon = True  # this allows unittest to quit if the mapper thread does not close properly.
		mapper._client.sendall = Mock()
		decoder = ArmouryPasswordDecoder(mapper)
		decoder.handlePassword = Mock()

		for line in [
			"Road of Narvi",
			">",
			"Doors: east: dwarfdoor",
			"Hidden Chamber",
			"The corpse of a stone statue is lying here.",
			"A large boulder is here, it must be heavy.",
			"up",
			"Doors: up: hatch, west: dwarfdoor",
			"Chamber of Zirakzigil",
			"Alas, you cannot go that way...",
			"You hear some very close noise from below.",
			"Carl has arrived from below.",
			"l page",
			"    ___________________________________",
			"   /                                  /)",
			"   |             -=-                 |/",
			"   |  -^-                        ~   |",
			"   |                                 |",
			"   |       ~                  ~      |",
			"   |                  ~              |",
			"   |      -^-                        |",
			"   |            ~          -=-       |",
			"   |_________________________________|",
			"  /|                                 )",
			" (/_________________________________/",
			"Carl tells you [GT] 'whats the command anyway'",
			"Gene tells you [GT] 'l page'",
			"Cindy says 'zadramnar'",
			"Carl leaves down.",
		]:
			decoder.handle(line)
			decoder.mapper._client.sendall.assert_not_called()
			decoder.handlePassword.assert_not_called()
