# -*- coding: utf-8 -*-

"""
 This file is part of the open source project py-dynasynthetic
 (see https://github.com/micha-k/py-dynasynthetic).

 This is just a test mock, pending a complete re-implementation
 for the new Dynatrace API backend.
"""

import unittest
import json

from dynasynthetic.DynatraceDatafeedNewAPI import DynatraceDatafeedNewAPI

class TestDynatraceDatafeedNewAPI(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.login_exp = 'testlogin'
        self.passwordhash_exp = 'a1b2c3d4'
        self.api_proto_exp = 'testproto'
        self.api_host_exp = 'test-host.com'
        self.api_version_exp = 'v1.0'
        self.api_product_exp = 'testprod'
        self.format_exp = 'test_format'

        self.exp_url = 'https://hxc35241.live.dynatrace.com/api/v2'


    def test_objectInitialization(self):
        dda = DynatraceDatafeedNewAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp,
                                   api_proto=self.api_proto_exp,
                                   api_host=self.api_host_exp,
                                   api_product=self.api_product_exp,
                                   format=self.format_exp)

        self.assertEqual(dda.api_proto, self.api_proto_exp)

        self.assertEqual(dda.api_host, self.api_host_exp)

    def test_objectInitializationDefaults(self):
        dda = DynatraceDatafeedNewAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)

        self.assertEqual(dda.api_proto, 'https')

    def test_trend(self):
        dda = DynatraceDatafeedNewAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)

        dda.mock = {'body': 'bla'}

    def test_raw(self):
        dda = DynatraceDatafeedNewAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)
        dda.mock = {'body': 'bla'}


    def test_set_proxy(self):
        dda = DynatraceDatafeedNewAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)
        dda.set_proxy('http://proxy.acme.org:123')

        self.assertDictEqual(dda.proxies, {'http': 'http://proxy.acme.org:123',
                                           'https': 'http://proxy.acme.org:123',
                                           'ftp': False})


if __name__ == '__main__':
    unittest.main()
