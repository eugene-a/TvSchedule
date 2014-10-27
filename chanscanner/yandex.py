from httplib2 import Http
from lxml.etree import HTMLParser, fromstring


class Target:
    def __init__(self):
        self.state = 0
        self.channel = None

    def start(self, tag, attrib):
        if self.state == 0:
            if tag == 'span' and attrib.get('id') == 'ShowTime':
                self.state = 1
        elif self.state == 1:
            if tag == 'img':
                alt = attrib.get('alt')
                if alt:
                    self.channel = alt
                    self.state = 2

    def close(self):
        pass

http = Http()

with open('output\\yandex.txt', 'w') as f:
    for i in range(1663):
        url = 'http://tv.yandex.ru/?period=24&channel=' + str(i)
        content = http.request(url)[1]
        parser = HTMLParser(target=Target())
        fromstring(content, parser)

        channel = parser.target.channel
        if channel is not None:
            s = "'{0}': '{1}',".format(channel,  i)
            f.write(s + '\n')
            print(s)
