
from bbultra2moodle.conv.Other import *
from bbultra2moodle.conv.Resource import *
import bbultra2moodle.utils as utils

class Quiz(Resource):
    def __init__(self, xml, quiz_questions, res_num):
        Resource.__init__(self, xml, res_num)

        self.questions = quiz_questions
        self.question_string = ",".join([str(q.id) for q in self.questions])
        self.feedback_id = utils.m_hash(self)
        self.res_num = res_num

    def _load(self):
        self.name = self.xml.find(".//assessment").attrib["title"]

        self.stamp = utils.generate_stamp()

        self.category_id = utils.m_hash(self.name, self.stamp)

        query = ".//presentation_material//mat_formattedtext"
        description = self.xml.find(query).text

        query = './/rubric[@view="All"]//mat_formattedtext'
        instructions = self.xml.find(query).text

        description = "" if not description else description
        instructions = "" if not instructions else instructions

        self.intro = description + "<br /><br />" + instructions

        self.intro = "" if self.intro == "<br /><br />" else self.intro
        while "@X@EmbeddedFile.requestUrlStub@X@bbcswebdav" in self.intro:
            self.intro = self.handle_embedded_stubfile(self.intro)
        self.type = "quiz"

    def handle_embedded_stubfile(self, text):
        if text.find("@X@EmbeddedFile.requestUrlStub@X@bbcswebdav") == -1:
            return text
        try:
            before, rest = text.split("@X@EmbeddedFile.requestUrlStub@X@bbcswebdav", 1)
            filename, after = rest.split('"', 1)

            after = '"' + after

            filename = utils.fix_filename(filename, self.res_num)
            filename = filename.strip("/")
            return before + "$@FILEPHP@$/" + filename + after
        except Exception as e:
            return text

