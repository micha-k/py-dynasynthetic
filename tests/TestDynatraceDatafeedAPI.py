# -*- coding: utf-8 -*-

"""
 This file is part of the open source project py-dynasynthetic
 (see https://github.com/micha-k/py-dynasynthetic).

 Author: Michael Kessel
 Contact: I have an email account 'dev' on a host called 'michaelkessel' listed
          in the toplevel domain 'de'.
"""

import unittest
import json

from dynasynthetic.DynatraceDatafeedAPI import DynatraceDatafeedAPI


class TestDynatraceDatafeedAPI(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.login_exp = 'testlogin'
        self.passwordhash_exp = 'a1b2c3d4'
        self.api_proto_exp ='testproto'
        self.api_host_exp = 'test-host.com'
        self.api_version_exp ='v1.0'
        self.api_product_exp = 'testprod'
        self.format_exp = 'test_format'

        self.random_string = "Potatoooo para tu hahaha " \
                             "ti aamoo! Uuuhhh po kass " \
                             "ti aamoo! Uuuhhh po kass poulet " \
                             "tikka masala."

        self.exp_url = 'https://ultraapi-prod.dynatrace.com/v3.2/synthetic'

        with open('tests/test-data/failed-unknown.json', 'r') as file:
            self.ukn_failure = json.loads(file.read())

        with open('tests/test-data/success-metrics.json', 'r') as file:
            self.json_metrics_success = json.loads(file.read())

        with open('tests/test-data/success-topmetrics.json', 'r') as file:
            self.json_topmetrics_success = json.loads(file.read())

    def test_objectInitialization(self):
        dda = DynatraceDatafeedAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp,
                                   api_proto=self.api_proto_exp,
                                   api_host=self.api_host_exp,
                                   api_version=self.api_version_exp,
                                   api_product=self.api_product_exp,
                                   format=self.format_exp)

        self.assertEqual(dda.api_proto, self.api_proto_exp)

        self.assertEqual(dda.api_host, self.api_host_exp)

        self.assertListEqual(dda.api_path, [self.api_version_exp,
                                            self.api_product_exp])

        self.assertDictEqual(dda.api_params, {'login': self.login_exp,
                                              'pass': self.passwordhash_exp,
                                              'format': self.format_exp})

    def test_objectInitializationDefaults(self):
        dda = DynatraceDatafeedAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)

        self.assertEqual(dda.api_proto, 'https')

        self.assertEqual(dda.api_host, 'ultraapi-prod.dynatrace.com')

        self.assertListEqual(dda.api_path, ['v3.2', 'synthetic'])

        self.assertDictEqual(dda.api_params, {'login': self.login_exp,
                                              'pass': self.passwordhash_exp,
                                              'format': 'json'})

        self.assertFalse(dda.mock)

    def test_mock(self):
        dda = DynatraceDatafeedAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)

        dda._setMock(mock_data=self.random_string)

        self.assertEqual(dda.mock, self.random_string)

    def test_url_generation(self):
        dda = DynatraceDatafeedAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)

        self.assertEqual(dda._get_rest_url(), self.exp_url)

    def test_mocked_metric_list_content(self):
        dda = DynatraceDatafeedAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)
        dda._setMock(mock_data={'rc': 200, 'body': self.json_metrics_success})

        self.assertEqual(dda.info(list='metrics'), self.json_metrics_success)

    def test_set_proxy(self):
        dda = DynatraceDatafeedAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)
        dda.set_proxy('http://proxy.acme.org:123')

        self.assertDictEqual(dda.proxies, {'http': 'http://proxy.acme.org:123',
                                           'https': 'http://proxy.acme.org:123',
                                           'ftp': False})

if __name__ == '__main__':
    unittest.main()
