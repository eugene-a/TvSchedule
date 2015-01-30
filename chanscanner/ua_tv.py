import os.path
import lxml.html
from tv_schedule import config

URL = 'http://tv.ua/channels'

tree = lxml.html.parse(URL)
doc = tree.getroot()
channels = doc. get_element_by_id('channels')

with open(os.path.join(config.output_dir(), 'tv_ua.txt'), 'w') as f:
    for a in channels.find_class('orange'):
        ch_code = os.path.basename(a.get('href'))
        ch_code = '"' + ch_code[ch_code.rindex('-') + 1:] + '"'
        f.write('{}: {}\n'.format(a[0].text,  ch_code))
