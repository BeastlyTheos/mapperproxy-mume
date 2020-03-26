# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from unittest.mock import call, Mock

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


class testLocateMapParser(unittest.TestCase):
	def setUp(self):
		self.mapper = Mock()
		self.mapper.clientSend = Mock()
		self.parser = LocateMapParser(self.mapper)

	def test_handle_whenGivenCompleteMap(self):
		parser = self.parser
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
		parser = self.parser
		mapper = self.mapper
		parser.parseLine = Mock()
		parser.printCoordinates = Mock()
		extraneousLine = "You sit down and rest your tired bones."

		# check that the extraneous line gracefully fails
		parser.handle("+---+")  # top border
		parser.handle(extraneousLine)
		mapper.clientSend.assert_called_with("Unrecognisable map line. Terminating parsing.\r\n" + extraneousLine)
		parser.parseLine.assert_not_called()
		parser.printCoordinates.assert_not_called()

		# assert the parser is no longer parsing lines
		parser.handle("| ---   -X------ -|")  # recognisable line of a map
		parser.parseLine.assert_not_called()
		parser.printCoordinates.assert_not_called()

	def test_parseLine_SavesCordinatesForEachValidChar(self):
		parser = self.parser
		mapper = self.mapper
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
		mapper.clientSend.assert_called_with("Unrecognised char 'Q'")

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
		mapper.clientSend.assert_called_with("Unrecognised char '.'")

	def test_printCoords_givenAFullMap(self):
		parser = self.parser
		output = self.mapper.clientSend
		parser.numCols = 7
		parser.numLines = 7

		for char, x, y in [
			("x", 2, 1),
			("3", 6, 1),
			("X", 3, 2),
			("2", 0, 3),
			("Z", 3, 3),
			("X", 1, 5),
			("Q", 4, 6),
		]:
			parser.saveCoordinate(char, x, y)

		parser.normaliseCoordinates()
		parser.printCoordinates()

		for expectedCall in [
			call("x 1 west 2 north"),
			call("3 3 east 2 north"),
			call("X 0  1 north"),
			call("2 3 west 0 "),
			call("Z 0  0 "),
			call("X 2 west 2 south"),
			call("Q 1 east 3 south"),
		]:
			self.assertIn(expectedCall, output.mock_calls)
			output.mock_calls.remove(expectedCall)
		self.assertFalse(output.mock_calls)
