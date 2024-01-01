from bbultra2moodle.conv.Resource import Resource
from bbultra2moodle.conv.ContentItem import ContentItem
import bbultra2moodle.utils as utils
class Section(Resource):
    def __init__(self, document):
        if not document :
            self.number =0 
            self.visible = 1
            self.name = self.content = ''
            self.summary = ''
        else :
            ContentItem.__init__(self, document.xml)
            self.res_num = document.res_num
            self.number = document.number          
        self.id = utils.m_hash(self)
        self.section_id = utils.m_hash(self)
        self.type = "section"
        self.res_type = "section"
        self.mods = {}
    

    def _load(self):
        self.name = self.xml.find(".//TITLE").get("value")
        self.summary = self.xml.find(".//DESCRIPTION").get("value")
        is_visible = self.xml.find(".//FLAGS/ISAVAILABLE").get("value")
        if is_visible == 'true' :
            self.visible = 1
        else :
            self.visible = 0  
        


