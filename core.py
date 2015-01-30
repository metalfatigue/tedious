import requests, traceback, sys, json
from lxml import html
import traceback
import sys

class Groute(object):
    SETTINGS = json.load(open("settings.json"))
    ROUTER = SETTINGS["settings"]["router"]

    stat = {"page": "", "tree": ""}
    sample = None
    stat_list = []
    frames = {}
  
    def __init__(self):
        self.router = requests.get(self.ROUTER["ip"])
  
    def reboot(self):
        r = requests.post(self.ROUTER["pages"]["reboot"],
                          data=self.ROUTER["creds"],
                          headers=self.ROUTER["header"],
                          auth=(self.ROUTER["username"],
                                self.ROUTER["password"]))
        ## Add logging here
        return r

    def active_clients(self):
        return requests.get(self.ROUTER["pages"]["active_clients"],
                            auth=(self.ROUTER["username"], 
                                  self.ROUTER["password"]))

    def stats(self):
        index = html.fromstring(self.router.text)
        frame = {"main":"", "page":"", "tree":"", "stats": [], "latest": None}
        frame["main"] = self.get_frame('view', index.xpath('//frame'))[0]
        frame["page"] = requests.get(self.router.url + frame["main"].get('src'))
        frame["tree"] = html.fromstring(frame["page"].text)
        temp = self.remove_frame_headers(self.extract_fields(frame["tree"]))
        return zip(temp[::2],temp[1::2])

    def remove_extra_info(self):
        return self.stats()[:18]

    def get_stat_name(self, stat):
        return stat.getchildren()[0].getchildren()[0].text

    def get_stat_value(self, stat, stat_name):
        if stat_name in ['Name Servers', 'Default Gateway']:
            return self.get_stat_name(stat).strip()
        else:
            return stat.getchildren()[0].text.strip()

    def raw_stat_to_dict(self, stat):
        stat_name = self.get_stat_name(stat[0])
        stat_value = self.get_stat_value(stat[1], stat_name)
        return { stat_name : stat_value }

    def __str__(self):
        print "\nCurrent status:\n"
        return "\n".join("{}: {}".format(k, v) for k,v in self.stats_pp().iteritems())

    def stats_pp(self):
        return reduce(lambda x,y: x.update(y) or x, 
                      map(self.raw_stat_to_dict, self.remove_extra_info()), 
                      {})

    def to_nonbreaking(self, val):
        return val.replace("\xc2\xa0", " ")
  
    def get_frame(self, frame_name, frames):
        return filter(lambda x: x.get('name') == frame_name, frames)
  
    def remove_frame_headers(self, stats):
        return filter(lambda x: 'background' not in x.attrib, stats)

    def extract_fields(self,stats):
        return filter(lambda x: x.getchildren()[0].getchildren() is not None, 
                      stats.xpath("//tr//td")[1:])

class Page(object):
    pass

g = Groute()
# h = html.fromstring(g.active_clients().text)
