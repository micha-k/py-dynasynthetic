# -*- coding: utf-8 -*-

"""
 This file is part of the open source project py-dynasynthetic
 (see https://github.com/micha-k/py-dynasynthetic).

 Author: Michael Kessel
 Contact: I have an email account 'dev' on a host called 'michaelkessel' listed
          in the toplevel domain 'de'.
"""

class DynatraceSyntheticAPI(object):

    AVAILABILITY_METRIC = 'avail'
    PERFORMANCE_METRIC = 'uxtme'

    OK_STRING = 'OK'
    OK_NUMERIC = 0

    WARNING_STRING = 'WARNING'
    WARNING_NUMERIC = 1

    CRITIAL_STRING = 'CRITICAL'
    CRITICAL_NUMERIC = 2

    UNKNOWN_STRING = 'UNKOWN'
    UNKNOWN_NUMERIC = 3

    def __init__(self, datafeed_api):
        self.df_api = datafeed_api

    def monitor_aggregated_availability(self, monid, warn, crit,
                                        relative_ms=3600000,
                                        bucket_minutes=60):
        return self.monitor_aggregated_metric(metric=self.AVAILABILITY_METRIC,
                                              monid=monid,
                                              warn=warn,
                                              crit=crit,
                                              relative_ms=relative_ms,
                                              bucket_minutes=bucket_minutes)

    def monitor_aggregated_performance(self, monid, warn, crit,
                                       relative_ms=3600000,
                                       bucket_minutes=60):
        return self.monitor_aggregated_metric(metric=self.PERFORMANCE_METRIC,
                                              monid=monid,
                                              warn=warn,
                                              crit=crit,
                                              relative_ms=relative_ms,
                                              bucket_minutes=bucket_minutes)

    def monitor_aggregated_metric(self,
                                  metric,
                                  monid,
                                  warn,
                                  crit,
                                  relative_ms=3600000,
                                  bucket_minutes=60):

        metric_data = self.get_aggregated_metric(metric=metric,
                                                 monid=monid,
                                                 relative_ms=relative_ms,
                                                 bucket_minutes=bucket_minutes)

        # Assess result based on alarm values
        result_string = self.UNKNOWN_STRING
        result_numeric = self.UNKNOWN_NUMERIC

        if warn > crit:
            # Higher is better, e.g. availability
            if metric_data['value'] <= crit:
                result_string = self.CRITIAL_STRING
                result_numeric = self.CRITICAL_NUMERIC
            if metric_data['value'] > crit and metric_data['value'] <= warn:
                result_string = self.WARNING_STRING
                result_numeric = self.WARNING_NUMERIC
            if metric_data['value'] > warn:
                result_string = self.OK_STRING
                result_numeric = self.OK_NUMERIC
        elif warn < crit:
            # Lower is better, e.g. response time
            if metric_data['value'] < warn:
                result_string = self.OK_STRING
                result_numeric = self.OK_NUMERIC
            if metric_data['value'] >= warn and metric_data['value'] < crit:
                result_string = self.WARNING_STRING
                result_numeric = self.WARNING_NUMERIC
            if metric_data['value'] >= crit:
                result_string = self.CRITIAL_STRING
                result_numeric = self.CRITICAL_NUMERIC
        else:
            raise ValueError('Critical and/or warning value invalid')

        metric_data['result_string'] = result_string
        metric_data['result_numeric'] = result_numeric

        return metric_data

    def get_aggregated_availability(self, monid,relative_ms=3600000,
                                    bucket_minutes=60):
        return self.get_aggregated_metric(metric=self.AVAILABILITY_METRIC,
                                          monid=monid,
                                          relative_ms=relative_ms,
                                          bucket_minutes=bucket_minutes)

    def get_aggregated_performance(self, monid,relative_ms=3600000,
                                    bucket_minutes=60):
        return self.get_aggregated_metric(metric=self.PERFORMANCE_METRIC,
                                          monid=monid,
                                          relative_ms=relative_ms,
                                          bucket_minutes=bucket_minutes)

    def get_aggregated_metric(self, metric, monid, relative_ms=3600000,
                              bucket_minutes=60):

        api_raw = self.df_api.trend(metrics=metric, monid=monid,
                                    rltime=relative_ms, bucket='minute',
                                    bucketsize=bucket_minutes,
                                    format='json')

        if api_raw['data'][0] and api_raw['data'][0][metric]:
            value = api_raw['data'][0][metric]
        else:
            value = -1

        if api_raw['meta']['metrics'][metric]:
            name = api_raw['meta']['metrics'][metric]['name']
            unit = api_raw['meta']['metrics'][metric]['unit']
            info = api_raw['meta']['metrics'][metric]['desc']
        else:
            name = ''
            unit = ''
            info = ''

        return {'value': value, 'unit': unit, 'name': name, 'info': info}

    def list_metrics(self, topmetrics_only=False):
        filter = ['mask', 'name', 'desc', 'unit']

        # determine, if we want all or just the top metrics
        if topmetrics_only:
            list_to_fetch = 'topmetrics'
        else:
            list_to_fetch = 'metrics'

        api_raw = self.df_api.info(list=list_to_fetch)

        return self._reduct_object_list_by_filter(obj=api_raw['data'],
                                                  filter=filter)

    def list_topmetrics(self):
        return self.list_metrics(topmetrics_only=True)


    def list_monitors(self):
        filter = ['monid', 'mname', 'bname', 'mfrequency', 'mtype', 'bname']
        api_raw = self.df_api.info(list='monitors')

        return self._reduct_object_list_by_filter(obj=api_raw['data'],
                                                  filter=filter)

    def _reduct_object_list_by_filter(self, obj, filter):
        reduced = []

        for object_item in obj:
            item_data = {}

            for filter_item in filter:
                item_data[filter_item] = object_item[filter_item]

            reduced.append(item_data)

        return reduced
