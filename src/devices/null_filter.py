class NullFilter:
    def __init__(self):
        self.buffer = ""

    def reset(self):
        self.buffer = ""

    def insert_char(self, c):
        self.buffer += c
        return False

    def completed(self):
        if self.buffer:
            return True 
        return False