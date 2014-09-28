#! /usr/bin/env python
"""
Usage:
  jsontocsv.py <input_file>
  jsontocsv.py -h | --help

Description:
  Convert exported IITC bookmarks json to csv so you can add key counts if desired.

  input_file:
      .json file as exported from IITC bookmarks plugin

Options:
  -h --help  Show this screen.
"""

import os
import json
import docopt
import shutil
import StringIO
import unicodecsv

def main():
    args = docopt.docopt(__doc__)
    input_file = args['<input_file>']

    csvform = convert(input_file)

    output_file = os.path.splitext(os.path.basename(input_file))[0]+'.csv'
    file_exists = os.path.exists(output_file)

    response = ''
    if file_exists:
        response = raw_input(output_file + ' already exists. Clobber? (y/N) ')
    if not file_exists or response.lower().startswith('y'):
        with open(output_file, 'w') as outfile:
            shutil.copyfileobj(csvform, outfile)

def convert(input_file):
    outfile = StringIO.StringIO()
    with open(input_file) as infile:
        j = json.load(infile)
        portals = j['portals']['idOthers']['bkmrk'].values()
        dw = unicodecsv.DictWriter(outfile, ['label', 'url', 'keys'], restval='0')
        for portal in portals:
            portal.pop('guid', None) # and guid goes byebye
            portal['url'] = 'https://www.ingress.com/intel?ll={0}&z=19&pll={0}'.format(portal.pop('latlng'))
            dw.writerow(portal)
    outfile.seek(0)
    return outfile

if __name__ == '__main__':
    main()
