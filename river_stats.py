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
#import dateparser

####
####  Date formats used
#
#   | 2007 | 04-Jan-07  |
#   | 2007 | 05-Jan-07  |
#   |------+------------|
#   | 2008 | 2008-01-01 |
#   | 2012 | 2012-01-03 |
#   |------+------------|
#   | 2013 | 1/1/2013   |
#   | 2018 | 1/2/2018   |

def parsedate(raw):
    try:
        if raw[2] == '-':
            dformat = '%d-%b-%y'
            return datetime.strptime(raw,dformat).date()
        elif raw[0:2] == '20':
            dformat = '%Y-%m-%d'
            return datetime.strptime(raw,dformat).date()
        else: # APPRPOX '%d/%m/%Y'
            mm,dd,yyyy = raw.split('/')
            return datetime.date(int(yyyy),int(mm),int(dd))
    except Exception as err:
        #print('Bad parse on <{}>: {}'.format(raw,err))
        return None

        
def collate(csvpath_list):
    """Combine data from multiple CSV files into one."""
    #print('DBG: csvpath_list=',list(csvpath_list))
    columnnames = ['launch','size','apps','chances','won_chances']
    launch_days = defaultdict(lambda : defaultdict(int)) # ld[(m,d)] = dict[year] = num_apps
    permits = defaultdict(int) # permits[date]=N; number of permits available
    years = set()

    for csvpath in csvpath_list:
        print('READING {}'.format(str(csvpath)))
        with open(csvpath, newline='') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=columnnames)
            for row in reader:
                parseddate = parsedate(row['launch'])
                #print('DBG parseddate=',parseddate)
                if parseddate is None:
                    continue
                if row['size'] == 'Small Size':
                    continue
                date = parseddate
                print('DBG: rawDate={}, parsedDate={}'.format(row['launch'],date))
                years.add(date.year)
                permits[date] += 1
                if row['chances'] == 'None':
                    appcnt = 0
                if row['chances'] == '':
                    appcnt = 0
                elif row['chances'] == 'same':
                    # same as previous count
                    appcnt = launch_days[(date.month, date.day)].get(date.year,0)
                elif row['chances'] == 'see above':
                    # same as previous count
                    appcnt = launch_days[(date.month, date.day)].get(date.year,0)
                else:
                    appcnt = int(row['chances'])
                if not (2007 <= date.year <= 2018):
                    print('WARNING: Parsed year={} in {}'.format(date.year, str(csvpath)))
                    continue
                #!if not (2007 <= date.year <= 2014):
                #!    print('WARNING: IGNORING year={} in {}'.format(date.year, str(csvpath)))
                #!    continue
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
                    prob = 1.0 if (0 == launch_days[(m,d)].get(year,0)) else permits[date]/launch_days[(m,d)].get(year,0.0)
                    numapp_list.append(prob)
                    #numapp_list.append(launch_days[(m,d)].get(year,0))
            if not all(v == 0 for v in numapp_list):
                writer.writerow(['{:02d}-{:02d}'.format(m,d)] + numapp_list)
        writer.writerow(['Cnts=Prob'])
    print('Permits(>1)={}'
          .format([(str(date),v) for (date,v) in permits.items() if (v > 1)  ]))
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
    csv_list = [
        #'tabula-2007_Lottery_Statistics.csv',
        #'tabula-2008_Lottery_Statistics.csv',
        #'tabula-2009_Lottery_Statistics.csv',
        #'tabula-2010_Lottery_Statistics.csv',
        #'tabula-2011_Lottery_Statistics.csv',
        #'tabula-2012_Lottery_Statistics.csv',
        #'tabula-2013_Lottery_Statistics.csv',
        #'tabula-2014_Lottery_Statistics.csv',
        'tabula-2015_Lottery_Statistics.csv',
        'tabula-2016_Lottery_Statistics.csv',
        'tabula-2017_Lottery_Statistics.csv',
        'tabula-2018_Lottery_Statistics.csv',
        ]
    path_list = [(Path(datadir).expanduser() / cfile) for cfile in csv_list]
    #collate(Path(datadir).expanduser().glob('tabula-20*_Statistics.csv'))
    collate(path_list)

if __name__ == '__main__':
    main()
