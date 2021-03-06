import gevent


class BotDispatch(object):
    def __init__(self, bots, connection):
        self._conn   = connection
        self._bots   = bots
        self._queues = []
        self._jobs   = []

        for bot in self._bots:
            bot._sendMsgQueue = self._conn._outputQueue
            self._queues.append(bot._msgQueue)
            self._jobs.append(gevent.spawn(bot.watch))

    def addBots(self, bots):
        for bot in bots:
            bot._sendMsgQueue = self._conn._outputQueue
            self._queues.append(bot._msgQueue)
            self._jobs.append(gevent.spawn(bot.watch))

    def dispatch(self):
      job = gevent.spawn(self._run)
      try:
          job.join()
      except KeyboardInterrupt:
          pass
      finally:
          job.kill()

    def _run(self):
        while True:
            what = self._conn._queue.get()
            for bot in self._queues:
                bot.put(what)
