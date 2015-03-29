import os.path
import itertools
import httplib2
import lxml.etree
from tv_schedule import config

URL = 'http://tvgid.ua/setup/'
http = httplib2.Http()
parser = lxml.etree.HTMLParser()

content = http.request(URL)[1]
doc = lxml.etree.fromstring(content, parser)
tr = doc[1][1][0][0][0][0][0][1][1][0][0][0][1][0][1]

with open(os.path.join(config.output_dir(), 'tvgid.txt'), 'w') as f:
    for inp in itertools.islice(itertools.chain(*tr), 0, None, 3):
        s = "{}: '{}'\n".format(inp.getnext().text, inp.get('value'))
        f.write(s)
