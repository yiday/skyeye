# -*- coding:utf-8 -*-

import inspect
import time
import urllib, urllib2
import json
import socket


class HostHardMetric(object):
    def __init__(self):
        self.data = {}

    def get_time(self):
        return int(time.time()) * 10000000

    def get_host(self):
        return socket.gethostname()

    def get_load_avg(self):
        with open('/proc/loadavg') as load_fp:
            load1, load5, load15, _, _ = load_fp.read().split()
            return (load1, load5, load15)
            # return ','.join(load_fp.read().split()[:3])

    def get_mem_total(self):
        with open('/proc/meminfo') as mem_fp:
            return mem_fp.readline().split()[1]

    def get_mem_usage(self, buff_cache=True):
        if buff_cache:
            with open('/proc/meminfo') as mem_fp:
                total = int(mem_fp.readline().split()[1])
                free = int(mem_fp.readline().split()[1])
                buff = int(mem_fp.readline().split()[1])
                cached = int(mem_fp.readline().split()[1])
                return total - free - buff - cached
        else:
            with open('/proc/meminfo') as mem_fp:
                return int(mem_fp.readline().split()[1]) - int(mem_fp.readline().split()[1])

    def get_mem_free(self, buff_cache=True):
        if buff_cache:
            with open('/proc/meminfo') as mem_fp:
                free = int(mem_fp.readline().split()[1])
                buff = int(mem_fp.readline().split()[1])
                cached = int(mem_fp.readline().split()[1])
                return free + buff + cached
        else:
            with open('/proc/meminfo') as mem_fp:
                mem_fp.readline()
                return mem_fp.readline().split()[1]

    def run_all_metric(self):
        for func in inspect.getmembers(self, predicate=inspect.ismethod):
            if func[0][:3] == 'get':
                self.data[func[0][4:]] = func[1]()
        return self.data


def post(url, data):
    req = urllib2.Request(url)
    data = urllib.urlencode(data)
    # enable cookie
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req, data)
    return response.read()


if __name__ == '__main__':
    influxdb_url = 'http://localhost:8086/write?db=mydb'
    # data = "cpu_load_short,host=server01,region=us-west value=11.22,value2=13.89"
    #
    obj = HostHardMetric()
    print obj.get_mem_total()
    print obj.get_mem_usage()
    # exit()
    # load1, load5,load15 = loadobj.get_load_avg()
    while True:
        data = obj.run_all_metric()

        metric_data = """
        load_info,host={host} load1={load1},load5={load5},load15={load15}
        mem_info,host={host} mem_total={mem_total},mem_free={mem_free},mem_usage={mem_usage}
        """.format(host=data['host'], load1=data['load_avg'][0], load5=data['load_avg'][1],
                   load15=data['load_avg'][2],
                   mem_total=data['mem_total'],
                   mem_free=data['mem_free'],
                   mem_usage=data['mem_usage']
                   )
        print metric_data
        # exit()
        request = urllib2.Request(influxdb_url,
                                  metric_data,
                                  {'Content-Type': 'application/octet-stream'}
                                  )
        urllib2.urlopen(request)

        time.sleep(5)
    # while True:
    #     obj = HostHardMetric()
    #     data = obj.run_all_metric()
    #     print data
    #     time.sleep(1)
