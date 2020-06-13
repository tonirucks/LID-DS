import base64
import os
import subprocess
from datetime import datetime, timedelta

from lid_ds.data_models import SysdigEvent
from lid_ds.postprocessing.tcpdump import get_first_attacker_package

MATCH_THRESHOLD = 0.8


def remove_date(date: datetime):
    return date - datetime(date.year, date.month, date.day)


def convert_b64_data_to_bytes(data):
    data = data.replace("data=", "").encode()
    return base64.b64decode(data)


def find_syscall_for_packet(file, packet):
    ts = remove_date(datetime.fromtimestamp(packet['time']))
    delta = timedelta(milliseconds=1000)
    ip_arg = "%s:%s->%s:%s" % (packet['src'], packet['sport'], packet['dst'], packet['dport'])

    p = subprocess.Popen('sysdig -br %s' % file, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    check_response_for = None
    while p.poll() is None:
        # returns None while subprocess is running
        line = p.stdout.readline()
        try:
            event = SysdigEvent(line)
            if check_response_for and event.event_type == "read" and not event.enter_event:
                if len(event.args) > 0 and "data=" in event.args[1]:
                    byte_data = convert_b64_data_to_bytes(event.args[1])
                    if byte_data in packet['data'] and len(byte_data) / len(packet['data']) > MATCH_THRESHOLD:
                        return check_response_for, event
            check_response_for = None
            if event.enter_event and event.event_type == "read" and ts - delta <= remove_date(event.event_time) <= ts + delta:
                # Check src->dst
                if ip_arg in event.args[0]:
                    check_response_for = event
        except:
            pass


if __name__ == '__main__':
    file_tcp = os.path.abspath("../../example/long_wozniak_2977.pcap")
    file_sysdig = os.path.abspath("../../example/long_wozniak_2977.scap")

    packet = get_first_attacker_package(file_tcp, "172.28.0.3")

    x = find_syscall_for_packet(file_sysdig, packet)
    print(x)
