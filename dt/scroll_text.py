class ScrollText:
    def __init__(self, text, left, right, start_pos):
        self.text = text
        self.left = left
        self.right = right
        self.pos = start_pos

    def scroll(self, text_length):
        self.pos -= 1
        if self.pos + text_length < self.left:
            self.pos = self.right
