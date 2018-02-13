#! /usr/bin/env python
"""<<Python script callable from command line.  Put description here.>>
"""
# Docstrings intended for document generation via pydoc

import sys
import argparse
import logging
import csv
import datetime 
from collections import defaultdict
from pprint import pformat
from pathlib import Path
from itertools import product
import dateparser


def collate(csvpath_list):
    """Combine data from multiple CSV files into one."""
    #print('DBG: csvpath_list=',list(csvpath_list))
    columnnames = ['launch','size','apps','chances','won_chances']
    launch_days = defaultdict(lambda : defaultdict(int)) # ld[(m,d)] = dict[year] = num_apps
    dupe = defaultdict(int) # number of EXTRA permits (over one) available
    dateformats=['%Y-%m-%d', '%d-%b-%y', '%d/%m/%Y']
    years = set()

    for csvpath in csvpath_list:
        print('READING {}'.format(str(csvpath)))
        with open(csvpath, newline='') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=columnnames)
            for row in reader:
                date = dateparser.parse(row['launch'], date_formats=dateformats)
                if date is None:
                    continue
                if row['size'] == 'Small Size':
                    continue
                years.add(date.year)
                if launch_days[(date.month, date.day)].get(date.year,0) > 0:
                    dupe[date] += 1
                if row['apps'] == 'None':
                    appcnt = 0
                elif row['apps'] == 'same':
                    # same as previous count
                    appcnt = launch_days[(date.month, date.day)].get(date.year,0)
                elif row['apps'] == 'see above':
                    # same as previous count
                    appcnt = launch_days[(date.month, date.day)].get(date.year,0)
                else:
                    appcnt = int(row['apps'])
                if not (2007 <= date.year <= 2018):
                    print('WARNING: Parsed year={} in {}'.format(date.year, str(csvfile)))
                    continue
                launch_days[(date.month, date.day)][date.year] += appcnt
                    
    #print('DBG launch_days={}'.format(pformat(launch_days)))
    outcsv = 'collated.csv'
    with open(outcsv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Launch(m-d)'] + sorted(years))
        #for (m,d) in launch_days.keys():
        for (m,d) in product(range(1,13), range(1,32)):
            numapp_list = []
            for year in sorted(years):
                try:
                    date = datetime.date(year,m,d)
                except: # date out of range
                    numapp_list.append(0)
                else:
                    permits = dupe[date]+1
                    numapp_list.append(launch_days[(m,d)].get(year,0)/permits)
            if not all(v == 0 for v in numapp_list):
                writer.writerow(['{:02d}-{:02d}'.format(m,d)] + numapp_list)
        writer.writerow(['Counts are Applications/AvailablePermit'])
    print('dupe=',dupe)
    print('Wrote:',outcsv)




##############################################################################

def main():
    "Parse command line arguments and do the work."
    #print('EXECUTING: %s\n\n' % (' '.join(sys.argv)))
    parser = argparse.ArgumentParser(
        description='My shiny new python program',
        epilog='EXAMPLE: %(prog)s a b"'
        )
    parser.add_argument('--version', action='version', version='1.0.1')
#!    parser.add_argument('infile', type=argparse.FileType('r'),
#!                        help='Input file')
#!    parser.add_argument('outfile', type=argparse.FileType('w'),
#!                        help='Output output')
#!
    parser.add_argument('--loglevel',
                        help='Kind of diagnostic output',
                        choices=['CRTICAL', 'ERROR', 'WARNING',
                                 'INFO', 'DEBUG'],
                        default='WARNING')
    args = parser.parse_args()
    #!args.outfile.close()
    #!args.outfile = args.outfile.name

    #!print 'My args=',args
    #!print 'infile=',args.infile

    log_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(log_level, int):
        parser.error('Invalid log level: %s' % args.loglevel)
    logging.basicConfig(level=log_level,
                        format='%(levelname)s %(message)s',
                        datefmt='%m-%d %H:%M')
    logging.debug('Debug output is enabled in %s !!!', sys.argv[0])

    datadir='~/sandbox/notes/trips/gc-river-data/'
    collate(Path(datadir).expanduser().glob('tabula-20*_Statistics.csv'))

if __name__ == '__main__':
    main()
