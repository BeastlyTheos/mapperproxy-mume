# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from unittest.mock import call, Mock

from mapper.LocateMapParser import LocateMapParser, verticleBordersRegex


class TestHandle(unittest.TestCase):
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
		numLines = 0

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
			parser.parseLine.assert_called_with(line, numLines)
			numLines += 1
			parser.printCoordinates.assert_not_called()

		parser.handle("+---+")
		parser.printCoordinates.assert_called()
		parser.parseLine.reset_mock()
		parser.printCoordinates.reset_mock()

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

	def test_handle_whenGivenMapWithExtraneousLines(self):
		mapper = Mock()
		mapper._client.sendall = Mock()
		parser = LocateMapParser(mapper)
		parser.parseLine = Mock()
		parser.printCoordinates = Mock()

		# check that the extraneous line gracefully fails
		parser.handle("+---+")  # top border
		parser.handle("You sit down and rest your tired bones.")  # not a recognised line of a map
		mapper._client.sendall.assert_called_with("Unrecognisable map line. Terminating parsing.")
		parser.parseLine.assert_not_called()
		parser.printCoordinates.assert_not_called()

		# assert the parser is no longer parsing lines
		parser.handle("| ---   -X------ -|")  # recognisable line of a map
		parser.parseLine.assert_not_called()
		parser.printCoordinates.assert_not_called()


class testParseLine(unittest.TestCase):
	def test_parseLine_callsSaveCordinatesForEachValidChar(self):
		mapper = Mock()
		mapper._client.sendall = Mock()
		parser = LocateMapParser(mapper)
		parser.saveCoordinate = Mock()

		parser.parseLine("|X-2=Q3?|", 5)
		self.assertEqual(
			parser.saveCoordinate.mock_calls,
			[
				call("X", 0, 5),
				call("2", 2, 5),
				call("3", 5, 5),
			]
		)
		mapper._client.sendall.assert_called_with("Unrecognised char 'Q'")

		parser.saveCoordinate.reset_mock()

		parser.parseLine("|??--=X-2--=3.X????|", 2)
		self.assertEqual(
			parser.saveCoordinate.mock_calls,
			[
				call("X", 5, 2),
				call("2", 7, 2),
				call("3", 11, 2),
				call("X", 13, 2),
			]
		)
		mapper._client.sendall.assert_called_with("Unrecognised char '.'")
