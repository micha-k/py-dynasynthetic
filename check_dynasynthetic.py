#!/usr/bin/env python

"""
 This file is part of the open source project py-dynasynthetic
 (see https://github.com/micha-k/py-dynasynthetic).

 Author: Michael Kessel
 Contact: I have an email account 'dev' on a host called 'michaelkessel' listed
          in the toplevel domain 'de'.

 check_dynasynthetic.py - Executable to use as a nagios plugin

     usage: check_dynasynthetic.py monitor [-h] -m METRIC -s SLOT [-w WARN]
                                          [-c CRITICAL] -u USER -p PASSWORD

    arguments:
      -h, --help                        show this help message and exit
      -m METRIC, --metric METRIC        Name of the metric to display
      -s SLOT, --slot SLOT              Slot to select data from
      -w WARN, --warn WARN              Value for warning result
      -c CRITICAL, --critical CRITICAL  Value for critical result
      -u USER, --user USER              Username to access data
      -p PASSWORD, --password PASSWORD  MD5 hash of the password to use
"""

import nagiosplugin
from nagiosplugin.performance import Performance
from nagiosplugin.result import Result
from nagiosplugin.state import Ok, Warn, Critical


from dynasynthetic import CommandlineClient as CC


class DynatraceMetric(nagiosplugin.Resource):

    def __init__(self, data):
        self.data = data

    def probe(self):
        yield nagiosplugin.Metric(self.data['name'],
                                  self.data['value'],
                                  min=0,
                                  context='metric')


class DynatraceMetricSummary(nagiosplugin.Summary):
    def __init__(self, data):
        self.data = data

    def summary_output(self):
        return '%s: %s (in %s, %s)' % (self.data['name'],
                                       self.data['value'],
                                       self.data['unit'],
                                       self.data['info'])

    def ok(self, results):
        return self.summary_output()

    def problem(self, results):
        return self.summary_output()

    def verbose(self, results):
        return self.summary_output()


class CommandlineClientAsScalarContext(nagiosplugin.ScalarContext):

    def __init__(self, name, data, warning=False, critical=False,
                 fmt_metric='', result_cls=Result):
        self.data = data
        super(CommandlineClientAsScalarContext, self).\
            __init__(name, warning, critical, fmt_metric, result_cls)

    def evaluate(self, metric, resource):
        if self.data['result_string'] == 'CRITICAL':
            return self.result_cls(Critical, False, metric)
        elif self.data['result_string'] == 'WARNING':
            return self.result_cls(Warn, None, metric)
        else:
            return self.result_cls(Ok, None, metric)

    def performance(self, metric, resource):
        return Performance(metric.name, metric.value)


@nagiosplugin.guarded
def main():

    cli = CC.CommandlineClient()
    cli.dispatch()
    data = cli.result_parsable()

    check = nagiosplugin.Check(
        DynatraceMetric(data=data),
        CommandlineClientAsScalarContext('metric', data, False, False),
        DynatraceMetricSummary(data=data))
    check.main()


if __name__ == '__main__':
    main()
