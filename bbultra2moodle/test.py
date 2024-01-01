import os
import sys
import optparse
import traceback
import bbultra2moodle.bbconverter as bbconverter
full_in_name = '/var/www/html/bbultra_2_moodle/content/bb/biol.zip'
full_out_name = '/var/www/html/bbultra_2_moodle/content/moodle/m_biol.zip'

bbconverter.create_moodle_zip(full_in_name, full_out_name)

    