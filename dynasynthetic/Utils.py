# -*- coding: utf-8 -*-

"""
 This file is part of the open source project py-dynasynthetic
 (see https://github.com/micha-k/py-dynasynthetic).

 Author: Michael Kessel
 Contact: I have an email account 'dev' on a host called 'michaelkessel' listed
          in the toplevel domain 'de'.
"""

from datetime import datetime


class DateUtils(object):

    @staticmethod
    def date_converter(raw_input, input_mask, output_mask):
        intermediate = datetime.strptime(raw_input, input_mask)
        return intermediate.strftime(output_mask)
