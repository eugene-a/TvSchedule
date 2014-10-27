from encodings import cp866

import cp1251m
from util import no_idle
from schwriter import write_schedule

cp1251m.register()

#print ukrainian 'i' to console as latin 'i'
cp866.encoding_map[ord('і')] = cp866.encoding_map[ord('i')]

no_idle()
write_schedule('tv_schedule.ini')
