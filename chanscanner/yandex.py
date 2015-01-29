import os.path
import httplib2
import lxml.etree
from tv_schedule import config
URL = 'https://tv.yandex.ru/87/channels/'
parser = lxml.etree.HTMLParser(encoding='utf-8')

http = httplib2.Http(ca_certs=r'c:\Downloads\tv.yandex.ru.crt')

with open(os.path.join(config.output_dir(), 'yandex.txt'), 'w') as f:
    for i in range(0, 1398):
        url = URL + str(i)
        content = http.request(url)[1]
        if len(content) > 0:
            doc = lxml.etree.fromstring(content, parser)
            channel = doc[1][0][1][0][0].text
            s = "{}: '{}'".format(channel, i)
            f.write(s + '\n')
            print(s)
