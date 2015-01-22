import itertools
import lxml.etree
import os.path

from tv_schedule import config

URL = 'http://tv.akado.ru/channels'

tree = lxml.etree.parse(URL, lxml.etree.HTMLParser(encoding='utf-8'))
doc = tree.getroot()
div = doc[1][0][4][0][0][0]

with open(os.path.join(config.output_dir(), 'akado.txt'), 'w') as f:
    for table in itertools.islice(div, 1, len(div) - 1):
        for row in table[1]:
            a = row[0][0][0]
            f.write("'{0}': '{1}',\n".format(a.text, a.get('href')[:-5]))
