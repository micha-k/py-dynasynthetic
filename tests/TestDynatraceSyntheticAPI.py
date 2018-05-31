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
from dynasynthetic.DynatraceSyntheticAPI import DynatraceSyntheticAPI


class TestDynatraceSyntheticfeedAPI(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.login_exp = 'testlogin'
        self.passwordhash_exp = 'a1b2c3d4'

        with open('tests/test-data/success-metrics.json', 'r') as file:
            self.json_metrics_success = json.loads(file.read())

        with open('tests/test-data/success-topmetrics.json', 'r') as file:
            self.json_topmetrics_success = json.loads(file.read())

        with open('tests/test-data/success-avail-metric.json', 'r') as file:
            self.json_avail_metric_success = json.loads(file.read())

        with open('tests/test-data/success-uxtme-metric.json', 'r') as file:
            self.json_perf_metric_success = json.loads(file.read())

        with open('tests/test-data/failed-unauthorized.json', 'r') as file:
            self.json_failed_unauthorized = json.loads(file.read())

        self.avail_data_expect = {'value': 0.91234578,
                                  'unit': "%",
                                  'name': "Availability",
                                  'info': "Average Availability of "
                                          "selected Measurements"}

        self.perf_data_expect = {'value': 7865.333333333333,
                                 'unit': "ms",
                                 'name': "User Experience",
                                 'info': "Full User Experience time as reported"
                                         " by the browser"}


    def test_mock_list_metric(self):
        dda = DynatraceDatafeedAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)
        dda._setMock(mock_data={'rc': 200, 'body': self.json_metrics_success})
        dsa = DynatraceSyntheticAPI(datafeed_api=dda)

        metrics = dsa.list_metrics()

        item1 = {"mask": "css_3_bttfp_c",
                 "name": "3rd Party CSS Count Before TTFP",
                 "desc": "3rd Party CSS Count Before Time to First Paint",
                 "unit": "number"}

        item2 =  {"mask": "css_3_o_s",
                  "name": "3rd Party CSS Size",
                  "desc": "3rd Party CSS Size",
                  "unit": "b"}

        self.assertTrue(item1 in metrics)
        self.assertTrue(item2 in metrics)

    def test_mock_avail_metric(self):
        dda = DynatraceDatafeedAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)
        dda._setMock(mock_data={'rc': 200,
                                'body': self.json_avail_metric_success})
        dsa = DynatraceSyntheticAPI(datafeed_api=dda)

        avail = dsa.get_aggregated_availability(monid=12345)

        self.assertDictEqual(avail, self.avail_data_expect)

    def test_mock_perf_metric_monitor(self):
        dda = DynatraceDatafeedAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)

        # Perfomance in this mock is 7865.333333333333
        dda._setMock(mock_data={'rc': 200,
                                'body': self.json_perf_metric_success})
        dsa = DynatraceSyntheticAPI(datafeed_api=dda)

        # Case: OK
        perf = dsa.monitor_aggregated_performance(monid=123456,
                                                  warn=8000,
                                                  crit=9000)
        self.assertEqual(perf['result_string'], dsa.OK_STRING)
        self.assertEqual(perf['result_numeric'], dsa.OK_NUMERIC)

        # Case: WARN
        perf = dsa.monitor_aggregated_performance(monid=123456,
                                                  warn=7000,
                                                  crit=8000)
        self.assertEqual(perf['result_string'], dsa.WARNING_STRING)
        self.assertEqual(perf['result_numeric'], dsa.WARNING_NUMERIC)

        # Case: CRITICAL
        perf = dsa.monitor_aggregated_performance(monid=123456,
                                                  warn=2000,
                                                  crit=7000)
        self.assertEqual(perf['result_string'], dsa.CRITIAL_STRING)
        self.assertEqual(perf['result_numeric'], dsa.CRITICAL_NUMERIC)

    def test_mock_perf_avail_monitor(self):
        dda = DynatraceDatafeedAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)

        # Availability in this mock is 0.91234578
        dda._setMock(mock_data={'rc': 200,
                                'body': self.json_avail_metric_success})
        dsa = DynatraceSyntheticAPI(datafeed_api=dda)

        # Case: OK
        avail = dsa.monitor_aggregated_availability(monid=123456,
                                                    warn=0.9,
                                                    crit=0.8)
        self.assertEqual(avail['result_string'], dsa.OK_STRING)
        self.assertEqual(avail['result_numeric'], dsa.OK_NUMERIC)

        # Case: WARN
        avail = dsa.monitor_aggregated_availability(monid=123456,
                                                    warn=0.95,
                                                    crit=0.90)
        self.assertEqual(avail['result_string'], dsa.WARNING_STRING)
        self.assertEqual(avail['result_numeric'], dsa.WARNING_NUMERIC)

        # Case: CRITICAL
        avail = dsa.monitor_aggregated_availability(monid=123456,
                                                    warn=0.99,
                                                    crit=0.98)
        self.assertEqual(avail['result_string'], dsa.CRITIAL_STRING)
        self.assertEqual(avail['result_numeric'], dsa.CRITICAL_NUMERIC)

    def test_export_raw(self):
        dda = DynatraceDatafeedAPI(login=self.login_exp,
                                   passwordhash=self.passwordhash_exp)

        dda._setMock(mock_data={'rc': 403,
                                'body': self.json_failed_unauthorized})
        dsa = DynatraceSyntheticAPI(datafeed_api=dda)
        self.assertRaises(ValueError, dsa.export_raw, begin=1, end=2, slot=3, page=4)



if __name__ == '__main__':
    unittest.main()
