import requests
import json
import subprocess
import re


def func(site):
    sch = 0
    try:
        tracer = subprocess.Popen(
            ["tracert", site], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        IP_REGEX = re.compile(r"(?P<IP>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
        while sch < 10:
            for line in tracer.stdout:
                line = line.decode('cp866')
                print(line)
                match_ip = IP_REGEX.search(line)
                if match_ip and "*" not in line:
                    IPs.append(match_ip.group("IP"))
                    sch+=1
                elif "*" in line:
                    break
            if "*" in line:
                    break
        main = IPs[0]
        IPs.pop(0)
        IPs.append(main)
        find_ip(IPs, main)
        tracer.wait()
    except Exception as ex:
        print(ex)


def find_ip(arr, ip):
    IPs = arr
    try:
        data = json.dumps(IPs)
        response = requests.post(endpoint, data=data)
        response = response.json()
        for item in response:
            if (
                "org" in item.keys()
                and "query" in item.keys()
                and "city" in item.keys()
                and "country" in item.keys()
            ):
                print(
                    item["org"]
                    + " has an ip "
                    + item["query"]
                    + " and is in "
                    + item["city"]
                    + ", "
                    + item["country"]
                )
            else:
                print(item["query"])
        raise Exception
    except Exception as ex:
        print(ex)


IPs = []
site = "gazprom.ru"
endpoint = "http://ip-api.com/batch"
func(site)
