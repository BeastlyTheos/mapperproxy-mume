# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from unittest.mock import Mock

from mapper.ExitSubs import autoexitRegexp, exitCommandRegexp, exitRegexp, ExitsSubstituter
from mapper.mapper import Mapper
from mapper.world import DIRECTIONS


class TestExitsSubstitution_regexp(unittest.TestCase):
	def test_exitRegexp(self):
		for exit in [
			"north",
			"[east]",
			"(south)",
			"#west#",
			"/up\\",
			"\\down/",
			"~north~",
			"~[east]~",
			"~(south)~",
			"~#west#~",
			"~/up\\~",
			"~\\down/~",
			"-north-",
			"-[east]-",
			"-(south)-",
			"-#west#-",
			"-/up\\-",
			"-\\down/-",
			"=north=",
			"=[east]=",
			"=(south)=",
			"=#west#=",
			"=/up\\=",
			"=\\down/=",
			"none",
		]:
			m = exitRegexp.match(exit)
			self.assertTrue(m, exit + " did not match the exitRegexp")
			self.assertTrue(
				m.group("isNone") or m.group("dir") in DIRECTIONS,
				exit + " is not a direction nor is it 'none'."
			)

	def test_autoexitsRegexp(self):
		for autoexits in [
			"Exits: north.",
			"Exits: [east].",
			"Exits: (south).",
			"Exits: #west#.",
			r"Exits: /up\.",
			r"Exits: \down/.",
			"Exits: ~north~.",
			"Exits: ~[east]~.",
			"Exits: ~(south)~.",
			"Exits: ~#west#~.",
			"Exits: ~/up\\~.",
			"Exits: ~\\down/~.",
			"Exits: -north-.",
			"Exits: -[east]-.",
			"Exits: -(south)-.",
			"Exits: -#west#-.",
			"Exits: -/up\\-.",
			"Exits: -\\down/-.",
			"Exits: =north=.",
			"Exits: =[east]=.",
			"Exits: =(south)=.",
			"Exits: =#west#=.",
			"Exits: =/up\\=.",
			"Exits: =\\down/=.",
			"Exits: ~#north#~, -east-.",
			"Exits: =[south]=, (west), ~#up#~.",
			"Exits: none.",
		]:
			m = autoexitRegexp.match(autoexits)
			self.assertTrue(m, autoexits + " does not match the autoexitRegexp")
			for exit in m.group("exits").split(", "):
				m = exitRegexp.match(exit)
				self.assertTrue(
					m.group("isNone") or m.group("dir") in DIRECTIONS,
					"{dir} from {autoexits} is not a valid direction nor is it 'none'.".format(dir=exit, autoexits=autoexits)
				)

	def test_exitsCommandRegexp(self):
		for exits in [
			"#South#  - (archedfence) The Summer Terrace\r\n",
			"[North]  - A closed 'stabledoor'\r\nSouth   - The Path over the Bruinen\r\n",
			(
				"[North]  - A closed 'marblegate'\r\nEast    - On a Graceful Bridge\r\n"
				"South   - On a Balcony over the Bruinen\r\nWest    - Meandering Path along the Bruinen\r\n"
				"Up      - At the Last Pavilion\r\n"
			),
			(
				"~East~   - South Fork of the Bruinen\r\n~West~   - South Fork of the Bruinen\r\n"
				"/Up\\     - Abrupt Riverside\r\n"
			),
			(
				"East    - Rocky River Bank\r\nSouth   - Bend in the Path to the Misty Mountains\r\n"
				"West    - Rocky Riverbank\r\n~\\Down/~  - South Fork of the Bruinen\r\n"
			),
			"North   - Evergreen Forest\r\nWest    - Plateau\r\n~\\Down/~  - Entrenched Meander\r\n",
			(
				"North   - Lightly-wooded Roadside\r\n=East=   - Great East Road West of a Gully\r\n"
				"South   - Dispersed Pines along the Road\r\n=West=   - Great East Road\r\n"
			),
			(
				"-North-  - Junction in the Path\r\nEast    - Folded Lands\r\n-South-  - Bend in a Faded Trail\r\n"
				"West    - A Rock-bristled Riverside\r\n"
			),
			"=(West)=  - (gorydoor) You can't distinguish a lot of details.\r\n",
			"None.\r\n",
		]:
			exits = exits.lower()
			m = exitCommandRegexp.match(exits)
			self.assertTrue(m, exits + " does not match the exitCommandRegexp")
			exitsList = m.group("exits").strip().split("\r\n")
			self.assertEqual(
				len(exitsList), len(exits.strip().split("\r\n")),
				"{exits} was incorrectly parsed into {num} lines".format(exits=exits, num=len(exitsList))
			)
			for exit in exitsList:
				exit = exit.split(" - ")[0].strip()
				m = exitRegexp.match(exit)
				self.assertTrue(m, "Failed to parse a dir out of " + exit)
				self.assertTrue(
					m.group("isNone") or m.group("dir") in DIRECTIONS,
					"{dir} from {exits} is not a valid direction nor is it 'none'.".format(dir=exit, exits=exits)
				)


class TestExitsSubstitution_handler(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		Mapper.loadRooms = Mock()  # to speed execution of tests
		cls.mapper = Mapper(
			client=Mock(),
			server=None,
			outputFormat=None,
			interface="text",
			promptTerminator=None,
			gagPrompts=None,
			findFormat=None,
			isEmulatingOffline=None,
		)
		cls.mapper.daemon = True  # this allows unittest to quit if the mapper thread does not close properly.
		cls.exitsSubstituter = ExitsSubstituter(cls.mapper)

	def setUp(self):
		self.mapper = TestExitsSubstitution_handler.mapper
		self.mapper._client.sendall = Mock()
		self.handle = TestExitsSubstitution_handler.exitsSubstituter.handle

	def test_handler_withNoExits(self):
		self.handle("Exits: none.\r\n")
		self.mapper._client.sendall.assert_called_with(b"\r\nExits: none.\r\n")
