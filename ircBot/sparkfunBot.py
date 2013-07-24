from channelBot import ChannelBot
import re
import requests

import logging
logger = logging.getLogger("irc.sparkfunBot")

sparkfunMatch = re.compile('https?://(?:www\.)?(?:sparkfun|sprkfn|sfe)\.(?:com|io)(?:/)(.*)/(\d*)')
shortMatch    = re.compile('http(s|)?://(binged\.it|bit\.ly|fb\.me|goo\.gl|is\.gd|ow\.ly|su\.pr|tinyurl\.com|tr\.im|youtu\.be)(/[^\s,;\.]+)')
youtubeMatch  = re.compile('https?://(?:www\.)(?:youtu\.be|youtube\.com)/.*')


class sparkfunBot(ChannelBot):
    echo     = False
    commands = True

    adminCmds = ["echo"]
    admins = ["JoshAshby-SFE"]

    def processMsg(self):
        logger.debug(self.who + " : " + self.said)

        url = self.saidHasURL()
        if url is not None:
            self.sparkfunURL(url)
            self.shortURL(url)
            self.youtubeURL(url)

        if self.echo:
            self.replyTo(self.who, self.said)

    def runCmd(self, cmd, action):
        if cmd == "author":
            self.reply("""JoshAshby 2013 <josh.ashby@sparkfun.com>\r\n
                          Source code at: https://github.com/JoshAshby/ircBot""")

        elif cmd == "echo":
            if action == "on":
                self.echo = True

            else:
                self.echo = False

    def saidHasURL(self):
        try:
            url = self.said[self.said.find("http"):].split(" ")[0]
            logger.debug(url)
            return url
        except:
            return None

    def sparkfunURL(self, url):
        stuff = sparkfunMatch.match(url)
        if stuff:
            returned = None
            action, id = stuff.groups()
            if id is not "":
                try:
                    if action == "products" or action == "p":
                        returned = getProduct(id)
                        self.reply("%s [ http://sfe.io/p%s ]" % \
                            (returned["name"],
                             id))
                    if action == "news" or action == "n":
                        returned = getNews(id)
                        self.reply("%s by %s [ http://sfe.io/n%s ]" % \
                            (returned["news_title"],
                             returned["news_author"],
                             id))

                except AssertionError:
                    self.replyTo(self.who, "That is not a valid %s id" % action)

    def shortURL(self, url):
        stuff = shortMatch.match(url)
        if stuff:
            returned = None
            schema, domain, path = stuff.groups()
            returned = requests.head("http%s://" %(schema) + domain+path)
            assert returned.status_code in [301, 302]
            self.reply(returned.headers["location"])

    def youtubeURL(self, url):
        stuff = youtubeMatch.match(url)
        if stuff:
            returned = None
            try:
                params = urlparse.parse_qsl(urlparse.urlparse(url).query)
                for param in params:
                    if param[0] == "v":
                      id = param[1]
            except:
                id = stuff.group(1)
            returned = requests.get("http://gdata.youtube.com/feeds/api/videos/"+id)
            assert returned.status_code == 200
            logger.debug(returned.json())


def getProduct(product):
    result = requests.get('http://www.sparkfun.com/products/' + product + '.json')
    assert result.status_code == 200
    return result.json()

def getNews(newsid):
    result = requests.get('http://www.sparkfun.com/news/' + newsid + '.json')
    assert result.status_code == 200
    return result.json()
