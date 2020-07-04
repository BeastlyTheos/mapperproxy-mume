﻿"""
Mume Remote Editing Protocol.
"""


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import logging
import os
import subprocess
import sys
import tempfile
import threading
from typing import AbstractSet, Callable, Mapping, MutableSequence

# Local Modules:
from .base import Protocol
from .telnet_constants import CR, CR_LF, LF
from ..utils import removeFile


MPI_INIT: bytes = b"~$#E"


logger: logging.Logger = logging.getLogger(__name__)


class MPIProtocol(Protocol):
	"""
	Implements support for the Mume remote editing protocol.

	Attributes:
		commandMap: A mapping of bytes to callables.
		editor: The program to use for editing received text.
		pager: The program to use for viewing received read-only text.
	"""

	states: AbstractSet[str] = frozenset(("data", "newline", "init", "command", "length", "body"))
	"""Valid states for the state machine."""

	def __init__(self, *args, **kwargs) -> None:
		self.outputFormat = kwargs.pop("outputFormat") if "outputFormat" in kwargs else None
		super().__init__(*args, **kwargs)
		self._state: str = "data"
		self._MPIBuffer: bytearray = bytearray()
		self._MPIThreads: MutableSequence[threading.Thread] = []
		self.commandMap: Mapping[bytes, Callable[[bytes], None]] = {b"E": self.edit, b"V": self.view}
		if sys.platform == "win32":
			self.editor: str = "notepad"
			self.pager: str = "notepad"
		else:
			self.editor: str = os.getenv("TINTINEDITOR", "nano -w")
			self.pager: str = os.getenv("TINTINPAGER", "less")

	@property
	def state(self) -> str:
		"""
		The state of the state machine.

		Valid values are in `states`.
		"""
		return self._state

	@state.setter
	def state(self, value: str) -> None:
		if value not in self.states:
			raise ValueError(f"'{value}' not in {tuple(sorted(self.states))}")
		self._state = value

	def edit(self, data: bytes) -> None:
		"""
		Edits text using the program defined in `editor`.

		Args:
			data: Received data from Mume, containing the session, description, and body of the text.
		"""
		session, description, body = data[1:].split(LF, 2)
		with tempfile.NamedTemporaryFile(prefix="mume_editing_", suffix=".txt", delete=False) as fileObj:
			fileName = fileObj.name
			fileObj.write(body.replace(CR, b"").replace(LF, CR_LF))
		lastModified = os.path.getmtime(fileName)
		if self.outputFormat == "tintin":
			print(f"MPICOMMAND:{self.editor} {fileName}:MPICOMMAND")
			input("Continue:")
		else:
			editorProcess = subprocess.Popen((*self.editor.split(), fileName))
			editorProcess.wait()
		if os.path.getmtime(fileName) == lastModified:
			# The user closed the text editor without saving. Cancel the editing session.
			response = b"C" + session
		else:
			with open(fileName, "rb") as fileObj:
				response = b"E" + session + LF + fileObj.read()
		response = response.replace(CR, b"").strip() + LF
		removeFile(fileName)
		self.write(MPI_INIT + b"E" + b"%d" % len(response) + LF + response)

	def view(self, data: bytes) -> None:
		"""
		Views text using the program defined in `pager`.

		Args:
			data: Received data from Mume, containing the text.
		"""
		with tempfile.NamedTemporaryFile(prefix="mume_viewing_", suffix=".txt", delete=False) as fileObj:
			fileName = fileObj.name
			fileObj.write(data.replace(CR, b"").replace(LF, CR_LF))
		if self.outputFormat == "tintin":
			print(f"MPICOMMAND:{self.pager} {fileName}:MPICOMMAND")
		else:
			pagerProcess = subprocess.Popen((*self.pager.split(), fileName))
			pagerProcess.wait()
			removeFile(fileName)

	def on_dataReceived(self, data: bytes) -> None:  # NOQA: C901
		appDataBuffer = []
		while data:
			if self.state == "data":
				appData, separator, data = data.partition(LF)
				appDataBuffer.append(appData + separator)
				if separator:
					self.state = "newline"
			elif self.state == "newline":
				if MPI_INIT.startswith(data[: len(MPI_INIT)]):
					# Data starts with some or all of the MPI_INIT sequence.
					self.state = "init"
				else:
					self.state = "data"
			elif self.state == "init":
				remaining = len(MPI_INIT) - len(self._MPIBuffer)
				self._MPIBuffer.extend(data[:remaining])
				data = data[remaining:]
				if self._MPIBuffer == MPI_INIT:
					# The final byte in the MPI_INIT sequence has been reached.
					if appDataBuffer:
						super().on_dataReceived(b"".join(appDataBuffer))
						appDataBuffer.clear()
					self._MPIBuffer.clear()
					self.state = "command"
				elif not MPI_INIT.startswith(self._MPIBuffer):
					# The Bytes in the buffer are not part of an MPI init sequence.
					data = bytes(self._MPIBuffer) + data
					self._MPIBuffer.clear()
					self.state = "data"
			elif self.state == "command":
				# The MPI command is a single byte.
				self._command, data = data[:1], data[1:]
				self.state = "length"
			elif self.state == "length":
				length, separator, data = data.partition(LF)
				self._MPIBuffer.extend(length)
				if not self._MPIBuffer.isdigit():
					logger.warning(f"Invalid data {self._MPIBuffer!r} in MPI length. Digit expected.")
					data = MPI_INIT + self._command + bytes(self._MPIBuffer) + separator + data
					del self._command
					self._MPIBuffer.clear()
					self.state = "data"
				elif separator:
					# The buffer contains the length of subsequent bytes to be received.
					self._length = int(self._MPIBuffer)
					self._MPIBuffer.clear()
					self.state = "body"
			elif self.state == "body":
				remaining = self._length - len(self._MPIBuffer)
				self._MPIBuffer.extend(data[:remaining])
				data = data[remaining:]
				if len(self._MPIBuffer) == self._length:
					# The final byte in the expected MPI data has been received.
					self.on_command(self._command, bytes(self._MPIBuffer))
					del self._command
					del self._length
					self._MPIBuffer.clear()
					self.state = "data"
		if appDataBuffer:
			super().on_dataReceived(b"".join(appDataBuffer))

	def on_command(self, command: bytes, data: bytes) -> None:
		"""
		Called when an MPI command is received.

		Args:
			command: The MPI command, consisting of a single byte.
			data: The payload.
		"""
		if command not in self.commandMap:
			logger.warning(f"Invalid MPI command {command!r}.")
			self.on_unhandledCommand(command, data)
		elif self.commandMap[command] is not None:
			thread = threading.Thread(target=self.commandMap[command], args=(data,), daemon=True)
			self._MPIThreads.append(thread)
			thread.start()

	def on_connectionMade(self) -> None:
		# Identify for Mume Remote Editing.
		self.write(MPI_INIT + b"I" + LF)

	def on_connectionLost(self) -> None:
		# Clean up any active editing sessions.
		for thread in self._MPIThreads:
			thread.join()
		self._MPIThreads.clear()

	def on_unhandledCommand(self, command: bytes, data: bytes) -> None:
		"""
		Called for commands for which no handler is installed.

		Args:
			command: The MPI command, consisting of a single byte.
			data: The payload.
		"""
		super().on_dataReceived(MPI_INIT + command + b"%d" % len(data) + LF + data)
