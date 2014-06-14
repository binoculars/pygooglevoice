__author__ = 'Barrett K. Harber'

import simplejson as json
import os
import csv
import codecs
import cStringIO
import re
import random
from string import punctuation

json_file = open(os.path.expanduser('~/gvoice_test_data.json'), 'rb')
json_data = json.load(json_file)

class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

cols = [#'account',
        'startTime',
        'fakePhoneNumber', #'phoneNumber',
        'type',
        #'messageText',
        'messageCharLength',
        'messageWordLength',
        'durationMinutes'
]

r = re.compile(r'[{}]'.format(punctuation))


substitution_table = {}

for msg in json_data:
    if not msg['phoneNumber'] in substitution_table.keys():
        substitution_table[msg['phoneNumber']] = random.randrange(12000000000,19999999999)


### Write out substitution table
csv_file = UnicodeWriter(open(os.path.expanduser('~/gvoice_test_data_obfu_subtable.csv'), 'wb+'), quoting=csv.QUOTE_ALL)

csv_file.writerow(['originalNumber', 'obfuscatedNumber'])

for key, val in substitution_table.iteritems():
    csv_file.writerow([str(key), str(val)])

### Write out obfuscated data
csv_file = UnicodeWriter(open(os.path.expanduser('~/gvoice_test_data_obfu.csv'), 'wb+'), quoting=csv.QUOTE_ALL)

csv_file.writerow(cols)

for msg in json_data:
    # handle nulls
    if not 'durationMinutes' in msg.keys():
        msg['durationMinutes'] = '0'

    # get rows
    row = [
        #msg['account'],
        msg['startTime'],
        str(substitution_table[msg['phoneNumber']]),
        str(msg['type']),
        #msg['messageText'],
        str(len(msg['messageText'])),
        str(len(re.split(r'[^0-9A-Za-z]+', msg['messageText']))),
        msg['durationMinutes']
    ]

    print row
    csv_file.writerow(row)

# Import into your favorite CSV app.