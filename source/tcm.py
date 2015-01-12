from itertools import takewhile, islice

from httplib2 import Http
from lxml.etree import fromstring, HTMLParser
from pytz import timezone

from schedule import Schedule
from util import get_date

source_tz = timezone('Europe/London')
http = Http()
parser = HTMLParser()

months = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12 
    }
    
def get_schedule(channel,  tz):
    url = 'http://www.tcmeurope.com/K/tvguide.php?days_ahead='
  
    schedule = Schedule(tz, source_tz)
    
    for days_ahead in '0', '3', '6':
        content = http.request(url + days_ahead)[1]
        doc = fromstring(content, parser)
        
        is_column = lambda x: x.get('class') == 'tvguide_column'
        
        for column in takewhile(is_column, doc[1][0][0][1][1]):                
            date = column[0].text.split()
            date = get_date(months[date[2][:3]], int(date[1]))
            schedule.set_date(date)
            
            for listing in islice(column, 1,  None):
                schedule.set_time(listing[0].text)
                schedule.set_title(listing[1].text)
                schedule.set_summary(listing[2].text)
                
    return schedule.pop()
        
