

from bbultra2moodle.conv.Other import *
from bbultra2moodle.conv.Resource import *
from bbultra2moodle.conv.ContentItem import ContentItem
import bbultra2moodle.utils as utils
import sys
import re
class Question(ContentItem):
    def __init__(self, xml, res_num):
        if self.__class__ == "Question":
            raise NotImplementedError("Do not instantiate base class")
        self.res_num = res_num
        ContentItem.__init__(self, xml)

        if not self.name:
            self.name = "________"

        self.name = re.sub(r"<.*?>", "", self.name).strip()

        query = './/flow[@class="FILE_BLOCK"]//matapplication'

        for elem in self.xml.findall(query):
            self.image = utils.fix_filename(elem.attrib["label"], res_num)

        self.stamp = utils.generate_stamp()
        self.id = utils.m_hash(self)

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


class FillInTheBlankQuestion(Question):
    def _load(self):
        self.name = self.xml.find(".//presentation//mat_formattedtext").text
        while "@X@EmbeddedFile.requestUrlStub@X@bbcswebdav" in self.name:
            self.name = self.handle_embedded_stubfile(self.name)
        self.text = self.name

        self.answers = []

        for answer_text in [e.text for e in self.xml.findall(".//varequal")]:
            while "@X@EmbeddedFile.requestUrlStub@X@bbcswebdav" in answer_text:
                answer_text = self.handle_embedded_stubfile(answer_text)
            answer = {}
            answer["answer_text"] = answer_text
            answer["points"] = 1
            answer["id"] = utils.m_hash(answer)

            self.answers.append(answer)

class EssayQuestion(Question):
    def _load(self):
        self.name = self.xml.find(".//presentation//mat_formattedtext").text
        while "@X@EmbeddedFile.requestUrlStub@X@bbcswebdav" in self.name:
            self.name = self.handle_embedded_stubfile(self.name)
        self.text = self.name
        self.answer_id = utils.m_hash(self)


class ShortResponseQuestion(EssayQuestion):
    pass


class TrueFalseQuestion(Question):
    def _load(self):
        self.name = self.xml.find(".//presentation//mat_formattedtext").text
        while "@X@EmbeddedFile.requestUrlStub@X@bbcswebdav" in self.name:
            self.name = self.handle_embedded_stubfile(self.name)
        self.text = self.name

        query = './/itemfeedback[@ident="correct"]//mat_formattedtext'

        true_fb_el = self.xml.find(query)
        false_fb_el = self.xml.find(query.replace('"c', '"inc'))

        self.true_feedback = true_fb_el.text if true_fb_el is not None else ""
        self.false_feedback = false_fb_el.text if false_fb_el is not None else ""

        answer_query = './/respcondition[@title="correct"]//varequal'

        answer_elem = self.xml.find(answer_query)

        if answer_elem is not None:
            a = answer_elem.text

            self.true_points, self.false_points = (1, 0) if a == "true" else (0, 1)

            self.true_answer_id = utils.m_hash(self, self.true_points)
            self.false_answer_id = utils.m_hash(self, self.false_points)
        else:
            # Survey
            # TODO: Make this multichoice
            self.true_points, self.false_points = (1, 0)

            self.true_answer_id = utils.m_hash(self, self.true_points)
            self.false_answer_id = utils.m_hash(self, self.false_points)


class MultipleChoiceQuestion(Question):
    def _load(self):
        self.name = self.xml.find(".//presentation//mat_formattedtext").text
        while "@X@EmbeddedFile.requestUrlStub@X@bbcswebdav" in self.name:
            self.name = self.handle_embedded_stubfile(self.name)
        self.text = self.name

        query = './/itemfeedback[@ident="correct"]//mat_formattedtext'

        try:
            self.cor_fb = self.xml.find(query).text
            self.incor_fb = self.xml.find(query.replace('"c', '"inc')).text
        except AttributeError:
            # Survey
            self.cor_fb = ""
            self.incor_fb = ""
        except:
            print("Unexpected error:", sys.exc_info()[0])

        self.answers = []

        self.build_answers()

        self.answer_string = ",".join([str(a["id"]) for a in self.answers])

    def build_answers(self):
        self.single_answer = 1

        answer_query = ".//render_choice//response_label"

        for answer_elem in self.xml.findall(answer_query):
            answer = {}
            answer["ident"] = answer_elem.attrib["ident"]
            answer["answer_text"] = answer_elem.find(".//mat_formattedtext").text

            # Filter out blank choices
            if not answer["answer_text"]:
                continue
            while (
                "@X@EmbeddedFile.requestUrlStub@X@bbcswebdav" in answer["answer_text"]
            ):
                answer["answer_text"] = self.handle_embedded_stubfile(
                    answer["answer_text"]
                )

            self.answers.append(answer)

        query = './/respcondition[@title="correct"]//varequal'

        correct_elem = self.xml.find(query)

        if correct_elem is not None:
            correct_ident = correct_elem.text

            for answer in self.answers:
                if answer["ident"] == correct_ident:
                    answer["points"] = 1
                    answer["feedback"] = self.cor_fb
                else:
                    answer["points"] = 0
                    answer["feedback"] = self.incor_fb

                answer["id"] = utils.m_hash(answer)
        else:
            for answer in self.answers:
                answer["points"] = 1
                answer["feedback"] = self.cor_fb
                answer["id"] = utils.m_hash(answer)


class EitherOrQuestion(MultipleChoiceQuestion):
    ans_types = {
        "yes_no": ("Yes", "No"),
        "agree_disagree": ("Agree", "Disagree"),
        "right_wrong": ("Right", "Wrong"),
        "true_false": ("True", "False"),
    }

    def build_answers(self):
        self.single_answer = 1

        answer_query = './/respcondition[@title="correct"]//varequal'
        answer_elem = self.xml.find(answer_query)

        if answer_elem is not None:
            answer = answer_elem.text

            ans_type = answer.split(".")[0]

            true_points, false_points = (1, 0) if answer.endswith("true") else (0, 1)

            right_ans = {}
            right_ans["answer_text"] = self.ans_types[ans_type][0]
            right_ans["points"] = true_points

            if true_points == 1:
                right_ans["feedback"] = self.cor_fb
            else:
                right_ans["feedback"] = self.incor_fb

            right_ans["id"] = utils.m_hash(right_ans)  # Fix m_hash

            wrong_ans = {}
            wrong_ans["answer_text"] = self.ans_types[ans_type][1]
            wrong_ans["points"] = false_points

            if false_points == 1:
                wrong_ans["feedback"] = self.cor_fb
            else:
                wrong_ans["feedback"] = self.incor_fb

            wrong_ans["id"] = utils.m_hash(wrong_ans)  # Fix_mhash
        else:
            # TODO: Improve
            # Survey
            right_ans = {}
            right_ans["answer_text"] = "Agree"
            right_ans["points"] = 1
            right_ans["feedback"] = ""
            right_ans["id"] = utils.m_hash(right_ans)  # Fix m_hash

            wrong_ans = {}
            wrong_ans["answer_text"] = "Disagree"
            wrong_ans["points"] = 0
            wrong_ans["feedback"] = ""
            wrong_ans["id"] = utils.m_hash(wrong_ans)  # Fix_mhash

        self.answers = (right_ans, wrong_ans)


class MultipleAnswerQuestion(MultipleChoiceQuestion):
    def build_answers(self):
        self.single_answer = 0

        answer_query = ".//render_choice//response_label"

        for answer_elem in self.xml.findall(answer_query):
            answer = {}
            answer["ident"] = answer_elem.attrib["ident"]
            answer["answer_text"] = answer_elem.find(".//mat_formattedtext").text
            # Filter out blank choices
            if not answer["answer_text"]:
                continue
            while (
                "@X@EmbeddedFile.requestUrlStub@X@bbcswebdav" in answer["answer_text"]
            ):
                answer["answer_text"] = self.handle_embedded_stubfile(
                    answer["answer_text"]
                )

            self.answers.append(answer)

        query = './/respcondition[@title="correct"]//and/varequal'
        correct_idents = [a.text for a in self.xml.findall(query)]

        for answer in self.answers:
            if answer["ident"] in correct_idents:
                answer["points"] = 1
                answer["feedback"] = self.cor_fb
            else:
                answer["points"] = 0
                answer["feedback"] = self.incor_fb

            answer["id"] = utils.m_hash(answer)


class OpinionScaleQuestion(MultipleChoiceQuestion):
    pass


class MatchingQuestion(Question):
    def _load(self):
        self.name = self.xml.find(".//presentation//mat_formattedtext").text
        while "@X@EmbeddedFile.requestUrlStub@X@bbcswebdav" in self.name:
            self.name = self.handle_embedded_stubfile(self.name)
        self.text = self.name

        self.answers = []

        ident_query = './/flow[@class="RESPONSE_BLOCK"]//response_lid'
        text_query = './/flow[@class="RESPONSE_BLOCK"]//mat_formattedtext'

        idents = self.xml.findall(ident_query)
        texts = self.xml.findall(text_query)

        for n, i in enumerate(self.xml.findall(ident_query)):
            answer = {}
            answer["ident"] = idents[n].attrib["ident"]
            answer["question_text"] = texts[n].text

            labels = idents[n].findall(".//response_label")

            answer["choice_idents"] = tuple([l.attrib["ident"] for l in labels])

            self.answers.append(answer)

        answer_query = './/flow[@class="RIGHT_MATCH_BLOCK"]//mat_formattedtext'

        answer_texts = [a.text for a in self.xml.findall(answer_query)]

        for match in self.xml.findall(".//varequal"):
            question_ident = match.attrib["respident"]
            answer_ident = match.text

            for answer in self.answers:
                if answer["ident"] == question_ident:
                    i = answer["choice_idents"].index(answer_ident)

                    answer["answer_text"] = answer_texts[i]

                    break

        for answer in self.answers:
            answer["id"] = utils.m_hash(answer)


class OrderingQuestion(Question):
    def _load(self):
        self.name = self.xml.find(".//presentation//mat_formattedtext").text
        while "@X@EmbeddedFile.requestUrlStub@X@bbcswebdav" in self.name:
            self.name = self.handle_embedded_stubfile(self.name)
        self.text = self.name

        self.answers = []

        answer_query = ".//render_choice//response_label"

        for answer_elem in self.xml.findall(answer_query):
            answer = {}
            answer["ident"] = answer_elem.attrib["ident"]
            answer["question_text"] = answer_elem.find(".//mat_formattedtext").text

            self.answers.append(answer)

        query = './/respcondition[@title="correct"]//varequal'
        ordered_ident_elems = self.xml.findall(query)

        for n, ordered_ident_elem in enumerate(ordered_ident_elems):
            for answer in self.answers:
                if answer["ident"] == ordered_ident_elem.text:
                    answer["answer_text"] = n + 1

                    break

        for answer in self.answers:
            answer["id"] = utils.m_hash(answer)

