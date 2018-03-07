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

from dynasynthetic import DynatraceDatafeedAPI as DDA
from dynasynthetic import DynatraceSyntheticAPI as DSA


class CommandlineClient(object):

    # methods of dsa object
    dispatchable_lists = {'metrics': 'list_metrics',
                          'topmetrics': 'list_topmetrics',
                          'monitors': 'list_monitors'}

    def __init__(self):
        self.logger = logging.getLogger('dynasynthetic-cli')

        self.result_data = {}
        self.result_type = None

        self.args = self.parse_arguments()
        self.dda = DDA.DynatraceDatafeedAPI(login=self.args.user,
                                            passwordhash=self.args.password)
        self.dsa = DSA.DynatraceSyntheticAPI(datafeed_api=self.dda)

    def dispatch(self, raw_monitor_data=False):
        '''
        Dispatch actions based on user input
        '''

        result_raw = {}
        result_data = {}
        result_type = None

        if self.args.subparser == 'list':
            result_data, result_type = self.dispatch_list()
        elif self.args.subparser == 'measure':
            result_data, result_type = self.dispatch_measure()
        elif self.args.subparser == 'monitor':
            result_data, result_type = self.dispatch_monitor()

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
            metric=self.args.metric, monid=self.args.slot)

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
            crit=self.args.critical)

        monitor_results = '%s - [%s] %s: %s (in %s, %s)' \
                          % (self.result_raw['result_string'],
                             self.result_raw['result_numeric'],
                             self.result_raw['name'],
                             self.result_raw['value'],
                             self.result_raw['unit'],
                             self.result_raw['info'])

        return monitor_results, 'single_line'

    def result_human_readable(self):
        '''
        Returns the result in a way, it can be directly printed to stdout
        '''

        if self.result_type == 'list':
            self.result_data = self.parse_and_display_as_list(
                data=self.result_data)
        elif self.result_type == 'single_line':
            pass

        return self.result_data

    def result_parsable(self):
        '''
        Returns the result as a dict, to be parsed
        e.g. by the script using it within a nagios check
        '''

        return self.result_raw

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


    def parse_arguments(self):
        desc = 'Commandline tool to access the Dynatrace Synthetic API'

        arg = argparse.ArgumentParser(description=desc)
        subparsers = arg.add_subparsers(dest='subparser')

        # Command list
        list_cmd = subparsers.add_parser('list')
        list_cmd.add_argument('-l', '--list', required=True,
                              choices=self.dispatchable_lists.keys(),
                              help='Name of the list to display')

        # Command metric
        measure_cmd = subparsers.add_parser('measure')
        measure_cmd.add_argument('-m', '--metric', type=str, required=True,
                                 help='Name of the metric to display')
        measure_cmd.add_argument('-s', '--slot', type=int, required=True,
                                 help='Slot to select data from')

        # Monitor command
        monitor_cmd = subparsers.add_parser('monitor')
        monitor_cmd.add_argument('-m', '--metric', type=str, required=True,
                                 help='Name of the metric to display')
        monitor_cmd.add_argument('-s', '--slot', type=int, required=True,
                                 help='Slot to select data from')
        monitor_cmd.add_argument('-w', '--warn', type=float,
                                 help='Value for warning result')
        monitor_cmd.add_argument('-c', '--critical', type=float,
                                 help='Value for critical result')

        # Add to all commands
        for parser_item in (list_cmd, measure_cmd, monitor_cmd):
            parser_item.add_argument('-u', '--user', type=str, required=True,
                                     help='Username to access data')
            parser_item.add_argument('-p', '--password', type=str, required=True,
                                     help='MD5 hash of the password to use')

        return arg.parse_args()

    def get_args(self):
        return self.args