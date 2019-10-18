# -*- coding: utf-8 -*-

"""
 This file is part of the open source project py-dynasynthetic
 (see https://github.com/micha-k/py-dynasynthetic).

 Author: Michael Kessel
 Contact: I have an email account 'dev' on a host called 'michaelkessel' listed
          in the toplevel domain 'de'.
"""

import copy

from datetime import datetime


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

    def get_aggregated_availability(self, monid, relative_ms=3600000,
                                    bucket_minutes=60):
        return self.get_aggregated_metric(metric=self.AVAILABILITY_METRIC,
                                          monid=monid,
                                          relative_ms=relative_ms,
                                          bucket_minutes=bucket_minutes)

    def get_aggregated_performance(self, monid, relative_ms=3600000,
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
        value = -1
        if 'data' in api_raw:
            if len(api_raw['data']) > 0:
                if metric in api_raw['data'][0]:
                    value = api_raw['data'][0][metric]

        name = ''
        unit = ''
        info = ''
        if 'meta' in api_raw:
            if 'metrics' in api_raw['meta']:
                if metric in api_raw['meta']['metrics']:
                    if 'name' in api_raw['meta']['metrics'][metric]:
                        name = api_raw['meta']['metrics'][metric]['name']
                    if 'unit' in api_raw['meta']['metrics'][metric]:
                        unit = api_raw['meta']['metrics'][metric]['unit']
                    if 'desc' in api_raw['meta']['metrics'][metric]:
                        info = api_raw['meta']['metrics'][metric]['desc']

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

    def export_raw(self, begin, end, slot, page):
        results = []
        indexed_slots = {}
        indexed_agents = {}

        # Display pgeid if page is requested
        group_val = None
        if page:
            group_val = 'pgeid'

        # More retries on bulk exports with longer sleep times
        self.df_api.retry_count = 5
        self.df_api.retry_backoff_factor = 0.5

        api_for_slots = copy.deepcopy(self.df_api)
        api_for_agents = copy.deepcopy(self.df_api)
        data_raw = self.df_api.raw(metrics='avail,respt',
                                   monid=slot,
                                   tstart=begin,
                                   tend=end,
                                   pgeid=page,
                                   group=group_val)

        # this list is deprecated in v3.2 right now
        api_for_agents.api_path = ['v3.3', 'synthetic']

        data_slots = api_for_slots.info(list='slots')
        data_agents = api_for_agents.info(list='agents')

        # Index slots
        if 'data' in data_slots:
            for slot_item in data_slots['data']:
                indexed_slots[slot_item['monid']] = slot_item
        else:
            raise ValueError("Missing field 'data' in data_slots")

        # Index agents
        if 'Sites' in data_agents:
            for agent_item in data_agents['Sites']:
                siteId = int(agent_item['Site']['siteID'])
                indexed_agents[siteId] = agent_item['Site']
        else:
            raise ValueError("Missing field 'Sites' in data_agents")

        result_head = "%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
                      ('TIME', 'AGENT', 'TARGET_ID',
                       'PERFORMANCE[respt]', 'ERROR',
                       'CONTENT_ERROR', 'ALIAS')
        results.append(result_head)

        # enrich data lines
        if 'data' in data_raw:
            for entry in data_raw['data']:
                date = datetime.fromtimestamp(int(entry['mtime']/1000))

                # check if we got all needed keys
                if not all(k in entry for k in ('agtid', 'avail', 'monid', 'respt')):
                    raise ValueError('Incomplete entry object: %s' % entry)

                # Looking up the slot and agent data
                cur_slot = indexed_slots[entry['monid']]
                cur_agent = indexed_agents[entry['agtid']]

                # Page set?
                page_string = ''
                if 'pgeid' in entry.keys():
                    page_string = ' - %s [p %s]' % (cur_slot['pages'][str(entry['pgeid'])]['uiName'],
                                                    str(entry['pgeid']))

                slot_alias = '%s (%s, %s%s)' % (cur_slot['mname'],
                                                cur_slot['bname'],
                                                cur_slot['mtype'],
                                                page_string)

                avail_status_mapping = {0: "Availability Error",
                                        1: "Success"}

                result_entry = "%s\t%s\t%s\t%s\t%s\t%s\t%s" \
                               % (date.strftime('%d-%b-%Y %H:%M:%S').upper(),
                                   cur_agent['name'],
                                   entry['monid'],
                                   float(entry['respt'])/1000,
                                   avail_status_mapping[entry['avail']],
                                   '0',
                                   slot_alias)

                results.append(result_entry)
        else:
            raise ValueError("Missing field 'data' in data_raw: %s" % data_raw.keys())

        return results

    def _reduct_object_list_by_filter(self, obj, filter):
        reduced = []

        for object_item in obj:
            item_data = {}

            for filter_item in filter:
                item_data[filter_item] = object_item[filter_item]

            reduced.append(item_data)

        return reduced
