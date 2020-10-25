import json
from .serial_device_base import SerialDeviceBase
from time import time
import logging
from qt import *

fake_guid = 0

def get_fake_guid():
    global fake_guid
    guid = fake_guid
    fake_guid += 1
    return str(guid)


class CommonMessagesMixin:
    @property
    def common_message_tree(self):
        return {
            'update': {
                'device_info': self.handshake_recieved
            },
            'response': {
                'ok': None, 
                'error': None
            }
        }

    def ping(self):
        self.send('{"request":{"ping":"%s"}}' % (self.msg_count))

    def handshake(self):
        self.send('{"request":"device_info"}')

    def handshake_recieved(self, response):
        if 'product_name' in response:
            self.name = response['product_name']
        if 'serial_number' in response:
            self.guid = response['serial_number']
        if 'firmware_version' in response:
            self.firmware_version = response['firmware_version']
        if 'protocol_version' in response:
            self.protocol_version = response['protocol_version']

    def locate(self):
        self.send('{"command":"locate"}')


class MessageTree(dict):
    def merge(self, d):
        for key in d:
            if key in self:
                self[key].update(d[key])
            else:
                self[key] = d[key]


class DeviceContextLogFilter(logging.Filter):
    def __init__(self, device):
        self.device = device

    def filter(self, record):
        record.port = self.device.port
        record.guid = self.device.guid
        record.baud = self.device.baud
        record.profile_name = self.device.profile_name
        return True


class SerialDevice(SerialDeviceBase):
    profile_name = ""
    
    def __init__(self, port=None, baud=9600, device=None):
        self.port = port
        self.baud = baud
        self.name = ""
        self.guid = get_fake_guid()
        
        # a SerialDevice can be created based on an existing SerialDevice
        if device:
            self.port = device.port
            self.baud = device.baud
            self.name = device.name
            self.guid = device.guid

        super().__init__(port=self.port, baud=self.baud)

        # self.log = logging.getLogger(f'{__name__}.{self.profile_name}.{self.guid}')
        self.log = logging.getLogger(f'{__name__}.{self.profile_name}')
        self.log.addFilter(DeviceContextLogFilter(self))
        self.log.info(f'Creating device')

        self.signals = None
        self.time_created = time()

        # message stuff
        self.msg_count = 0
        self.message_tree = MessageTree()
        self.msg_history = []       

    @property
    def title(self):
        return f"{self.profile_name} ({self.port}) <{self.guid}>"

    @property
    def description(self):
        return {
            "profile_name":self.profile_name,
            "guid":self.guid,
            "port":self.port,
            "title":self.title,
        }

    def process_message(self, msg, table):
        # TODO: catch KeyErrors
        if self.message_tree is not None:
            for k in msg.keys():
                # does the table list an action?
                if k in table.keys() and callable(table[k]):
                    table[k](msg[k])

                # can we go deeper?
                elif isinstance(msg[k], dict):
                    if k in table.keys():
                        self.process_message(msg[k], table[k])

    def recieve(self, string):
        super().recieve(string)

        try:
            msg = json.loads(string)
            self.process_message(msg, self.message_tree)
        except json.decoder.JSONDecodeError as e:
            self.log.warn("JSONDecodeError" + str(e))

