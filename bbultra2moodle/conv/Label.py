

from bbultra2moodle.conv.Other import *
from bbultra2moodle.conv.Resource import *
import bbultra2moodle.utils as utils

class Label(Resource):
    def __init__(self, document):
        self.name = self.content = document.name
        self.res_num = document.res_num
        self.id = utils.m_hash(self)
        self.section_id = utils.m_hash(self)
        self.type = "resource"
        self.res_type = 'html'
        av = document.xml.find(".//FLAGS/ISAVAILABLE").get("value")
        if av == "false":
            self.visible = 0
        else:
            self.visible = 1
        self.description = ''
        self.intro =''
        self.page= []
        self.indent =0