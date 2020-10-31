class NewlineFilter:
    def __init__(self):
        self.buffer = ""
        self.depth = 0

    def reset(self):
        self.buffer = ""
        self.depth = 0

    def insert_char(self, c):
        self.buffer += c
        return False

    def completed(self):
        if '\n' in self.buffer:
            return True
        return False