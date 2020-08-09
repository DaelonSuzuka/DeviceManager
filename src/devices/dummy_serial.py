class DummySerial:
    def __init__(self, port=None, timeout=0):
        self.port = port
        self.read_buffer = ""
        self.responder = DummyResponder()

    def open(self):
        pass

    def close(self):
        pass

    def write(self, string):
        if self.responder:
            self.read_buffer += self.responder.respond(string.decode())

    def read(self, number=1):
        result = ""
        for i in range(number):
            result += self.read_buffer[:1]
            self.read_buffer = self.read_buffer[1:]
        return result.encode()

    @property
    def in_waiting(self):
        return len(self.read_buffer)


class DummyResponder:
    def respond(self, string):
        return ""