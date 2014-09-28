import json
import pprint
import unicodecsv

with open('stanford.json') as infile, open('stanford.csv', 'w') as outfile:
    j = json.load(infile)
    portals = j['portals']['idOthers']['bkmrk'].values()
    dw = unicodecsv.DictWriter(outfile, ['label', 'url', 'keys'], restval='0')
    for portal in portals:
        portal.pop('guid', None) # and guid goes byebye
        portal['url'] = 'https://www.ingress.com/intel?ll={0}&z=19&pll={0}'.format(portal.pop('latlng'))
        dw.writerow(portal)
