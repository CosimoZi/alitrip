# coding: utf-8
from __future__ import unicode_literals
import traceback
import cPickle
import json
import jinja2
from jinja2 import Environment, FileSystemLoader


class BaseCounter:
    '''BaseCounter是所有counter的基类.初始化需要传入文件地址,parser负责解析行,strainer负责过滤符合要求的行,extractor负责从符合要求的行中提取信息并存储到类中.'''

    def __init__(self, files):
        self.files = files if isinstance(files, (tuple, list)) else [files]
        self.data = {}

    def strainer(self, line):
        return True

    def extractor(self, line):
        pass

    def parse(self, line):
        return line

    def analyze(self):
        for file in self.files:
            with open(file) as f:
                for line in f:
                    try:
                        line = self.parse(line)
                        if self.strainer(line):
                            self.extractor(line)
                    except Exception, e:
                        print line
                        traceback.print_exc()
                        # raise
                        continue

    def reprocess(self):
        pass

    def get_data(self):
        self.analyze()
        self.reprocess()
        return self.data


class BaseService:
    counter = None

    def get_date(self):
        if isinstance(self.files, (str, unicode)):
            date = self.files.split('.')[-1][:8]
            if date.isdigit():
                return date
        elif isinstance(self.files, (list, tuple)):
            date = self.files[0].split('.')[-1][:8]
            if date.isdigit():
                return date

    def __init__(self, files, mode=0):
        self.data_path = 'data/' + self.__class__.__name__ + 'Data'
        self.files = files
        self.date = self.get_date()
        # print self.date
        if mode == 0:
            self.data = self.counter(files).get_data()
            cPickle.dump(self.data, open(self.data_path, 'wb'), protocol=cPickle.HIGHEST_PROTOCOL)
        elif mode == 1:
            self.data = cPickle.load(open(self.data_path))

    def store(self):
        pass


class AlitripCounter(BaseCounter):
    def parse(self, line):
        line_parts = line.split('#')
        # [{"depCityCode":"NKG","arrCityCode":"HKG","depDate":"2016-09-07"},{"depCityCode":"HKG","arrCityCode":"NKG","depDate":"2016-09-14"}]
        journey = eval(line_parts[0])
        if len(journey) < 2: return
        condition = (journey[0]['depCityCode'], journey[0]['arrCityCode'], journey[0]['depDate'], journey[1]['depDate'])
        flightItems = json.loads(line_parts[2][line_parts[2].find('(') + 1:-2])['data']['flightItems']
        from pprint import pprint
        # for i in flightItems:
        #     if len(i['flightInfo'][0]['flightSegments']) > 1:
        #         return
        flight_items = {
            i['uniqKey']: {'leave_flight_number': i['flightInfo'][0]['flightSegments'][0]['marketingFlightNo'],
                           # 'back_flight_number': i['flightInfo'][0]['flightSegments'][1]['marketingFlightNo'],
                           'leave_depart_time': i['flightInfo'][0]['flightSegments'][0]['depTimeStr'],
                           # 'back_depart_time': i['flightInfo'][0]['flightSegments'][1]['depTimeStr'],
                           'leave_arrive_time': i['flightInfo'][0]['flightSegments'][0]['arrTimeStr'],
                           # 'back_arrive_time:': i['flightInfo'][0]['flightSegments'][1]['arrTimeStr'],
                           'price': float(i['totalAdultPrice']) / 100,
                           'leave_city_name': i['flightInfo'][0]['flightSegments'][0]['depCityName'],
                           'back_city_name': i['flightInfo'][0]['flightSegments'][0]['arrCityName']
                           } for i in flightItems if len(i['flightInfo'][0]['flightSegments']) < 2}
        return condition, line_parts[1], flight_items

    def strainer(self, line):
        if line:
            return True
        return False

    def extractor(self, line):
        conditon, crawl_time, flightItems = line
        self.data.setdefault(conditon, [crawl_time, {}])
        self.data[conditon][1].update(flightItems)


class AlitripService(BaseService):
    counter = AlitripCounter

    def store(self):
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('template.xml')
        xml = template.render(data=self.data)
        with open('output/statistics.xml', 'wb') as f:
            f.write(xml.encode('utf-8'))


if __name__ == '__main__':
    AlitripService('data/raw_data').store()
