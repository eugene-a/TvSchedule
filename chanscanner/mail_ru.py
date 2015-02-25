import os.path
import json
import httplib2
from tv_schedule import config


_URL = 'http://tv.mail.ru/ext/admtv/?sch.main=1&sch.channel_type='

_http = httplib2.Http()

with open(os.path.join(config.output_dir(), 'mail_ru.txt'), 'w') as f:
    for i in range(1, 13):
        istr = str(i)
        content = _http.request(_URL + istr)[1].decode()
        chan_type = json.loads(content)['channel_type']
        l = chan_type.get(istr)
        if l is not None:
            for chan in l:
                ch_code = chan['url'].split('/')[2]
                s = '{}: "{}"'.format(chan['name'], ch_code)
                f.write(s + '\n')
                print(s)
