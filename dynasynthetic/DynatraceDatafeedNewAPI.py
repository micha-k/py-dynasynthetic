# -*- coding: utf-8 -*-

"""
Re-implementation of Datafeed API for new Dynatrace system
"""
import requests
import requests.utils
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class DynatraceDatafeedNewAPI(object):

    def __init__(self,
                 login,
                 passwordhash,  # Note: The API-Token goes here!
                 api_proto='https',
                 api_host='hxc35241.live.dynatrace.com',
                 api_product="api",
                 format='json',
                 retry_count=2,
                 retry_backoff_factor=0.1,
                 timeout=3):

        self.api_proto = api_proto
        self.api_host = api_host
        self.api_path = [ api_product ]
        self.api_params = { 'format': format,
                            'api-token': passwordhash}

        self.proxies = {'http': False,
                        'https': False,
                        'ftp': False}

        self.retry_count = retry_count
        self.retry_backoff_factor = retry_backoff_factor
        self.timeout = timeout

        self.mock = False


    def info(self, list):   #CLI name 'list' is param for rest call
        if list == "metrics":
            self.api_path.append('v2/metrics/descriptors')
            self.api_params['includeMeta'] = True
        if list == "topmetrics":
            self.api_path.append('v2/metrics/descriptors')
        elif list == "monitors":
            self.api_path.append('v1/synthetic/monitors')

        print("info called for list"+list+"\n")
        print(self.api_path)
        return self._rest_call()

    def trend(self, metrics, monid, rltime=None, tstart=None, tend=None,
              bucket=None, bucketsize=None, group=None, header=None,
              sort=None, limit=None, skip=None, format=None):

        # copy list to reset it at the end of trend()
        # We need this to retrieve the metadate with the new backend API
        base_path=list(self.api_path)

        # map metric name
        if metrics == 'avail':
            self.api_path.append('v2/metrics/series')
            self.api_path.append("builtin:synthetic.browser.success,builtin:synthetic.browser.failure")
            self.api_params['from'] = 'now-1h'
            self.api_params['to'] = 'now'
            self.api_params['resolution'] = 'Inf'
            self.api_params['scope'] = self._remap_scope(monid)
        if metrics == 'uxtme':
            self.api_path.append('v2/metrics/series')
            self.api_path.append('builtin:synthetic.browser.totalDuration')
            self.api_params['scope'] = self._remap_scope(monid)

            self.api_params['from'] = 'now-1h'
            self.api_params['to'] = 'now'
            self.api_params['resolution'] = '60m'

        restcall_result = self._rest_call()
        self.api_path = base_path
        return restcall_result

########################################
    def get_meta(self, metrics):
        self.api_path.append('v2/metrics/descriptors')
        if metrics == 'avail':
            new_metric = "builtin:synthetic.browser.success"
        if metrics == 'uxtme':
            new_metric = 'builtin:synthetic.browser.totalDuration'

        self.api_path.append(new_metric)
        meta_data = self._rest_call()
        return {'data':meta_data, 'metric':new_metric}


########################################
    def _remap_scope(self, monid):
        # real values omitted
        scope_map = { 4711: ("DEADBEEFCAFEBABE", "dummy name for dynatrace check") }
        if scope_map.has_key(monid):
            ent = scope_map[monid][0]
        else:
            raise ValueError("Cannot map unknown monitor ID to new API.")

        return 'entity(SYNTHETIC_TEST-' + ent + ')'

########################################
    def raw(self, metrics, monid, pgeid=None, rltime=None, tstart=None,
            tend=None, group=None, header=None, sort=None, limit=None,
            skip=None, format=None):

        return self._rest_call()


########################################
    def set_proxy(self, proxy_address):
        self.proxies = {'http': proxy_address,
                        'https': proxy_address,
                        'ftp': False}

########################################
    def _get_rest_url(self):
        url = "%s://%s/%s" % (self.api_proto,
                              self.api_host,
                              '/'.join(self.api_path))

        return url

########################################
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
                      proxies=self.proxies,
                      timeout=self.timeout)
            
            call_result = {'rc': r.status_code,
                           'body': r.json()}
        else:
            call_result = self.mock

        return call_result['body']

########################################
    def _setMock(self, mock_data=True):
        self.mock = mock_data
