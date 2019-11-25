# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest

from mapper.ExitSubs import exitRegexp
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
			dir = "none" if m.group(0) == "none" else m.group("dir")
			self.assertTrue(dir in DIRECTIONS + ["none"], exit + " is not a direction")

	@unittest.skip
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
			r"Exits: ~/up\~.",
			r"Exits: ~\down/~.",
			"Exits: -north-.",
			"Exits: -[east]-.",
			"Exits: -(south)-.",
			"Exits: -#west#-.",
			r"Exits: -/up\-.",
			r"Exits: -\down/-.",
			"Exits: =north=.",
			"Exits: =[east]=.",
			"Exits: =(south)=.",
			"Exits: =#west#=.",
			r"Exits: =/up\=.",
			r"Exits: =\down/=.",
			"Exits: ~#north#~, -east-.",
			"Exits: =[south]', (west), ~#up#~.",
			"Exits: none.",
		]:
			m = autoexitsRegexp.match(autoexits)
			self.assertTrue(m)
			exits = m.group("exits")
			for exit in exits:
				self.assertTrue(exit in ["north", "east", "south", "west", "up", "down"])


	@unittest.skip
	def test_exitsCommandRegexp(self):
		for exits in [
			"[North]  - A closed 'stabledoor'\r\nSouth   - The Path over the Bruinen",
			"#South#  - (archedfence) The Summer Terrace",
			"[North]  - A closed 'marblegate'\r\nEast    - On a Graceful Bridge\r\nSouth   - On a Balcony over the Bruinen\r\nWest    - Meandering Path along the Bruinen\r\nUp      - At the Last Pavilion",
			"~East~   - South Fork of the Bruinen\r\n~West~   - South Fork of the Bruinen\r\n/Up\     - Abrupt Riverside",
			"East    - Rocky River Bank\r\nSouth   - Bend in the Path to the Misty Mountains\r\nWest    - Rocky Riverbank\r\n~\Down/~  - South Fork of the Bruinen",
			"North   - Evergreen Forest\r\nWest    - Plateau\r\n~\Down/~  - Entrenched Meander",
			"North   - Lightly-wooded Roadside\r\n=East=   - Great East Road West of a Gully\r\nSouth   - Dispersed Pines along the Road\r\n=West=   - Great East Road",
			"-North-  - Junction in the Path\r\nEast    - Folded Lands\r\n-South-  - Bend in a Faded Trail\r\nWest    - A Rock-bristled Riverside",
			"=(West)=  - (gorydoor) You can't distinguish a lot of details.",
			"None.",
		]:
			m = exitCommandRegexp.match(exits)
			self.assertTrue(m)
			for exit in exits:
				self.assertTrue(exit in ["north", "east", "south", "west", "up", "down"])

#class TestExitsSubstitution(unittest.TestCase):
#class method to setup mapper object
#instance method to setup new room object, and remock the client send method
#			have various functions that call the event handler, varrying the room attributes, such as, no exits, some exits, some exits with some being hidden, all exits being hidden, room object knows of no exits, but game says there are none...