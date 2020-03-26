# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest

from mapper.LocateMapParser import LocateMapParser, lineRegex, verticleBordersRegex


class TestLocateMapParser_regex(unittest.TestCase):
	def testLinesRegex(self):
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

	def testLineRegex(self):
		for line in [
		]:
			self.assertTrue(verticleRegex.match(line), line + " does not match the regex for map lines.")

		for line in [
		]:
			self.assertFalse(lineRegex.match(line), line + " matches the regex for map lines.")
