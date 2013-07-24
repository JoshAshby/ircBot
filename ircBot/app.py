"""
Basic IRC bot in python powered by gevent. Most of this is currently borrowed
  from https://gist.github.com/maxcountryman/676306 but is slowly being
  rewritten or heavily modified
"""
import gevent

from ircConnector import IrcConnector
from dispatch import BotDispatch

from log import setupLog

import config as c


from channelBot import ChannelBot
import re
import requests


sparkfunMatch = re.compile('https?://(?:www\.)?(?:sparkfun|sprkfn|sfe)\.(?:com|io)(?:/)(.*)/(\d*)')
class RegularBot(ChannelBot):
    echo     = False
    commands = True

    adminCommands = ["echo"]
    admins = ["JoshAshby-SFE"]

    def processMsg(self):
        logger.debug(self.who + " : " + self.said)

        stuff = sparkfunMatch.match(self.said)
        if stuff:
            returned = None
            action, id = stuff.groups()
            if id is not "":
                try:
                    if action == "products" or action == "p":
                        returned = getProduct(id)
                        self.reply("%s [ http://sfe.io/p/%s ]" % \
                            (returned["name"],
                             id))
                    if action == "news" or action == "n":
                        returned = getNews(id)
                        self.reply("*%s* by %s [ http://sfe.io/n/%s ]" % \
                            (returned["news_title"],
                             returned["news_author"]
                             id))

                except AssertionError:
                    self.replyTo(self.who, "That is not a valid %s id" % action)

        if self.echo:
            self.replyTo(self.who, self.said)

    def runCmd(self, cmd, action):
        if cmd in self.adminCommands and self.who not in self.admins:
            self.replyTo(self.who, "You can't use this action! :P")
            return

        if cmd == "author":
            self.reply("Josh Ashby 2013 <josh.ashby@sparkfun.com>")

        elif cmd == "echo":
            if action == "on":
                self.echo = True

            else:
                self.echo = False


def getProduct(product):
    result = requests.get('http://www.sparkfun.com/products/' + product + '.json')
    assert result.status_code == 200
    return result.json()

def getNews(newsid):
    result = requests.get('http://www.sparkfun.com/news/' + newsid + '.json')
    assert result.status_code == 200
    return result.json()


#class JoshBot(ChannelBot):
    #personal = True
    #def processMsg(self, who, said):
        #logger.debug("Hi Josh! " + said)
        #self.reply("Hi Josh! " + said)


if __name__ == '__main__':
    logger = setupLog()

    connection = IrcConnector()
    connection.run()

    bots = [
      RegularBot("#josh-test"),
      #JoshBot("JoshAshby-SFE")
    ]

    dispatcher = BotDispatch(bots, connection)
    dispatcher.dispatch()
