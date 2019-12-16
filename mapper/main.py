# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Built-in Modules:
from datetime import datetime
import logging
import os
import socket
try:
	import ssl
except ImportError:
	ssl = None
import threading

# Local Modules:
from .utils import getDirectoryPath, removeFile, touch

SERVER_DATA, MM2_DATA = (0, 1)

LISTENING_STATUS_FILE = os.path.join(getDirectoryPath("."), "mapper_ready.ignore")


logger = logging.getLogger(__name__)


def record(type, data):
	print("from %s on %s. %s" % (
		type,
		datetime.now().strftime("%H:%M.%S"),
		data,
	))


class Proxy(threading.Thread):
	def __init__(self, client, server):
		threading.Thread.__init__(self)
		self.name = "Proxy"
		self._client = client
		self._server = server
		self.finished = threading.Event()

	def close(self):
		self.finished.set()

	def run(self):
		while not self.finished.isSet():
			try:
				data = self._client.recv(4096)
				self._server.sendall(data)
			except socket.timeout:
				continue
			except EnvironmentError:
				self.close()
				continue
			if not data:
				self.close()
			record("here", data)
			if data == b'':
				self.close()
				exit()
				raise Exception("closing")


class Server(threading.Thread):
	def __init__(self, client, server):
		threading.Thread.__init__(self)
		self.name = "Server"
		self._client = client
		self._server = server
		self.finished = threading.Event()

	def close(self):
		self.finished.set()

	def run(self):
		while not self.finished.isSet():
			try:
				data = self._server.recv(4096)
				self._client.sendall(data)
			except EnvironmentError:
				self.close()
				continue
			if not data:
				self.close()
				continue
			try:
				record("SERVER", data)
				if data == b'':
					self.close()
			except EnvironmentError:
				self.close()
				continue


class MockedSocket(object):
	def connect(self, *args):
		pass

	def getpeercert(*args):
		return {"subject": [["commonName", "mume.org"]]}

	def shutdown(self, *args):
		pass

	def close(self, *args):
		pass

	def sendall(self, *args):
		pass


def main(
		localHost,
		localPort,
		remoteHost,
		remotePort,
		noSsl
):
	# initialise client connection
	proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	proxySocket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
	proxySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	proxySocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	proxySocket.bind((localHost, localPort))
	proxySocket.listen(1)
	touch(LISTENING_STATUS_FILE)
	clientConnection, proxyAddress = proxySocket.accept()
	clientConnection.settimeout(1.0)
	# initialise server connection
	serverConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverConnection.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
	serverConnection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	if not noSsl and ssl is not None:
		serverConnection = ssl.wrap_socket(serverConnection)
		clientConnection = ssl.wrap_socket(clientConnection)
	try:
		serverConnection.connect((remoteHost, remotePort))
	except TimeoutError:
		try:
			clientConnection.sendall(b"\r\nError: server connection timed out!\r\n")
			clientConnection.sendall(b"\r\n")
			clientConnection.shutdown(socket.SHUT_RDWR)
		except EnvironmentError:
			pass
		clientConnection.close()
		removeFile(LISTENING_STATUS_FILE)
		return
	if not noSsl and ssl is not None:
		# Validating server identity with ssl module
		# See https://wiki.python.org/moin/SSL
		for field in serverConnection.getpeercert()["subject"]:
			if field[0][0] == "commonName":
				certhost = field[0][1]
				if certhost != "mume.org":
					raise ssl.SSLError("Host name 'mume.org' doesn't match certificate host '{}'".format(certhost))
	proxyThread = Proxy(
		client=clientConnection,
		server=serverConnection,
	)
	serverThread = Server(
		client=clientConnection,
		server=serverConnection,
	)
	serverThread.start()
	proxyThread.start()
	proxyThread.join()
	return
	serverThread.join()
	try:
		serverConnection.shutdown(socket.SHUT_RDWR)
	except EnvironmentError:
		pass
	try:
		clientConnection.sendall(b"\r\n")
		proxyThread.close()
		clientConnection.shutdown(socket.SHUT_RDWR)
	except EnvironmentError:
		pass
	proxyThread.join()
	serverConnection.close()
	clientConnection.close()
	removeFile(LISTENING_STATUS_FILE)
