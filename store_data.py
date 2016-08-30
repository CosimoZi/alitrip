# coding: utf-8
from netlib.http import decoded
from threading import Lock
import urlparse
import time
import re

searchJourney_pattern = re.compile('searchJourney=([^&]+)&')

lock=Lock()

def response(context, flow):
    with decoded(flow.response):
        if '"flightItems":[{"uniqKey"' in flow.response.body:
            with lock:
                with open('data/raw_data', mode='ab') as file:
                    file.write(
                        '#'.join(
                            (urlparse.unquote(searchJourney_pattern.search(flow.request.url).group(1)), time.ctime(),
                             flow.response.body.decode('gbk').encode('utf-8').strip() + '\n')))
                    file.flush()
