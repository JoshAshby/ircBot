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


class Irc(object):
    '''Provides a basic interface to an IRC server.'''
    _conn = None

    def __init__(self, nick, server, port, channel):
        self._nick    = nick
        self.channel  = channel
        self.lines    = queue.Queue()
        logger.info("Starting up...")

        self._conn = Tcp(server, port)
        gevent.spawn(self._conn.connect)

        logger.info("Connection started, finishing auth...")
        self.cmd('USER', (self.nick, ' 3 ', '* ', "WAT"))

    def _disconnect(self):
        self._conn.disconnect()

    def _parsemsg(self, s):
        '''
        Breaks a message from an IRC server into its prefix, command, 
        and arguments.
        '''
        prefix = ''
        trailing = []
        if not s:
            raise exc.IrcNullMessage('Received an empty line from the server.')
        if s[0] == ':':
            prefix, s = s[1:].split(' ', 1)
        if s.find(' :') != -1:
            s, trailing = s.split(' :', 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()
        command = args.pop(0)
        return prefix, command, args

    def serve(self):
        '''
        The main event loop.

        Data from the server is parsed here using `parsemsg`. Parsed events
        are put in the object's event queue, `self.events`.
        '''
        while True:
            logger.debug("here")
            line = self._conn.iqueue.get()
            try:
                prefix, command, args = self._parsemsg(line)

                line = {'prefix': prefix, 'command': command, 'args': args}
                self.lines.put(line)
                logger.debug(line)

                if command == '433': # nick in use
                    self.nick = self.nick + '_'

                if command == 'PING':
                    self.cmd('PONG', args)

                if command == '001':
                    self.cmd('JOIN', self.channel)

            except exc.IrcNullMessage:
                logger.debug("Null")

    @property
    def nick(self):
        return self._nick

    @nick.setter
    def nick(self, value):
        self._nick = value
        self.cmd('NICK', self.nick)

    def reply(self, prefix, msg):
        self.msg(prefix.split('!')[0], msg)

    def msg(self, target, msg):
        self.cmd('PRIVMSG', (target + ' :' + msg))

    def cmd(self, command, args, prefix=None):
        if prefix is not None:
            s = prefix + command + ' ' + ''.join(args)
        else:
            s = command + ' ' + ''.join(args)

        logger.debug(s)
        self._conn.oqueue.put(s)


if __name__ == '__main__':
    logger = setupLog()

    bot = Irc('JoshAshby', server='irc.freenode.net', port=6667, channel="#linuxandsci")
    job = gevent.spawn(bot.serve)
    job.join()
