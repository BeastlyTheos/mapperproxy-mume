# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from unittest.mock import Mock

from mapper.ArmouryPasswordDecoder import ArmouryPasswordDecoder, lineRegex, startOfPasswordLine
from mapper.mapper import Mapper


class TestArmouryPasswordDecoder(unittest.TestCase):
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

	def setUp(self):
		cls = TestArmouryPasswordDecoder
		cls.mapper.clientSend = Mock()
		self.decoder = ArmouryPasswordDecoder(cls.mapper)

	def testNothingHappensWhenReceivingIrrelevantLines(self):
		sendall = self.mapper.clientSend
		decoder = self.decoder

		decoder.decodePassword = Mock()

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
			sendall.assert_not_called()
			decoder.decodePassword.assert_not_called()

	def testErrorIsSentToClientWhenLineHasInvalidPassword(self):
		sendall = self.mapper.clientSend
		decoder = self.decoder

		decoder.decodePassword = Mock()

		for line in [
			"Barely visible in a corner of the page is the strange word: ",
			"Barely visible in a corner of the page is the strange word: rtkauk",
			"Barely visible in a corner of the page is the strange word: jndaJwsdkh",
			"Barely visible in a corner of the page is the strange word: jnda3sdkh",
			"Barely visible in a corner of the page is the strange word: sekrgfrag8",
			"Barely visible in a corner of the page is the strange word: 9zmlrfrwol",
			"Barely visible in a corner of the page is the strange word: szla.mzag",
		]:
			self.assertFalse(lineRegex.search(line), "'%s' is a bad test line. It shouldn't match the regex" % line)
			decoder.handle(line)
			decoder.decodePassword.assert_not_called()
			sendall.assert_called_with(
				"Error in armoury password decoder: cannot parse a password from preceding line."
			)

	def test_decodePassword_isCalledWhenReceivingLineWithAValidPassword(self):
		sendall = self.mapper.clientSend
		decoder = self.decoder

		decoder.decodePassword = Mock()

		for line in [
			"Barely visible in a corner of the page is the strange word: rtkabmsuk",
			"Barely visible in a corner of the page is the strange word: jndaJwsdk",
			"Barely visible in a corner of the page is the strange word: sekrgfrag",
			"Barely visible in a corner of the page is the strange word: zmlrfrwol",
			"Barely visible in a corner of the page is the strange word: zajrpsjef",
			"Barely visible in a corner of the page is the strange word: fadmmrztr",
			"Barely visible in a corner of the page is the strange word: maftvmnua",
			"Barely visible in a corner of the page is the strange word: zjgoelnda",
			"Barely visible in a corner of the page is the strange word: norlamznz",
			"Barely visible in a corner of the page is the strange word: vajranmre",
			"Barely visible in a corner of the page is the strange word: hhdbafrgo",
			"Barely visible in a corner of the page is the strange word: zusuofnep",
			"Barely visible in a corner of the page is the strange word: sadndfnds",
			"Barely visible in a corner of the page is the strange word: zJfrazskg",
			"Barely visible in a corner of the page is the strange word: hlkaashhe",
			"Barely visible in a corner of the page is the strange word: fskulmvgl",
			"Barely visible in a corner of the page is the strange word: sbzrawlba",
			"Barely visible in a corner of the page is the strange word: rhmtpmnfb",
			"Barely visible in a corner of the page is the strange word: hsLeasveJ",
			"Barely visible in a corner of the page is the strange word: mkdramzkr",
			"Barely visible in a corner of the page is the strange word: fekpunnaa",
			"Barely visible in a corner of the page is the strange word: nadjehmau",
			"Barely visible in a corner of the page is the strange word: zgdramrJa",
			"Barely visible in a corner of the page is the strange word: hjnrkfrun",
			"Barely visible in a corner of the page is the strange word: sjzaafhuu",
			"Barely visible in a corner of the page is the strange word: wkjhussad",
			"Barely visible in a corner of the page is the strange word: satoemwaL",
			"Barely visible in a corner of the page is the strange word: zadaarJkb",
			"Barely visible in a corner of the page is the strange word: rkdtmmmul",
			"Barely visible in a corner of the page is the strange word: szladmzag",
			"Barely visible in a corner of the page is the strange word: medaesruz",
		]:
			self.assertTrue(lineRegex.search(line), "'%s' is a bad test line. It should match the regex" % line)
			decoder.handle(line)
			
			sendall.assert_not_called()
			decoder.decodePassword.assert_called_with(line[len(startOfPasswordLine):])
