import json
import logging
import os
import subprocess
import threading
import time
from datetime import datetime, timedelta
from time import sleep
import paho.mqtt.client as mqtt
from AttackerBase import AttackerBase
from MqttHelper import read_mqtt_params
import queue


class AttackerRemote(AttackerBase):

    def __init__(self):
        AttackerBase.__init__(self, 'attacker_remote')

        self.__attack_sname_to_fname_mapper = {
            'ip-scan': 'scan-scapy',
            'port-scan': 'scan-nmap',
            'ddos': 'ddos',
            'replay': 'replay-scapy',
            'mitm': 'mitm-scapy'
        }

        self.attacksQueue = queue.Queue()
        self.client = mqtt.Client()
        self.setup_mqtt = threading.Thread(target=self.setup_mqtt_client)
        self.setup_mqtt.start()

    def setup_mqtt_client(self):
        temp_address = "../input/sample_mqtt_connection.txt"

        connection_params = read_mqtt_params(temp_address)
        connection_params['topic'] = connection_params['topic'] + '/#'
        print(connection_params)

        # Set up callback functions
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message

        if connection_params.keys().__contains__('username') and connection_params.keys().__contains__('password'):
            print('password')
            username = connection_params['username']
            password = connection_params['password']
            self.client.username_pw_set(username, password)

        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message

        self.client.connect(connection_params['address'], int(connection_params['port']))

        self.client.subscribe(connection_params['topic'], qos=1)
        self.client.loop_forever()

    def on_subscribe(self, client, userdata, mid, granted_qos):
        self.report("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(self, client, userdata, msg):
        self.report("message received")
        self.report(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        self.attacksQueue.put(msg)

    def _logic(self):
        if not self.attacksQueue.empty():
            self.process_messages(self.attacksQueue.get())
        time.sleep(2)

    def process_messages(self, attack_data):
        self.report('attacker_remote start apply following attack')
        attack_dic = json.loads(attack_data.payload.decode("utf-8"))
        json_attack_key = "attack"

        if not attack_dic.keys().__contains__(json_attack_key):
            print(attack_dic)
            self.report('Json is invalid. cannot find attack tag!', level=logging.ERROR)
            return
        attack_short_name = attack_dic[json_attack_key]

        if not self.__attack_sname_to_fname_mapper.keys().__contains__(attack_short_name):
            self.report(f'cannot find any script for attack = \'{attack_short_name}\'', level=logging.ERROR)
            return
        attack_full_name = self.__attack_sname_to_fname_mapper[attack_short_name]

        self._apply_attack(attack_short_name, attack_full_name)






if __name__ == '__main__':
    attackerRemote = AttackerRemote()
    attackerRemote.start()
