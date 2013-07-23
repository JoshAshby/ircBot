"""
Basic IRC bot in python powered by gevent. Most of this is currently borrowed
  from https://gist.github.com/maxcountryman/676306 but is slowly being
  rewritten or heavily modified
"""

import gevent

from gevent import socket, queue
from gevent.ssl import wrap_socket

from log import setupLog
from tcp import Tcp
import ircExceptions as exc


class IrcConnector(object):
    _conn = None

    def __init__(self, nick, server, port, channel):
        self._nick    = nick
        self._channel = channel
        self._server  = server
        self._port    = port
        self.lines    = queue.Queue()
        logger.info("Starting up...")

        self._connect()

    def _connect(self):
        self._conn = Tcp(self._server, self._port)
        gevent.spawn(self._conn.connect)

        logger.info("Connection started, finishing auth...")
        self.nick = self._nick
        self.cmd('USER', (self.nick, ' 3 ', '* ', "Wat Who Where"))

    def _disconnect(self):
        self._conn.disconnect()

    def reconnect(self):
        self._disconnect()
        self._connect()

    def serve(self):
        while True:
            line = self._conn.iqueue.get()
            try:
                prefix = ''
                trailing = []
                s = line

                if not s:
                    raise exc.IrcNullMessage('Received an empty line from the server.')

                if s[0] == ':':
                    prefix, s = s[1:].split(' ', 1)
                    name = prefix.split('!~')[0]

                logger.debug("said: " + s)

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

                self.lines.put(data)
                logger.debug(data)

                if command == '433': # nick in use
                    self.nick = self.nick + '_'

                elif command == 'PING':
                    self.cmd('PONG', data["said"])

                elif command == '001':
                    self.cmd('JOIN', self._channel)

                elif command == 'ERROR':
                    self.reconnect()

                elif command == 'PRIVMSG':
                    self.msg(channel, name + ": "+str(line))

            except exc.IrcNullMessage:
                logger.debug("Null")

    @property
    def nick(self):
        return self._nick

    @nick.setter
    def nick(self, value):
        self._nick = value
        self.cmd('NICK', self.nick)

    def reply(self, msg):
        self.cmd('PRIVMSG', (self._channel + ' :' + msg))

    def msg(self, who, msg):
        if who[0] != "#":
            who = "#" + who
        self.cmd('PRIVMSG', (who + " :" + msg))

    def cmd(self, command, args):
        s = command + ' ' + ''.join(args)

        logger.debug(s)
        self._conn.oqueue.put(s)


if __name__ == '__main__':
    logger = setupLog()

    bot = IrcConnector(nick='JoshAshby',
                       server='irc.freenode.net',
                       port=6667,
                       channel="#josh-test")

    job = gevent.spawn(bot.serve)
    job.join()
