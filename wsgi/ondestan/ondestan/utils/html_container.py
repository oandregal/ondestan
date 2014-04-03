# coding=UTF-8


class HtmlContainer:
    def __init__(self, content):
        self.content = content

    def __html__(self):
        return self.content
