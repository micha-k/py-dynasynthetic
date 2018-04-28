# -*- coding: utf-8 -*-

"""
 This file is part of the open source project py-dynasynthetic
 (see https://github.com/micha-k/py-dynasynthetic).

 Author: Michael Kessel
 Contact: I have an email account 'dev' on a host called 'michaelkessel' listed
          in the toplevel domain 'de'.
"""

import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class DynatraceDatafeedAPI(object):

    def __init__(self,
                 login,
                 passwordhash,
                 api_proto='https',
                 api_host='ultraapi-prod.dynatrace.com',
                 api_version='v3.2',
                 api_product='synthetic',
                 format='json',
                 retry_count=2,
                 retry_backoff_factor=0.1):

        self.api_proto = api_proto
        self.api_host = api_host
        self.api_path = [api_version, api_product]
        self.api_params = {'login': login,
                           'pass': passwordhash,
                           'format': format}

        self.proxies = {'http': False,
                        'https': False,
                        'ftp': False}

        self.retry_count = retry_count
        self.retry_backoff_factor = retry_backoff_factor

        self.mock = False

    def info(self, list):
        self.api_path.append('info')
        self.api_params['list'] = list

        return self._rest_call()

    def trend(self, metrics, monid, rltime=None, tstart=None, tend=None,
              bucket=None, bucketsize=None, group=None, header=None,
              sort=None, limit=None, skip=None, format=None):

        self.api_path.append('trend')

        # check valid definition of timerange
        if not (rltime or (tstart and tend)):
            raise ValueError('No valid timerange parameters '
                             '(rltime or tstar+tend) set')

        # check timerange values
        if rltime and not int(rltime) >0:
           raise ValueError('rltime must be >0')
        if tstart and not int(tstart) >0:
           raise ValueError('tstart must be >0')
        if tend and not int(tend) >0:
           raise ValueError('tend must be >0')

        # set relative OR absolute time
        if rltime:
            self.api_params['rltime'] = rltime
        else:
            self.api_params['tstart'] = tstart
            self.api_params['tend'] = tend

        self.api_params['metrics'] = metrics
        self.api_params['monid'] = monid

        if bucket:
            self.api_params['bucket'] = bucket

        if bucketsize:
            self.api_params['bucketsize'] = bucketsize

        if group:
            self.api_params['group'] = group

        if header:
            self.api_params['header'] = header

        if sort:
            self.api_params['sort'] = sort

        if limit:
            self.api_params['limit'] = limit

        if skip:
            self.api_params['skip'] = skip

        if format:
            self.api_params['format'] = format

        return self._rest_call()

    def raw(self, metrics, monid, pgeid=None, rltime=None, tstart=None, tend=None,
            group=None, header=None, sort=None, limit=None, skip=None,
            format=None):

        self.api_path.append('raw')

        # check valid definition of timerange
        if not (rltime or (tstart and tend)):
            raise ValueError('No valid timerange parameters '
                             '(rltime or tstar+tend) set')

        # check timerange values
        if rltime and not int(rltime) >0:
           raise ValueError('rltime must be >0')
        if tstart and not int(tstart) >0:
           raise ValueError('tstart must be >0')
        if tend and not int(tend) >0:
           raise ValueError('tend must be >0')

        # set relative OR absolute time
        if rltime:
            self.api_params['rltime'] = rltime
        else:
            self.api_params['tstart'] = tstart
            self.api_params['tend'] = tend

        self.api_params['metrics'] = metrics
        self.api_params['monid'] = monid

        if pgeid:
            self.api_params['pgeid'] = pgeid

        if group:
            self.api_params['group'] = group

        if header:
            self.api_params['header'] = header

        if sort:
            self.api_params['sort'] = sort

        if limit:
            self.api_params['limit'] = limit

        if skip:
            self.api_params['skip'] = skip

        if format:
            self.api_params['format'] = format

        return self._rest_call()

    def set_proxy(self, proxy_address):
        self.proxies = {'http': proxy_address,
                        'https': proxy_address,
                        'ftp': False}

    def _get_rest_url(self):
        url = "%s://%s/%s" % ( self.api_proto,
                               self.api_host,
                               '/'.join(self.api_path) )

        return url

    def _rest_call(self):
        url = self._get_rest_url()

        if not self.mock:

            # Apply retry settings
            # (https://stackoverflow.com/questions/15431044/can-i-set-max-retries-for-requests-request)
            s = requests.Session()
            retries = Retry(total=self.retry_count,
                            backoff_factor=self.retry_backoff_factor)
            s.mount('https://', HTTPAdapter(max_retries=retries))

            r = s.get(url,
                      params=self.api_params,
                      proxies=self.proxies)
            call_result = { 'rc': r.status_code,
                            'body': r.json()}
        else:
            call_result = self.mock

        return call_result['body']

    def _setMock(self, mock_data=True):
        self.mock = mock_data
