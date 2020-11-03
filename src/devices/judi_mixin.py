
class JudiStandardMixin:
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

        if hasattr(self, 'signals') and hasattr(self.signals, 'handshake_recieved'):
            self.signals.handshake_recieved.emit(response)

    def locate(self):
        self.send('{"command":"locate"}')