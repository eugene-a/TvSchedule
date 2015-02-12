import os.path
import lxml.etree
from tv_schedule import config

URL = 'http://www.ntvplus.ru/tv/#genre=3494'

parser = lxml.etree.HTMLParser()

tree = lxml.etree.parse(URL, parser)
doc = tree.getroot()

with open(os.path.join(config.output_dir(), 'ntvplus.txt'), 'w') as f:
    channels = doc[1][5][0][4][0][0][1]
    for label in channels[:-2]:
        inp = label[0]
        f.write('{}: "{}"\n'.format(inp.tail, inp.get('id')))
