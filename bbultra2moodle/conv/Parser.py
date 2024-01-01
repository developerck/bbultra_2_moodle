import zipfile
import time
from lxml import etree
import io
import shutil
import re
import sys
from bbultra2moodle.conv.Forum import Forum
from bbultra2moodle.conv.Quiz import Quiz
from bbultra2moodle.conv.Section import Section
from bbultra2moodle.conv.Label import Label
from bbultra2moodle.conv.Other import *
from bbultra2moodle.conv.Resource import *
from bbultra2moodle.conv.Question import *
import bbultra2moodle.utils as utils

class Parser(object):
    def __init__(self, archive_filename):
        self.archive_filename = archive_filename
        self.timestamp = str(time.time()).split(".")[0]
        try:
            self.zip = zipfile.ZipFile(self.archive_filename, "r")
        except zipfile.error:
            raise zipfile.error(self.archive_filename)
        utils.logme("Parsing Maninfest")
        self.manifest = self.parse_manifest()
        self.course_setting = {}
        self.used = {"labels":[],"quizzes":[],'forums':[],"resources":[]}
        self.forums = {}
        self.labels = {}
        self.quizzes = {}
        self.resources = {}
        self.sections = {}
        self.assesment= {}
        self.links={}
        self.areas = {}
        self.questions = {}
        self.questions["essay"] = []
        self.questions["matching"] = []
        self.questions["truefalse"] = []
        self.questions["shortanswer"] = []
        self.questions["multichoice"] = []
        self.parent_resnum = {}
        self.contentids = {}

        # adding default section
        self.sections["0"] = Section("")
        utils.logme("Converting Resources from manifest")
        self.convert_resources()
        utils.logme("Resources Converted")
        utils.logme("CA : Content areas START")
        self.convert_content_areas()
        utils.logme("CA : Content areas END")
        utils.logme("Section work completed")
        self.quiz_category_stamp = utils.generate_stamp()
        self.quiz_category_id = utils.m_hash(self.quiz_category_stamp)
        self.has_questions = any(self.questions.values())
        utils.logme("Question Work completed")
        self.zip.close()

    def parse_manifest(self):
        try:
            manifest_bytes = self.zip.read("imsmanifest.xml")
            manifest_str = manifest_bytes.decode("utf-8")
            namespace = 'xmlns:bb="http://www.blackboard.com/content-packaging/"'

            manifest_str = manifest_str.replace(namespace, "")
            manifest_str = (
                manifest_str.replace("bb:", "")
                .replace("xml:", "")
                .replace('encoding="UTF-8"', "")
            )
            return etree.fromstring(manifest_str)
        except:
            utils.logerror("error in parsing manifest")
            return ""

    def convert_resources(self):
        utils.logme("CR : Converting Resource ")
        for resource in self.manifest.iterfind(".//resource"):
            dat_name = resource.get("file")
            try:
                xml = etree.parse(self.zip.open(dat_name))
            except KeyError:
                utils.logerror("Error in finding " + dat_name)
                continue

            res_num = dat_name.replace(".dat", "")
            res_type = resource.get("type")
            utils.logme("CR : res_num " + res_num + " | type " + res_type)

            if res_type == "course/x-bb-coursesetting":
                self.convert_course_settings(xml)
            elif res_type == "course/x-bb-courseassessment":
                self.convert_course_assesment(xml, res_num)
            elif res_type == "resource/x-bb-link":
                self.convert_course_links(xml, res_num)
            elif res_type == "resource/x-bb-discussionboard":
                self.forums[res_num] = Forum(xml, res_num)
            elif res_type == "resource/x-bb-announcement":
                self.resources[res_num] = Announcement(xml, res_num)
            elif res_type == "assessment/x-bb-qti-test":
                quiz_questions = self.convert_questions(xml, res_num)
                self.quizzes[res_num] = Quiz(xml, quiz_questions, res_num)
            elif res_type == "assessment/x-bb-qti-survey":
                quiz_questions = self.convert_questions(xml, res_num)
                self.quizzes[res_num] = Survey(xml, quiz_questions, res_num)
            elif res_type == "assessment/x-bb-qti-pool":
                quiz_questions = self.convert_questions(xml, res_num)
                self.quizzes[res_num] = Pool(xml, quiz_questions, res_num)
            elif res_type == "resource/x-bb-document":
                self.convert_resources_document(xml, res_num)
            else:
                utils.logerror(
                    "CR : res_type not implemented " + res_type + " | " + dat_name
                )

    def convert_course_settings(self, xml):
        self.course_setting["fullname"] = xml.find(".//TITLE").get("value")
        self.course_setting["shortname"] = xml.find(".//COURSEID").get("value")
        self.course_setting["description"] = xml.find(".//DESCRIPTION").get("value")
        if self.course_setting["description"] is None :
            self.course_setting["description"] = ''
        self.course_setting['timestamp'] = self.timestamp
        self.course_setting["course_created"] = self.timestamp
        self.course_setting["start_date"] = self.timestamp
      
        
        av = xml.find(".//FLAGS/ISAVAILABLE").get("value")
        if av == "true":
            self.course_setting["visible"] = 1
        else:
            self.course_setting["visible"] = 0
        category_elems = xml.findall(".//CLASSIFICATION")
        self.course_setting["primary_category"] = category_elems[0].get("value")
        try:
            self.course_setting["secondary_category"] = category_elems[1].get("value")
        except IndexError:
            self.course_setting["secondary_category"] = ""
    
    def convert_course_assesment(self, xml, res_num):
        asmtid = xml.find(".//ASMTID").get("value")
        self.assesment[res_num] = {"asmtid":asmtid,"xml":xml,"res_num":res_num}
        
    def convert_course_links(self, xml, res_num):
        ref = xml.find(".//REFERRER").get("id")
        ref_to = xml.find(".//REFERREDTO").get("id")
        self.links[ref] = {"res_num":res_num,"ref":ref,"ref_to":ref_to,"xml":xml}
        
    def convert_questions(self, xml, res_num):
        questions = xml.findall(".//item")
        old_question_ids = [q.id for q in sum(self.questions.values(), [])]
        for question in questions:
            question_type = question.find(".//bbmd_questiontype").text
            if question_type == "Essay":
                self.questions["essay"].append(EssayQuestion(question, res_num))
            elif question_type == "Short Response":
                self.questions["essay"].append(ShortResponseQuestion(question, res_num))
            elif question_type == "True/False":
                self.questions["truefalse"].append(TrueFalseQuestion(question, res_num))
            elif question_type == "Either/Or":
                self.questions["multichoice"].append(
                    EitherOrQuestion(question, res_num)
                )
            elif question_type == "Multiple Choice":
                self.questions["multichoice"].append(
                    MultipleChoiceQuestion(question, res_num)
                )
            elif question_type == "Multiple Answer":
                self.questions["multichoice"].append(
                    MultipleAnswerQuestion(question, res_num)
                )
            elif question_type == "Opinion Scale":
                self.questions["multichoice"].append(
                    OpinionScaleQuestion(question, res_num)
                )
            elif question_type == "Matching":
                self.questions["matching"].append(MatchingQuestion(question, res_num))
            elif question_type == "Ordering":
                self.questions["matching"].append(OrderingQuestion(question, res_num))
            elif question_type == "Fill in the Blank":
                self.questions["shortanswer"].append(
                    FillInTheBlankQuestion(question, res_num)
                )
            elif question_type == "Fill in the Blank Plus":
                self.questions["shortanswer"].append(
                    FillInTheBlankQuestion(question, res_num)
                )
            else:
                utils.logerror(
                    "CR : question type not implemented "
                    + res_num
                    + " | "
                    + question_type
                )

        all_questions = sum(self.questions.values(), [])
        all_question_ids = [q.id for q in all_questions]
        new_question_ids = [q for q in all_question_ids if q not in old_question_ids]
        quiz_questions = [q for q in all_questions if q.id in new_question_ids]
        return quiz_questions

    def convert_resources_document(self, xml, res_num):
        document = Document(xml, res_num)
        if not document.ignore:
            self.resources[res_num] = document
        elif document.make_label:
            self.labels[res_num] = Label(document)
        elif document.make_section:
            document.number = len(self.sections)
            self.sections[res_num] = Section(document)
        else:
            utils.logerror(
                "CR : Missing Doc and ignore " + document.type + " | " + res_num
            )

    def convert_content_areas(self):
        indent = 0
        sections = []
        for content_area in self.manifest.find(".//organization").iterchildren():
            if not content_area.tag == "item":
                continue
            try:
                dat_name = content_area.attrib["identifierref"] + ".dat"
            except KeyError:
                utils.logerror("CA : missing dat " + dat_name)
                continue

            res_xml = etree.parse(self.zip.open(dat_name))
            res_num = content_area.attrib["identifierref"]
            utils.logme("CA : " + res_num + " indent " + str(indent))

            def recurse(elem, indent, section_res_num):
                children = elem.getchildren()
                for child in children:
                    if not child.tag == "item":
                        continue
                    cres_num = child.attrib["identifierref"]
                    childdat = child.attrib["identifierref"] + ".dat"
                    cres_xml = etree.parse(self.zip.open(childdat))
                    utils.logme("CA : " + cres_num + " indent " + str(indent))
                    root = cres_xml.getroot()
                    area = {}
                    area["root"] = root.tag
                    area["xml"] = cres_xml
                    area["res_num"] = cres_num
                    area["contentid"] = root.get("id")
                    area["parentid"] = ""
                    area["foldertype"] = ""
                    p = cres_xml.find(".//PARENTID")
                    self.contentids[root.get("id")] = cres_num
                    if p.get("value") is not None:
                        area["parentid"] = p.get("value")
                        try:
                            self.parent_resnum[p.get("value")] =self.contentids[p.get("value")] 
                        except :
                            utils.logme("parent not found " + p.get("value"))
                    f = cres_xml.find(".//FOLDERTYPE")
                    if f is not None:
                        area["foldertype"] = f.get("value")
                    area["indent"] = indent
                    self.areas[cres_num] = area
                    if self.is_section(area):
                        section_res_num = cres_num
                        sections.append(self.sections[cres_num])
                    else:
                        self.is_activity(area, section_res_num)

                    inner_children = child.getchildren()
                    if len(inner_children) > 1:
                        recurse(child, indent + 1, section_res_num)

            recurse(content_area, indent, res_num)

    def is_section(self, area):
        section = False
        if area.get("root") == "CONTENT":
            if area.get("parentid") != '{unset id}':
                if area.get("foldertype") == "BB_FOLDER":
                    section = True
        return section

    def is_activity(self, area, section_res_num):
        res_num = area.get("res_num")
        if section_res_num not in self.sections.keys():
            section_res_num = '0'
        
        if res_num in self.resources.keys():
            l = self.resources[res_num]
            ch = area.get("xml").find('.//CONTENTHANDLER').get('value')
            if ch == 'resource/x-bb-asmt-test-link' :
                    if res_num in self.links.keys():
                        ref_to = self.links[res_num].get("ref_to")
                        if ref_to in self.assesment.keys():
                            asmtid = self.assesment[ref_to].get("asmtid")
                            if asmtid in self.quizzes.keys():
                                l = self.quizzes[asmtid]
                                self.used['quizzes'].append(l)
                                self.sections[section_res_num].mods[asmtid]=l
            elif ch == 'resource/x-bb-forumlink' :
                    if res_num in self.links.keys():
                        ref_to = self.links[res_num].get("ref_to")
                        if ref_to in self.forums.keys():
                            l = self.forums[ref_to]
                            self.used['forums'].append(l)
                            self.sections[section_res_num].mods[ref_to]=l
            elif ch == 'resource/x-bb-document' and area.get("foldertype") =='':
                parent_res = self.parent_resnum[area.get("parentid")]
                if parent_res in self.labels.keys():
                    self.sections[section_res_num].mods[parent_res].alltext = l.alltext
            else:
                self.used['resources'].append(l)
                self.sections[section_res_num].mods[res_num]=l
        elif res_num in self.quizzes.keys():
            l = self.quizzes[res_num]
            self.used['quizzes'].append(l)
            self.sections[section_res_num].mods[res_num]=l
        elif res_num in self.forums.keys():
            l = self.forums[res_num]
            self.used['forums'].append(l)
            self.sections[section_res_num].mods[res_num]=l
        elif res_num in self.labels.keys():
            l = self.labels[res_num]
            self.used['labels'].append(l)
            self.sections[section_res_num].mods[res_num]=l
        else:
            used = 0
            utils.logerror("IS ACTIVITY : " + res_num)

        return True

    