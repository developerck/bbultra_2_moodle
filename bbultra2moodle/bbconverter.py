# bb2ultra2moodle
import os
import re
import time
import base64
import shutil
import urllib
import zipfile
import subprocess
import sys
import io
import re
from lxml import etree
from bbultra2moodle.conv.Parser import Parser
import bbultra2moodle.utils as utils




def create_moodle_zip(blackboard_zip_fname, out_name):
    try:
        shutil.rmtree("elixer_tmp")
        shutil.rmtree("course_files")
    except OSError:
        pass

    course = Parser(blackboard_zip_fname)
    moodle_zip = zipfile.ZipFile(out_name, "w")
    moodle_xml_str = utils.convert(course).encode("utf-8")
    moodle_zip.writestr("moodle.xml", moodle_xml_str)

    err_fh = open(os.path.devnull, "w")

    command = ("unzip %s -d elixer_tmp" % blackboard_zip_fname).split(" ")
    subprocess.Popen(command, stdout=err_fh, stderr=err_fh).communicate()
    skip_parent = False

    for root, dirs, files in os.walk("elixer_tmp"):
        if not skip_parent:
            skip_parent = True
            continue

        for bb_fname in files:
            moodle_fname = bb_fname
            if moodle_fname.endswith(".xml"):
                continue

            if bb_fname.startswith("!"):
                if "." in bb_fname:
                    ext, fname = [s[::-1] for s in bb_fname[1:][::-1].split(".", 1)]
                    moodle_fname = base64.b16decode(fname.upper()) + "." + ext
                else:
                    ext, fname = "", bb_fname[1:]
                    moodle_fname = base64.b16decode(fname.upper())

                moodle_fname = urllib.unquote(moodle_fname)

            res_num = root.split(os.sep, 1)[1].split(os.sep)[0].replace("res", "")

            fixed_filename = utils.fix_filename(moodle_fname, res_num)

            bb_fname = os.path.join(root, bb_fname)

            moodle_fname = os.path.join("course_files", fixed_filename)

            moodle_zip.write(bb_fname, moodle_fname)

    shutil.rmtree("elixer_tmp")

    moodle_zip.close()
