from itertools import islice
from lxml.etree import parse, HTMLParser
from os.path import join
from tv_schedule.config import output_dir

tree = parse('http://tv.akado.ru/channels', HTMLParser(encoding='utf-8'))
doc = tree.getroot()
div = doc[1][0][4][0][0][0]
with open(join(output_dir(), 'akado.txt'), 'w') as f:
    for table in islice(div, 1, len(div) - 1):
        for row in table[1]:
            a = row[0][0][0]
            f.write("'{0}': '{1}',\n".format(a.text, a.get('href')[:-5]))
