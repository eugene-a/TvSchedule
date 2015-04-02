import os.path
import lxml.etree
from tv_schedule import config

URL = 'http://www.tv.lv/channels/'

parser = lxml.etree.HTMLParser()

tree = lxml.etree.parse(URL, parser)
doc = tree.getroot()

path = os.path.join(config.output_dir(), 'tv_lv.txt')
with open(path, 'w', encoding='utf-8') as f:
    for item in doc[1][6][2][0][0][2][0][0][0][0][2][1][1:]:
        it = item.iterchildren()
        f.write('{}: "{}"\n'.format(next(it)[0].text, next(it).get('data-id')))
