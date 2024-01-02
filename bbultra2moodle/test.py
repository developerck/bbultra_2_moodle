import os
import sys
import optparse
import traceback
import bbultra2moodle.bbconverter as bbconverter
full_in_name = '/var/www/html/bbultra_2_moodle/content/bb/OZ-999-TMP-OTHR908.zip'
full_out_name = '/var/www/html/bbultra_2_moodle/content/moodle/OZ-999-TMP-OTHR908.zip'

bbconverter.create_moodle_zip(full_in_name, full_out_name)

    