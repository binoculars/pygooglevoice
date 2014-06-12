__author__ = 'Barrett K. Harber'

# Import local libraries
from googlevoice import Voice
import googlevoice.settings

# Import standard libraries
from urllib2 import urlopen
from urllib import urlencode
import simplejson as json
from lxml import etree
import re
import math
import os

# Regex pattern to match digits
regexDigits = re.compile('^\d+')

# Enrich the JSON if needed
def getEnrichedJSON(response, account):
    xml_tree = etree.fromstring(response)

    json_data = json.loads(xml_tree.xpath('/response/json')[0].text)
    html_tree = etree.HTML(xml_tree.xpath('/response/html')[0].text)

    msgs = []
    for (id, msg) in json_data['messages'].items():
        msg['account'] = account
        call_duration = html_tree.xpath("//div[@id='" + id + "']//span[@class='gc-message-call-details']")
        if len(call_duration) > 0:
            durationText = call_duration[0].text
            msg['callDetails'] = durationText
            m = regexDigits.match(durationText)
            if m:
                msg['durationMinutes'] = m.group()
        msgs.append(msg)
    return msgs

# Log in to Google
voice = Voice()
print("Logging in")
voice.login()

url = googlevoice.settings.XML_ALL # History URL endpoint
print('Getting ' + url)
res = urlopen(url).read() # Read data from endpoint
xml_tree = etree.fromstring(res) # Parse xml tree
json_data = json.loads(xml_tree.xpath('/response/json')[0].text) # Parse out JSON
total_size = int(json_data['totalSize']) # Get the total count of messages
results_per_page = int(json_data['resultsPerPage']) # Get amount of results per page (typically 10)
pages = int(math.floor(total_size / results_per_page)) + (1 if total_size % results_per_page > 0 else 0) # Calculate number of pages
print "Total pages: %s" % pages
messages = getEnrichedJSON(res, voice.email) # Get messages from response

# Iterate through and get all of the messages for each page
for page in range(2, pages + 1):
    params = urlencode({'page' : 'p%s' % page})
    url = googlevoice.settings.XML_ALL + '?' + params
    print("Getting " + url)
    res = urlopen(url).read()
    messages += getEnrichedJSON(res, voice.email)

# Write out the data to a JSON file
with open(os.path.expanduser('~/gvoice_test_data.json'), 'wb+') as outfile:
    json.dump(messages, outfile)

