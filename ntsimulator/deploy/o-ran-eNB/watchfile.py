#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
import subprocess
from os.path import expanduser
import paho.mqtt.client as mqtt
from watchdog.events import *
from watchdog.observers import Observer
home = expanduser("~")

#base = 'https://sdnc-web:8453'
base = 'https://10.118.126.72:8453'
#base = 'https://oranyyds.connectivity.tw'
username = 'admin'
password = 'Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U'
requests.packages.urllib3.disable_warnings()


class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {} to {}".format(event.src_path,event.dest_path))
        else:
            print("file moved from {} to {}".format(event.src_path,event.dest_path))
            self.task(filName = event.dest_path)

    def on_created(self, event):
        if event.is_directory:
            print("directory created:{}".format(event.src_path))
        else:
            print("file created:{}".format(event.src_path))

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{}".format(event.src_path))
        else:
            print("file deleted:{}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{}".format(event.src_path))
        else:
            print("file modified:{}".format(event.src_path))
            if "alarm_config" in event.src_path:
                with open(event.src_path, 'r') as fp:
                    content = fp.read().strip().split('\n')
                    print(content)
                    if len(content) == 3:
                        send_message(content[1], content[0], content[2])

    def task(self, filName):
        print(filename)

# REST to set event settings
def configEventSettings(nfName, nfType, file_name):
  file_send = os.path.dirname(os.path.abspath(__file__)) + '/' + nfType + file_name #'/event-settings_send.json'
  #file_no_send = os.path.dirname(os.path.abspath(__file__)) + '/' + nfType + '/event-settings_no_send.json'
  with open(file_send) as json_file:
    body = json.load(json_file)
    url = base + '/rests/data/network-topology:network-topology/topology=topology-netconf/node=' + nfName + '/yang-ext:mount/nts-network-function:simulation/network-function'
    headers = {
        'content-type': 'application/yang-data+json',
        'accept': 'application/yang-data+json'
    }
    try:
      response = requests.put(url, verify=False, auth=(username, password), json=body, headers=headers)
    except requests.exceptions.Timeout:
      sys.exit('HTTP request failed, please check you internet connection.')
    except requests.exceptions.TooManyRedirects:
      sys.exit('HTTP request failed, please check your proxy settings.')
    except requests.exceptions.RequestException as e:
      # catastrophic error. bail.
      raise SystemExit(e)

    return response.status_code >= 200 and response.status_code < 300

def write_config(condition, object_str, severity):
    start = '{\n'
    rules_start = '\t"fault-rules" : {\n'
    header_notif = '\t\t"yang-notif-template" : "<alarm-notif xmlns=\\"urn:o-ran:fm:1.0\\"><fault-id>$$uint16_counter$$</fault-id><fault-source>%%object%%</fault-source><affected-objects><name>%%affected-object%%</name></affected-objects><fault-severity>%%fault-severity%%</fault-severity><is-cleared>%%cleared%%</is-cleared><fault-text>%%text%%</fault-text><event-time>%%date-time%%</event-time></alarm-notif>",\n'
    header_method = '\t\t"choosing-method" : "linear",\n'
    fault_start = '\t\t"faults" : [\n'
    fault_content_start = '\t\t\t{\n'
    fault_content_condition = '\t\t\t\t"condition" : "' + condition + '",\n'
    fault_content_object = '\t\t\t\t"object" : "' + object_str + '",\n'
    fault_content_severity = '\t\t\t\t"severity" : "' + severity + '",\n'
    fault_content_time = '\t\t\t\t"date-time" : "$$time$$",\n'
    fault_content_problem = '\t\t\t\t"specific-problem" : "' + condition + '",\n\n'
    fault_content_severity_2 = '\t\t\t\t"fault-severity" : "' + severity + '",\n'
    fault_content_affected = '\t\t\t\t"affected-object" : "%%object%%",\n'
    fault_content_cleared = '\t\t\t\t"cleared" : "false",\n'
    fault_content_text = '\t\t\t\t"text" : "' + condition + '"\n'
    fault_content_end = '\t\t\t}\n'
    fault_end = '\t\t]\n'
    rules_end = '\t}\n'
    end = '}\n'
    content = start + rules_start + header_notif + header_method + fault_start
    content = content + fault_content_start + fault_content_condition
    content = content + fault_content_object + fault_content_severity
    content = content + fault_content_time + fault_content_problem
    content = content + fault_content_severity_2 + fault_content_affected
    content = content + fault_content_cleared + fault_content_text
    content = content + fault_content_end + fault_end + rules_end + end
    file = open("/opt/dev/ntsim-ng/config/config_fault.json", "w")
    file.write(content)
    file.close()

def send_message(condition, object_str, severity):
    send = True
    nfName = "o-eNB"
    if send is True:
        write_config(condition, object_str,severity)
        print(condition)
        print("Set send: ", "o-eNB", configEventSettings(nfName, "o-ran-enb", "/event-settings_send.json"))
        time.sleep(1) 
        print("Set don't send: ", "o-eNB", configEventSettings(nfName, "o-ran-enb", "/event-settings_no_send.json"))
    # call api

if __name__ == "__main__":
    home = os.path.expanduser("~")
    #print(home + "/file_test")
    observer = Observer()
    event_handler = FileEventHandler()
    filePath = "/opt/dev/ntsim-ng/config/" #home + "/file_test"
    observer.schedule(event_handler, filePath, True)
    observer.start()
    while True:
        time.sleep(60)
