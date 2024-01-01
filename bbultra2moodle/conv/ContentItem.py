import xml.etree.ElementTree as ET
class ContentItem(object):
    def __init__(self, xml):
        if self.__class__ == "ContentItem":
            raise NotImplementedError("Do not instantiate base class")

        self.xml = xml
        self._load()