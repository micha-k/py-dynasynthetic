# -*- coding: utf-8 -*-

"""
 This file is part of the open source project py-dynasynthetic
 (see https://github.com/micha-k/py-dynasynthetic).

 Author: Michael Kessel
 Contact: I have an email account 'dev' on a host called 'michaelkessel' listed
          in the toplevel domain 'de'.
"""

import argparse
import logging
import sys
import re

from dynasynthetic import Utils
from dynasynthetic import DynatraceDatafeedAPI as DDA
from dynasynthetic import DynatraceSyntheticAPI as DSA


class CommandlineClient(object):

    # methods of dsa object
    dispatchable_lists = {'metrics': 'list_metrics',
                          'topmetrics': 'list_topmetrics',
                          'monitors': 'list_monitors'}

    def __init__(self):
        self.logger = logging.getLogger('dynasynthetic-cli')

        self.result_raw = {}
        self.result_data = {}
        self.result_type = None

        self.args = self.parse_arguments()
        self.dda = DDA.DynatraceDatafeedAPI(login=self.args.user,
                                            passwordhash=self.args.password)
        self.dsa = DSA.DynatraceSyntheticAPI(datafeed_api=self.dda)

        if self.args.proxy:
            self.dda.set_proxy(proxy_address=self.args.proxy)

    def dispatch(self, raw_monitor_data=False):
        '''
        Dispatch actions based on user input
        '''

        result_data = {}
        result_type = None

        if self.args.subparser == 'list':
            result_data, result_type = self.dispatch_list()
        elif self.args.subparser == 'measure':
            result_data, result_type = self.dispatch_measure()
        elif self.args.subparser == 'monitor':
            result_data, result_type = self.dispatch_monitor()
        elif self.args.subparser == 'bulk':
            result_data, result_type = self.dispatch_bulk()

        self.result_data = result_data
        self.result_type = result_type

    def dispatch_list(self):

        list_result = None
        selected_list = self.args.list

        if selected_list and selected_list in self.dispatchable_lists.keys():
            methode_name = self.dispatchable_lists[selected_list]
            method_reference = getattr(self.dsa, methode_name)

            list_result = method_reference()
        else:
            self.logger.error('Invalid list choosen')

        return list_result, 'list'

    def dispatch_measure(self):

        self.result_raw = self.dsa.get_aggregated_metric(
            metric=self.args.metric, monid=self.args.slot,
            relative_ms=self.args.relative_time*60*1000,
            bucket_minutes=self.args.relative_time)

        measure_result = '%s: %s (in %s, %s)' % (self.result_raw['name'],
                                                 self.result_raw['value'],
                                                 self.result_raw['unit'],
                                                 self.result_raw['info'])

        return measure_result, 'single_line'

    def dispatch_monitor(self):

        self.result_raw = self.dsa.monitor_aggregated_metric(
            metric=self.args.metric,
            monid=self.args.slot,
            warn=self.args.warn,
            crit=self.args.critical,
            relative_ms=self.args.relative_time*60*1000,
            bucket_minutes=self.args.relative_time)

        monitor_results = '%s - [%s] %s: %s (in %s, %s)' \
                          % (self.result_raw['result_string'],
                             self.result_raw['result_numeric'],
                             self.result_raw['name'],
                             self.result_raw['value'],
                             self.result_raw['unit'],
                             self.result_raw['info'])

        return monitor_results, 'single_line'

    def dispatch_bulk(self):

        date_pattern = re.compile("\d{4}\-\d{2}\-\d{2}")

        if not date_pattern.match(self.args.begin):
            self.error_and_exit('Begin value does not match pattern')
        if not date_pattern.match(self.args.end):
            self.error_and_exit('End value does not match pattern')

        begin_datetime = '%s 00:00:00' % self.args.begin
        begin = Utils.DateUtils.date_converter(raw_input=begin_datetime,
                                               input_mask='%Y-%m-%d %H:%M:%S',
                                               output_mask='%s')
        end_datetime = '%s 23:59:59' % self.args.end
        end = Utils.DateUtils.date_converter(raw_input=end_datetime,
                                             input_mask='%Y-%m-%d %H:%M:%S',
                                             output_mask='%s')

        self.result_raw = self.dsa.export_raw(begin=int(begin)*1000,
                                              end=int(end)*1000,
                                              slot=self.args.slot,
                                              page=self.args.limit)

        return self.result_raw, 'multiline'

    def result_human_readable(self):
        '''
        Returns the result in a way, it can be directly printed to stdout
        '''

        if self.result_type == 'list':
            self.result_data = self.parse_and_display_as_list(
                data=self.result_data)
        elif self.result_type == 'single_line':
            pass
        elif self.result_type == 'multiline':
            self.result_data = self.display_multiline(out=self.result_data)

        return self.result_data

    def result_parsable(self):
        '''
        Returns the result as a dict, to be parsed
        e.g. by the script using it within a nagios check
        '''

        return self.result_raw

    def error_and_exit(self, msg):
        self.logger.error('Error: %s' % msg)
        sys.exit(1)

    def parse_and_display_as_list(self, data, colList=None):
        """
        Inspiration by: Thierry Husson, https://stackoverflow.com/questions/17330139/python-printing-a-dictionary-as-a-horizontal-table-with-headers
        """

        out = []

        if not colList: colList = list(data[0].keys() if data else [])
        myList = [colList] # 1st row = header
        for item in data: myList.append([str(item[col] or '') for col in colList])
        colSize = [max(map(len,col)) for col in zip(*myList)]
        formatStr = ' | '.join(["{{:<{}}}".format(i) for i in colSize])
        myList.insert(1, ['-' * i for i in colSize]) # Seperating line
        for item in myList: out.append(formatStr.format(*item))

        return "\n".join(out)

    def display_multiline(self, out):
        return "\n".join(out)

    def parse_arguments(self):
        desc = 'Commandline tool to access the Dynatrace Synthetic API'

        arg = argparse.ArgumentParser(description=desc)
        subparsers = arg.add_subparsers(dest='subparser')

        # Command list
        list_cmd = subparsers.add_parser('list',
                                         help='Display several lists')
        list_cmd.add_argument('-l', '--list', required=True,
                              choices=self.dispatchable_lists.keys(),
                              help='Name of the list to display')

        # Command metric
        measure_cmd = subparsers.add_parser('measure',
                                            help='Display a selected metric')
        measure_cmd.add_argument('-m', '--metric', type=str, required=True,
                                 help='Name of the metric to display')
        measure_cmd.add_argument('-s', '--slot', type=int, required=True,
                                 help='Slot to select data from')
        measure_cmd.add_argument('-r', '--relative-time', type=int,
                                 default=60, help='Timerange (in minutes) '
                                                  'to consider for metric '
                                                  'calculation')

        # Monitor command
        monitor_cmd = subparsers.add_parser('monitor',
                                            help='Monitor metric with warning '
                                                 'and critical values')
        monitor_cmd.add_argument('-m', '--metric', type=str, required=True,
                                 help='Name of the metric to display')
        monitor_cmd.add_argument('-s', '--slot', type=int, required=True,
                                 help='Slot to select data from')
        monitor_cmd.add_argument('-w', '--warn', type=float,
                                 help='Value for warning result')
        monitor_cmd.add_argument('-c', '--critical', type=float,
                                 help='Value for critical result')
        monitor_cmd.add_argument('-r', '--relative-time', type=int,
                                 default=60, help='Timerange (in minutes) '
                                                  'to consider for metric '
                                                  'calculation')

        # Bulkexport command
        bulk_cmd = subparsers.add_parser('bulk',
                                         help='Bulk export of test results')
        bulk_cmd.add_argument('-b', '--begin', type=str, required=True,
                              help='Begin of timerange (format: YYYY-MM-DD)')
        bulk_cmd.add_argument('-e', '--end', type=str, required=True,
                              help='End of timerange (format: YYYY-MM-DD)')
        bulk_cmd.add_argument('-s', '--slot', type=int, required=True,
                              help='Slot to select data from')
        bulk_cmd.add_argument('-l', '--limit', type=int, required=False,
                              help='Limit data to results of a single page')


        # Add to all commands
        for parser_item in (list_cmd, measure_cmd, monitor_cmd, bulk_cmd):
            parser_item.add_argument('-u', '--user', type=str, required=True,
                                     help='Username to access data')
            parser_item.add_argument('-p', '--password', type=str, required=True,
                                     help='MD5 hash of the password to use')
            parser_item.add_argument('--proxy', type=str,
                                     help='Proxy to use webservice connection')

        return arg.parse_args()

    def get_args(self):
        return self.args