import os.path
import httplib2
import lxml.etree
from encodings import cp866
from tv_schedule import config

http = httplib2.Http()
parser = lxml.etree.HTMLParser()

# print ukrainian 'i' to console as latin 'i'
cp866.encoding_map[ord('і')] = cp866.encoding_map[ord('i')]

with open(os.path.join(config.output_dir(), 'vsetv.txt'), 'w') as f:
    hdrs = {
        'user-agent':
            'Mozilla/5.0 (Windows NT 6.1; rv:9.0) Gecko/20100101 Firefox/9.0'
    }
    for i in range(1, 1019):
        url = 'http://www.vsetv.com/schedule_channel_{}_week.html'.format(i)
        content = http.request(url, headers=hdrs)[1]
        doc = lxml.etree.fromstring(content, parser)
        table = doc[3][6]           # <!-- Base Table (1 колонка / 8 строк) -->
        chlogo = table[3][0][2]
        if chlogo.tag == 'div':
            channel = chlogo[0].get('alt')
            s = "{}: '{}'".format(channel, i)
            f.write(s + '\n')
            print(s)
