import gevent

from gevent import socket, queue
from urllib import unquote

import logging
logger = logging.getLogger("irc.tcp")


class Tcp(object):
    '''Handles TCP connections, `timeout` is in secs.'''
    def __init__(self, host, port, timeout=300):
        self._ibuffer = ''
        self._obuffer = ''
        self.iqueue = queue.Queue()
        self.oqueue = queue.Queue()
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket = self._create_socket()

    def _create_socket(self):
        return socket.socket()

    def connect(self):
        self._socket.connect((self.host, self.port))
        try:
            jobs = [gevent.spawn(self._recv_loop), gevent.spawn(self._send_loop)]
            gevent.joinall(jobs)
        finally:
            gevent.killall(jobs)

    def disconnect(self):
        self._socket.close()

    def _recv_loop(self):
        while True:
            data = self._socket.recv(4096)
            self._ibuffer += data
            while '\r\n' in self._ibuffer:
                line, self._ibuffer = self._ibuffer.split('\r\n', 1)
                self.iqueue.put(line)
            logger.debug("recv: " + line)

    def _send_loop(self):
        while True:
            line = self.oqueue.get().splitlines()[0][:500]
            try:
                self._obuffer += line.encode('ascii', 'backslashreplace') + '\r\n'
            except UnicodeDecodeError:
                self._obuffer += line + "\r\n"

            while self._obuffer:
                sent = self._socket.send(self._obuffer)
                self._obuffer = self._obuffer[sent:]
            logger.debug("send: " + line)
