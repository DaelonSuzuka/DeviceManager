from qt import *
import time
import json
import logging
from .utils import get_ip
import socket


class Host:
    def __init__(self, address, beacon_message, timeout=10):
        host_data = json.loads(beacon_message)

        self.hostname = host_data['hostname']
        self.judi_control_port = host_data['judi_remote_port']
        self.address = address
        self.update()

        self.timeout = timeout

    def __repr__(self):
        return f'<{self.hostname}@{self.address}:{self.judi_control_port}>'

    def update(self):
        self.active = True
        self.last_message_time = time.time()

    def check_timeout(self):
        if (time.time() - self.last_message_time) > self.timeout:
            self.active = False
        return self.active


class DiscoveryService(QObject):
    host_found = Signal(Host)
    host_lost = Signal(Host)

    def __init__(self, parent=None, beacon_port=7755, judi_port=43000):
        super().__init__(parent=parent)
        self.log = logging.getLogger(__name__ + '.discovery')
        
        self.port = beacon_port
        self.hostname = socket.gethostname()
        self.hosts = {}

        self.beacon = QUdpSocket(self)
        self.beacon.bind(QHostAddress(get_ip()), self.port, mode=QAbstractSocket.ShareAddress)

        self.watcher = QUdpSocket(self)
        self.watcher.bind(QHostAddress('0.0.0.0'), self.port, mode=QAbstractSocket.ShareAddress)

        self.beacon_timer = QTimer()
        self.beacon_timer.timeout.connect(self.update)
        
        msg = '{"hostname":"%s","judi_remote_port":"%s"}' % (self.hostname, str(judi_port))
        self.beacon_message = QByteArray(msg.encode())
        
        self.start()

    def start(self):
        self.log.info(f'starting discovery service')
        self.update()
        self.beacon_timer.start(5000)
        self.watcher.readyRead.connect(self.get_message)

    def stop(self):
        self.log.info(f'stopping discovery service')
        self.beacon_timer.stop()
        self.watcher.readyRead.disconnect(self.get_message)

    def update(self):
        self.beacon.writeDatagram(self.beacon_message, QHostAddress.Broadcast, self.port)

        for _, host in self.hosts.items():
            if host.active and not host.check_timeout():
                self.log.info(f'host lost {host}')
                self.host_lost.emit(host)
                
    def get_message(self):
        if self.watcher.pendingDatagramSize() != -1:
            dg = self.watcher.receiveDatagram(self.watcher.pendingDatagramSize())

            address = dg.senderAddress().toString()
            port = dg.senderPort()

            # reject our own datagrams
            if address == get_ip():
                return

            msg = bytes(dg.data()).decode()

            self.log.debug(f'RX: [{address}:{port}] {msg}')

            if address not in self.hosts:
                self.hosts[address] = Host(address, msg)
                self.log.info(f'host found {self.hosts[address]}')
                self.host_found.emit(self.hosts[address])

            if address in self.hosts:
                if not self.hosts[address].active:
                    self.log.info(f'host found {self.hosts[address]}')
                    self.host_found.emit(self.hosts[address])

                self.hosts[address].update()