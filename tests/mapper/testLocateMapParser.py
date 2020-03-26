# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from unittest.mock import Mock

from mapper.LocateMapParser import LocateMapParser, verticleBordersRegex


class TestRegex(unittest.TestCase):
	def test_verticleBordersRegex(self):
		for line in [
			"+-----------------------------------+",
			"+-----------------------------------+",
			"+-----------------+",
			"+-----------------+",
			"+-----------------------------------+",
			"+-------+",
		]:
			self.assertTrue(
				verticleBordersRegex.match(line),
				"'%s' does not match the regex for start and end lines." % line
			)

		for line in [
			"|????????????????   ????????????????|",
			"|????????????           ????????????|",
			"|?????????                 ?????????|",
			"|????????                   ????????|",
			"|??????                       ??????|",
			"|?????                         ?????|",
			"|????                           ????|",
			"|???                             ???|",
			"|??                               ??|",
			"|?                                 ?|",
			"|                                   |",
			"|       - ---     X ------  --------|",
			"|     ----- ---   -------- --    ---|",
			"|?--- -------   ==--------- - ---- ?|",
			"|?-=- -- ----   ==-----------------?|",
			"|?-------------------------  -- -  ?|",
			"|?------------- - - ------   -- -  ?|",
			"|??---------- --- - --------------??|",
			"|??------------ ------------------??|",
			"|??---- -          ------- ---- - ??|",
			"|???-  --           --     - --  ???|",
			"|???????   ???????|",
			"|????         ????|",
			"|???           ???|",
			"|??             ??|",
			"|?               ?|",
			"|--     3 ------  |",
			"| ---   -X------ -|",
			"|--   ==--------- |",
			"|?-   ==---------?|",
			"|?---------------?|",
			"|?--- - - ------ ?|",
			"|?? --- - ------??|",
			"|???- ---------???|",
			"|????    -----????|",
			"|???????  -???????|",
			"|??   ??|",
			"|?     ?|",
			"|  2 ---|",
			"|  -X---|",
			"|==-----|",
			"|?=----?|",
			"|??---??|",
		]:
			self.assertFalse(
				verticleBordersRegex.match(line),
				"'%s' matches the regex for start and end lines."
			)

	def test_handle_whenGivenCompleteMap(self):
		parser = LocateMapParser(Mock())
		parser.parseLine = Mock()
		parser.printCoordinates = Mock()
		for line in [
			"+",
			"++",
			"| ---   -X------ -|",
			"Mana:Cold>",
			"A hobbit has arrived from the south.",
			"You sit down and rest your tired bones.",
			"cast 'locate magic' good 16",
			"Traces of white tones form the aura of this place.",
			"|--   ==--------- |",
			"|??             ??|",
			"|  2 ---|",
		]:
			parser.handle(line)
			parser.parseLine.assert_not_called()
			parser.printCoordinates.assert_not_called()

		parser.handle("+---+")
		for line in [
			"| ---   -X------ -|",
			"|--   ==--------- |",
			"|??             ??|",
			"|  2 ---|",
		]:
			parser.handle(line)
			parser.parseLine.assert_called_with(line)
			parser.printCoordinates.assert_not_called()
