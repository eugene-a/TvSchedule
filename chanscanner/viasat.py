import os.path
import lxml.etree
from tv_schedule import config

URL = 'http://www.viasat.lv/viasat0/tv-programma27/tv-programma28/_/all/'

parser = lxml.etree.HTMLParser()
tree = lxml.etree.parse(URL, parser)
doc = tree.getroot()
chan_list = doc[1][0][5][0][3][0][1]

path = os.path.join(config.output_dir(), 'viasat.txt')

with open(path, 'w', encoding='utf-8') as f:
    for chan in chan_list[0: -1]:
        a = chan[0]
        ch_code = a.get('href').split('/')[-2]
        s = '{}: "{}"'.format(a.text.strip(), ch_code)
        f.write(s + '\n')
        print(s)
