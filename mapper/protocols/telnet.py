# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Built-in Modules:
import logging
from telnetlib import IAC, DO, DONT, WILL, WONT, SB, SE, CHARSET, GA
import threading


# Some sub-option constants that aren't defined in the telnetlib module.
SB_IS, SB_SEND, SB_INFO = (bytes([i]) for i in range(3))
# The Q Method of Implementing TELNET Option Negotiation (RFC 1143).
NO, YES, EXPECT_NO, EXPECT_YES, EXPECT_NO_OPPOSITE, EXPECT_YES_OPPOSITE = (i for i in range(6))
REMOTE = 0
LOCAL = 1
# Telnet charset sub-option (RFC 2066).
SB_REQUEST, SB_ACCEPTED, SB_REJECTED, SB_TTABLE_IS, SB_TTABLE_REJECTED, SB_TTABLE_ACK, SB_TTABLE_NAK = (
	bytes([i]) for i in range(1, 8)
)


logger = logging.getLogger(__name__)


def escapeIAC(dataBytes):
	return dataBytes.replace(IAC, IAC + IAC)


class TelnetHandler(object):
	def __init__(self, processed, remoteSender, promptTerminator=None):
		self._processed = processed
		self._remoteSender = remoteSender
		self._promptTerminator = promptTerminator
		self.optionNegotiationOrds = frozenset(ord(byte) for byte in (DONT, DO, WONT, WILL))
		self.inCommand = threading.Event()
		self.optionNegotiation = None
		self.inSubOption = threading.Event()
		self._subOptionBuffer = bytearray()
		self.charsets = {
			"us-ascii": b"US-ASCII",
			"latin-1": b"ISO-8859-1",
			"utf-8": b"UTF-8"
		}
		self._options = {
			CHARSET: {
				"separator": b";",
				"name": self.charsets["us-ascii"]
			}
		}

	def _sendRemote(self, dataBytes):
		try:
			self._remoteSender(dataBytes)
		except TypeError:
			if isinstance(self._remoteSender, (bytearray, list)):
				self._remoteSender.extend(dataBytes)
			else:
				raise

	def _sendOption(self, command, option):
		self._sendRemote(IAC + command + option)

	def handleCommand(self, ordinal):
		if ordinal in IAC:
			# Escaped IAC, ignore.
			pass
		elif ordinal in SB:
			# Sub-option begin.
			self.inSubOption.set()
		elif ordinal in GA:
			# MUME will send IAC + GA after a prompt.
			self._processed.extend(self._promptTerminator if self._promptTerminator is not None else IAC + GA)
		elif ordinal in self.optionNegotiationOrds and self.optionNegotiation is None:
			self.optionNegotiation = ordinal
		else:
			self._processed.extend((IAC[0], ordinal))
		self.inCommand.clear()

	def handleOption(self, ordinal):
		command = bytes([self.optionNegotiation])
		self.optionNegotiation = None
		option = bytes([ordinal])
		if option in self._options:
			if command == WILL or command == WONT:
				nvt = REMOTE
				rxAccept = WILL
				txAccept = DO
				txDeny = DONT
			else:
				nvt = LOCAL
				rxAccept = DO
				txAccept = WILL
				txDeny = WONT
			if nvt not in self._options[option]:
				self._options[option][nvt] = NO
			if command == rxAccept:
				if self._options[option][nvt] == NO:
					self._options[option][nvt] = YES
					self._sendOption(txAccept, option)
				elif self._options[option][nvt] == EXPECT_NO:
					self._options[option][nvt] = NO
				elif self._options[option][nvt] == EXPECT_NO_OPPOSITE:
					self._options[option][nvt] = YES
				elif self._options[option][nvt] == EXPECT_YES_OPPOSITE:
					self._options[option][nvt] = EXPECT_NO
					self._sendOption(txDeny, option)
				else:
					self._options[option][nvt] = YES
					if option == CHARSET:
						logger.debug("MUME acknowledges our request, tells us to begin charset negotiation.")
						# Negotiate the character set.
						separator = self._options[CHARSET]["separator"]
						name = self._options[CHARSET]["name"]
						logger.debug(f"Tell MUME we would like to use the '{name.decode('us-ascii')}' charset.")
						self.sendSubOption(CHARSET, SB_REQUEST + separator + name)
			else:
				if self._options[option][nvt] == YES:
					self._options[option][nvt] = NO
					self._sendOption(txDeny, option)
				elif self._options[option][nvt] == EXPECT_NO_OPPOSITE:
					self._options[option][nvt] = EXPECT_YES
					self._sendOption(txAccept, option)
				else:
					self._options[option][nvt] = NO
		else:
			self._processed.extend(IAC + command + option)

	def handleSubOption(self, ordinal):
		if self._subOptionBuffer.endswith(IAC) and ordinal in SE:
			# Sub-option end.
			del self._subOptionBuffer[-1]  # Remove IAC from the end.
			option = bytes([self._subOptionBuffer.pop(0)])
			if option == CHARSET:
				status = self._subOptionBuffer[:1]
				response = self._subOptionBuffer[1:]
				name = self._options[CHARSET]["name"]
				if status == SB_ACCEPTED:
					logger.debug(f"MUME responds: Charset '{response.decode('us-ascii')}' accepted.")
				elif status == SB_REJECTED:
					# Note: MUME does not respond with the charset name if it was rejected.
					logger.warning(f"MUME responds: Charset '{name.decode('us-ascii')}' rejected.")
				else:
					logger.warning(
						"Unknown charset negotiation response from MUME: "
						+ repr(IAC + SB + CHARSET + self._subOptionBuffer + IAC + SE)
					)
			else:
				self._processed.extend(IAC + SB + option + self._subOptionBuffer + IAC + SE)
			self._subOptionBuffer.clear()
			self.inSubOption.clear()
		else:
			self._subOptionBuffer.append(ordinal)

	def sendCommand(self, command):
		self._sendRemote(IAC + command)

	def sendSubOption(self, option, dataBytes):
		self._sendRemote(IAC + SB + option + escapeIAC(dataBytes) + IAC + SE)

	def isOptionEnabled(self, option, nvt, state=YES):
		return (
			option in self._options
			and nvt in self._options[option]
			and self._options[option][nvt] == state
		)

	def enableOption(self, option, nvt):
		if nvt == REMOTE:
			txAccept = DO
		else:
			txAccept = WILL
		if option not in self._options:
			self._options[option] = {}
		if nvt not in self._options[option] or self._options[option][nvt] == NO:
			self._options[option][nvt] = EXPECT_YES
			self._sendOption(txAccept, option)
		elif self._options[option][nvt] == EXPECT_NO:
			self._options[option][nvt] = EXPECT_NO_OPPOSITE
		elif self._options[option][nvt] == EXPECT_YES_OPPOSITE:
			self._options[option][nvt] = EXPECT_YES

	def disableOption(self, option, nvt):
		if nvt == REMOTE:
			txDeny = DONT
		else:
			txDeny = WONT
		if option not in self._options:
			self._options[option] = {}
		if nvt not in self._options[option]:
			self._options[option][nvt] = NO
		elif self._options[option][nvt] == YES:
			self._options[option][nvt] = EXPECT_NO
			self._sendOption(txDeny, option)
		elif self._options[option][nvt] == EXPECT_YES:
			self._options[option][nvt] = EXPECT_YES_OPPOSITE
		elif self._options[option][nvt] == EXPECT_NO_OPPOSITE:
			self._options[option][nvt] = EXPECT_NO

	def charset(self, name):
		logger.debug("Ask MUME to negotiate charset.")
		# Tell the server that we will negotiate the character set.
		self._options[CHARSET]["name"] = self.charsets[name]
		self.enableOption(CHARSET, LOCAL)
