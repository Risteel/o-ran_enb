#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
import subprocess
import paho.mqtt.client as mqtt

# base = 'https://sdnc-web:8453'
base = 'https://192.168.60.158:8453'
#base = 'https://oranyyds.connectivity.tw'
username = 'admin'
password = 'Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U'
requests.packages.urllib3.disable_warnings()


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


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("ORAN/MQTTYYDS")

def on_message(client, userdata, msg):
    send = False
    content = msg.payload.decode('utf-8')
    print(msg.topic+" "+ content)
    send = True
    nfName = "o-eNB"
    if send is True:
        if content == "1":
            write_config("DoS", "Connlab", "MAJOR")
            print("DoS")
        elif content == "2":
            write_config("Send SIB12", "Connlab", "CRITICAL")
            print("SIB12")
        elif content == "3":
            write_config("DNS Attack", "Connlab", "MAJOR")
            print("DNS Attack")
        print("Set send: ", "o-eNB", configEventSettings(nfName, "o-ran-enb", "/event-settings_send.json"))
        time.sleep(1) 
        print("Set don't send: ", "o-eNB", configEventSettings(nfName, "o-ran-enb", "/event-settings_no_send.json"))
    # call api


# main

client = mqtt.Client()

client.on_connect = on_connect

client.on_message = on_message

client.username_pw_set("connlab","LCCYCH507")

client.connect("connmqttlab.jed.tw", 1883, 60)

client.loop_forever()