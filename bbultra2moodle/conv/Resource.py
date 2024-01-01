from bbultra2moodle.conv.ContentItem import ContentItem
import bbultra2moodle.utils as utils
import urllib

class Resource(ContentItem):
    def __init__(self, xml, res_num):
        if self.__class__ == "Resource":
            raise NotImplementedError("Do not instantiate base class")

        self.res_num = res_num
        self.indent = 0

        ContentItem.__init__(self, xml)
        self.toc = False
        self.contentid = ''
        self.parentid = ''
        self.roottag = ''
        root = xml.getroot()
        if root.tag == 'CONTENT':
            self.contentid = root.attrib['id']
            self.parentid = self.xml.find(".//PARENTID").get("value")
        elif root.tag == 'COURSETOC' :
            self.toc = True    
        self.roottag  = root.tag
        av = "false"
        if xml.find(".//FLAGS/ISAVAILABLE") is not None :
            av = xml.find(".//FLAGS/ISAVAILABLE").get("value")
        if av == "false":
            self.visible = 0
        else:
            self.visible = 1
        self.id = utils.m_hash(self)
        self.section_id = utils.m_hash(self)


class Announcement(Resource):
    def _load(self):
        self.name = self.xml.find(".//TITLE").attrib["value"]
        self.alltext = self.xml.find(".//TEXT").text
        self.res_type = "html"
        self.reference = "2"  # TODO
        av = self.xml.find(".//FLAGS/ISAVAILABLE").get("value")
        if av == "false":
            self.visible = 0
        else:
            self.visible = 1
        self.type = "resource"
        
class Document(Resource):
    def _load(self):
        self.content_id = self.xml.getroot().get("value")
        self.name = self.xml.find(".//TITLE").get("value")
        self.alltext = self.xml.find(".//TEXT").text
        self.intro = self.xml.find(".//DESCRIPTION").get("value")
        self.ignore = False
        self.make_label = False
        self.make_section = False

        if not self.alltext:
            self.alltext = ""

        while "@X@EmbeddedFile.location@X@" in self.alltext:
            self.alltext = self.handle_embedded_file(self.alltext)
        while "@X@EmbeddedFile.requestUrlStub@X@" in self.alltext:
            self.alltext = self.handle_embedded_stubfile(self.alltext)

        content_handler = self.xml.find(".//CONTENTHANDLER").get("value")
        ignored_handlers = (
            "resource/x-bb-module-page",
      
        )

        if content_handler == "resource/x-bb-externallink":
            self.res_type = "file"
            self.reference = self.xml.find(".//URL").get("value")
        elif content_handler in ignored_handlers:
            self.ignore = True
        elif content_handler == "resource/x-bb-folder":
            # now check folder type
            folder_type = self.xml.find(".//FOLDERTYPE").get("value")
            if folder_type == "BB_FOLDER":
                self.ignore = True
                self.make_section = True
                if self.xml.find(".//PARENTID").attrib["value"] == "{unset id}":
                    self.make_section = False
            elif folder_type == "BB_PAGE":
                self.ignore = True
                self.make_label = True
                if self.xml.find(".//PARENTID").attrib["value"] == "{unset id}":
                    self.make_label = False
            else:
                print("FOLDER_TYPE  not handled " + folder_type)

        elif content_handler == "resource/x-bb-lesson":
            self.ignore = True
            self.make_section = True
        else:
            self.res_type = "html"

        for file_elem in self.xml.findall(".//FILE"):
            self.handle_file(file_elem)

        self.type = "resource"

    def handle_file(self, file_elem):
        orig_name = file_elem.find(".//NAME").text

        fixed_name = utils.fix_filename(orig_name, self.res_num)
        fixed_name = fixed_name.strip("/")
        fname = urllib.quote(fixed_name.encode("utf-8"))

        link_name = file_elem.find(".//LINKNAME").attrib["value"]

        f_link = '<a href = "$@FILEPHP@$/%s" title = %s>' % ((fname,) * 2)
        f_link = "Attached File: " + f_link + "%s</a>" % link_name

        self.alltext = "<br /><br />".join([self.alltext, f_link])

    def handle_embedded_file(self, text):
        before, rest = text.split("@X@EmbeddedFile.location@X@", 1)

        filename, after = rest.split('"', 1)

        after = '"' + after

        filename = utils.fix_filename(filename, self.res_num)

        return before + "$@FILEPHP@$/" + filename + after

    def handle_embedded_stubfile(self, text):
        if text.find("@X@EmbeddedFile.requestUrlStub@X@") == -1:
            return text
        try:
            before, rest = text.split("@X@EmbeddedFile.requestUrlStub@X@", 1)

            filename, after = rest.split('"', 1)

            after = '"' + after

            filename = utils.fix_filename(filename, self.res_num)
            return before + "$@FILEPHP@$/" + filename + after
        except Exception as e:
            print("exception ")
        return ""
