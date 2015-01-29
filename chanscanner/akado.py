import itertools
import os.path
import lxml.etree
from tv_schedule import config

URL = 'http://tv.akado.ru/channels'
parser = lxml.etree.HTMLParser(encoding='utf-8')

tree = lxml.etree.parse(URL, parser)
doc = tree.getroot()
div = doc[1][0][4][0][0][0]

with open(os.path.join(config.output_dir(), 'akado.txt'), 'w') as f:
    for table in itertools.islice(div, 1, len(div) - 1):
        for row in table[1]:
            a = row[0][0][0]
            ch_code = os.path.splitext(a.get('href'))[0]
            f.write("{}: {}\n".format(a.text, ch_code))
