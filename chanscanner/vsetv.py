from httplib2 import Http
from lxml.etree import HTMLParser, fromstring
from encodings import cp866
from os.path import join
from tv_schedule.config import output_dir

http = Http()
parser = HTMLParser()

# print ukrainian 'i' to console as latin 'i'
cp866.encoding_map[ord('і')] = cp866.encoding_map[ord('i')]

with open(join(output_dir(), 'vsetv.txt'), 'w') as f:
    hdrs = {
        'user-agent':
            'Mozilla/5.0 (Windows NT 6.1; rv:9.0) Gecko/20100101 Firefox/9.0'
    }
    for i in range(1, 1016):
        url = 'http://www.vsetv.com/schedule_channel_{0}_week.html'.format(i)
        content = http.request(url, headers=hdrs)[1]
        doc = fromstring(content, parser)
        table = doc[3][6]           # <!-- Base Table (1 колонка / 8 строк) -->
        chlogo = table[3][0][2]
        if chlogo.tag == 'div':
            channel = chlogo[0].get('alt')
            s = "'{0}': '{1}',".format(channel, i)
            f.write(s + '\n')
            print(s)
