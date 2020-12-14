class DelimiterFilter:
    def __init__(self, start=None, end=None):
        self.buffer = ""
        self.depth = 0
        self.start = start
        self.end = end

    def reset(self):
        self.buffer = ""
        self.depth = 0

    def insert_char(self, c):
        self.buffer += c
        
        return self.completed()

    def completed(self):
        if self.end is None:
            if self.start in self.buffer:
                return True
        else:
            if self.end in self.buffer and self.start not in self.buffer:
                self.buffer = ""

            if self.end in self.buffer:
                return True

        return False