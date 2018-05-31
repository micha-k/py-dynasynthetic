#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 This file is part of the open source project py-dynasynthetic
 (see https://github.com/micha-k/py-dynasynthetic).

 Author: Michael Kessel
 Contact: I have an email account 'dev' on a host called 'michaelkessel' listed
          in the toplevel domain 'de'.
"""

from dynasynthetic import CommandlineClient as CC

if __name__ == '__main__':
    cli = CC.CommandlineClient()
    cli.dispatch()

    print(cli.result_human_readable())
