class JSONBuffer:
    """A utility class that helps keep track of an incoming JSON message.
    """

    def __init__(self):
        self.buffer = ""
        self.depth = 0

    def reset(self):
        self.buffer = ""
        self.depth = 0

    def insert_char(self, c):
        """Insert a single char into the buffer.
        """
        if c == "{":
            self.depth += 1
        if self.depth > 0:
            self.buffer += c
        if c == "}":
            self.depth -= 1

    def completed(self):
        """Check if the MessageBuffer contains a completed JSON message.
        """
        if (self.depth == 0) and (len(self.buffer) > 0):
            return True
        return False