
from bbultra2moodle.conv.Other import *
from bbultra2moodle.conv.Resource import *


class Forum(Resource):
    def _load(self):
        self.name = self.xml.find(".//TITLE").attrib["value"]
        self.introduction = self.xml.find(".//TEXT").text
        self.type = "forum"
