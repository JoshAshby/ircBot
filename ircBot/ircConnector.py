import gevent

from gevent import socket, queue
from gevent.ssl import wrap_socket

from tcp import Tcp
import ircExceptions as exc

import logging
logger = logging.getLogger("irc")

import config as c


class IrcConnector(object):
    _conn = None

    def __init__(self):
        self._nick     = c.nick
        self._channels = c.channels
        self._server   = c.server
        self._port     = c.port
        self._queue = queue.Queue()

        self._connect()

    def _connect(self):
        self._conn = Tcp(self._server, self._port)
        gevent.spawn(self._conn.connect)

        self.nick = self._nick
        self.cmd('USER', (self.nick, ' 3 ', '* ', "Wat Who Where"))

    def _disconnect(self):
        self._conn.disconnect()

    def _reconnect(self):
        self._disconnect()
        self._connect()

    def run(self):
        while True:
            line = self._conn.iqueue.get()
            if line[:4] == "ERROR":
                self._reconnect()
            try:
                prefix = ''
                trailing = []
                s = line

                if not s:
                    raise exc.IrcNullMessage('Received an empty line from the server.')

                if s[0] == ':':
                    prefix, s = s[1:].split(' ', 1)
                    name = prefix.split('!~')[0]

                if s.find(' :') != -1:
                    s, trailing = s.split(' :', 1)
                    args = s.split()
                    args.append(trailing)

                else:
                    args = s.split()

                command = args.pop(0)
                channel = args.pop(0)
                said    = ''.join(args)

                data = {"cmd": command,
                        "channel": channel,
                        "who": name,
                        "said": said}

                self._queue.put(data)
                logger.debug(data)

                if command == '433': # nick in use
                    self.nick = self.nick + '_'

                elif command == 'PING':
                    self.cmd('PONG', data["said"])

                elif command == '001':
                    if type(self._channels) is list:
                        for chan in self._channels:
                            self.cmd('JOIN', chan)
                    else:
                        self.cmd('JOIN', self._channels)

                elif command == 'ERROR':
                    self._reconnect()

                elif command == 'PRIVMSG':
                    if channel[0] != "#":
                        channel = name
                    self.msg(channel, name + ": "+str(line))

            except exc.IrcNullMessage:
                logger.debug("Null message")

    @property
    def nick(self):
        return self._nick

    @nick.setter
    def nick(self, value):
        self._nick = value
        self.cmd('NICK', self.nick)

    def join(self, channels=None):
        if channels is None:
            channels = self._channels
        if type(channels) is list:
            for chan in channels:
                self.cmd('JOIN', chan)
        else:
            self.cmd('JOIN', channels)

    def reply(self, msg):
        self.cmd('PRIVMSG', (self._channel + ' :' + msg))

    def msg(self, who, msg):
        self.cmd('PRIVMSG', (who + " :" + msg))

    def cmd(self, command, args):
        s = command + ' ' + ''.join(args)

        logger.debug(s)
        self._conn.oqueue.put(s)
