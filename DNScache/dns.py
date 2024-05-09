from __future__ import annotations
from dnslib import A, DNSRecord, QTYPE, RR
from typing import Union
import json
import socket
import time


class ClassDNS:
    def __init__(self, host:str):
        self.cache:set = {}
        self.fetch()
        self.socket:socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, 53))
        self.q_type:Union[None,str] = None

    DNS_IPs = ["185.228.168.9", "185.121.177.177", "45.32.230.225", "50.116.23.211",
                    "192.203.230.10", "192.5.5.241", "192.112.36.4",
                    "198.97.190.53", "192.36.148.17", "192.58.128.30",
                    "193.0.14.129", "199.7.83.42", "202.12.27.33"]
    
    def server(self) -> None:
        while True:
            data, addr = self.socket.recvfrom(512)
            dns_record = DNSRecord.parse(data)
            q_name = dns_record.q.qname.__str__()
            if dns_record.q.qtype != 1:
                self.socket.sendto(data, addr)
            elif 'multiply' in q_name:
                self.socket.sendto(self.recieve_resp(dns_record), addr)
            else:
                if q_name in self.cache:
                    reply = self.get_records(dns_record, q_name)
                    if reply.a.rdata:
                        self.socket.sendto(reply.pack(), addr)
                        continue
                    else:
                        del self.cache[q_name]
                result = None
                for root_server in ClassDNS.DNS_IPs:
                    self.q_type = dns_record.q.qtype
                    result = self.lookup(dns_record, root_server)
                    if result:
                        break
                self.data_result(q_name, DNSRecord.parse(result))
                self.socket.sendto(result, addr)

    def get_records(self, dns_record:DNSRecord, q_name:str) -> DNSRecord.reply:
        reply = dns_record.reply()
        current_time = time.time()
        for answer in self.cache[q_name]:
            if answer[2] + answer[1] - current_time >= 0:
                rr = RR(rname=q_name, rtype=QTYPE.A,
                        rdata=A(answer[0]), ttl=answer[1])
                reply.add_answer(rr)
        return reply

    def data_result(self, request:str, result: DNSRecord) -> None:
        answers = []
        for rr in result.rr:
            answers.append((rr.rdata.__str__(), rr.ttl, time.time()))
        if len(answers) == 0:
            return
        self.cache[request] = answers
        self.update_cache()

    def update_cache(self) -> None:
        with open('cache.json', 'w') as cache:
            json.dump(self.cache, cache)

    def fetch(self) -> None:
        try:
            with open('cache.json', 'r') as cache:
                data = json.load(cache)
                if data:
                    self.cache = data
        except FileNotFoundError:
            self.update_cache()

    def lookup(self, dns_record: DNSRecord, zone_ip:str) -> Union[None,bytes]:
        response = dns_record.send(zone_ip)
        parsed_response = DNSRecord.parse(response)
        for adr in parsed_response.auth:
            if adr.rtype == 6:
                return response
        if parsed_response.a.rdata:
            return response
        new_zones_ip = self.get_new_zones_ip(parsed_response)
        for new_zone_ip in new_zones_ip:
            ip = self.lookup(dns_record, new_zone_ip)
            if ip:
                return ip
        return None

    def get_new_zones_ip(self, parsed_response:DNSRecord) -> list:
        new_zones_ip = []
        for adr in parsed_response.ar:
            if adr.rtype == 1:
                new_zones_ip.append(adr.rdata.__repr__())
        if len(new_zones_ip) == 0:
            for adr in parsed_response.auth:
                if adr.rtype == 2:
                    question = DNSRecord.question(adr.rdata.__repr__())
                    pkt = self.lookup(question, ClassDNS.DNS_IPs[0])
                    parsed_pkt = DNSRecord.parse(pkt)
                    new_zone_ip = parsed_pkt.a.rdata.__repr__()
                    if new_zone_ip:
                        new_zones_ip.append(new_zone_ip)
        return new_zones_ip

    def recieve_resp(self, dns_record: DNSRecord):
        name = dns_record.q.qname.__str__()
        index = name.find('multiply')
        zones = name[:index].split('.')
        sch = 0
        for zone in zones:
            try:
                number = int(zone)
                if sch == 0:
                    sch = 1
                sch *= number
            except ValueError:
                continue
        sch %= 256
        reply_ip = f'127.0.0.{sch}'
        reply = dns_record.reply()
        reply.add_answer(RR(dns_record.q.qname, QTYPE.A,
                            rdata=A(reply_ip), ttl=60))
        return reply.pack()


if __name__ == "__main__":
    ClassDNS('127.0.0.1').server()
