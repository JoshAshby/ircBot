import config as c
from channelBot import ChannelBot
import re
import requests
import urlparse

import gdata.youtube
import gdata.youtube.service
yt = gdata.youtube.service.YouTubeService()
yt.developer_key = c.GOOGLE_ID

import pyimgur
im = pyimgur.Imgur(c.IMGUR_CLIENT_ID)

import logging
logger = logging.getLogger("irc.sparkfunBot")

sparkfunMatch = ("sparkfun.com", "sprkfn.com", "sfe.io")
shortMatch    = ("binged.it",
                 "bit.ly",
                 "fb.me",
                 "goo.gl",
                 "is.gd",
                 "ow.ly",
                 "su.pr",
                 "tinyurl.com",
                 "tr.im")
youtubeMatch  = ("youtu.be", "youtube.com")
imgurMatch    = ("imgur.com")


class sparkfunBot(ChannelBot):
    echo     = False
    commands = True

    adminCmds = ["echo"]
    admins = ["JoshAshby-SFE"]

    def processMsg(self):
        logger.debug(self.who + " : " + self.said)

        try:
            url = self.saidHasURL()
            if url is not None:
                self.sparkfunURL(url)
                self.shortURL(url)
                self.youtubeURL(url)
                self.imgurURL(url)
        except:
            pass

        if self.echo:
            self.replyTo(self.who, self.said)

    def runCmd(self, cmd, action):
        if cmd == "author":
            self.reply("""JoshAshby 2013 <josh.ashby@sparkfun.com> \
Source code at: https://github.com/JoshAshby/ircBot""")

        elif cmd == "echo":
            if action == "on":
                self.echo = True

            else:
                self.echo = False

    def saidHasURL(self):
        loc = self.said.find("http")
        if loc is not -1:
            url = self.said[self.said.find("http"):].split(" ")[0]
            logger.debug("url:" + url)
            return urlparse.urlparse(url)
        return None

    def sparkfunURL(self, url):
        if any(part in str(url.netloc) for part in sparkfunMatch):
            returned = None
            try:
                action, id = url.path.lstrip("/").split("/")
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
        if any(part in str(url.netloc) for part in shortMatch):
            returned = None
            returned = requests.head(urlparse.urlunparse(url))
            assert returned.status_code in [301, 302]
            self.reply(returned.headers["location"])

    def youtubeURL(self, url):
        if any(part in str(url.netloc) for part in youtubeMatch):
            returned = None
            if any("v" in part[0] for part in urlparse.parse_qsl(url.query)):
                id = part[1]
            else:
                id = url.path.lstrip("/")

            entry = yt.GetYouTubeVideoEntry(video_id=id)
            self.reply(entry.media.title.text + " [ %s ]" % urlparse.urlunparse(url))

    def imgurURL(self, url):
        if any(part in str(url.netloc) for part in imgurMatch):
            id = url.path.split(".")[0]
            returned = im.get_image(id)
            if returned.title:
                reply = "%s [ %s " % (returned.title, returned.link)
                if returned.is_nsfw:
                    reply += "NSFW "
                reply += "]"
                self.reply(reply)


def getProduct(product):
    result = requests.get('http://www.sparkfun.com/products/' + product + '.json')
    assert result.status_code == 200
    return result.json()

def getNews(newsid):
    result = requests.get('http://www.sparkfun.com/news/' + newsid + '.json')
    assert result.status_code == 200
    return result.json()
