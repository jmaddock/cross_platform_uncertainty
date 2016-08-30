import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import requests
import json
from datetime import datetime
#import config
#import utils

# set RVLIMIT to 1 to get all diffs
RVLIMIT = '1'

def get_revisions_from_web(title,json_dump=[]):
    # set initial params for API query
    rvlimit = RVLIMIT
    base_url = r'https://en.wikipedia.org/w/api.php'
    params = {
        'action':'query',
        'prop':'revisions',
        'titles':title,
        'rvprop':'ids|timestamp|comment|user|sha1|content',
        'rvlimit':rvlimit,
        'rvdiffto':'next',
        'rvdir':'newer',
        'format':'json'
    }
    # if not passed a json dump, start with the oldest edit
    # else start with the last edit in the json dump
    if len(json_dump) == 0:
        next_rev = None
    else:
        next_rev = json_dump[-1]['revisions'][0]['diff']['to']
    download_count = 0
    while True:
        # try/except keyboardinterrupt to dump all collected data
        try:
            # updated the starting revision ID for the query
            if next_rev:
                params.update({
                    'rvstartid':next_rev,
                    'rvlimit':rvlimit
                })
            # make API request
            r = requests.get(base_url, params=params).json()
            # handle server errors and return collected data
            if 'error' in r:
                print(r['error'])
                return json_dump
            # handle server warnings and continue
            if 'warnings' in r:
                print(r['warnings'])
            # get the query result
            if 'query' in r:
                page_id = list(r['query']['pages'].keys())[0]
                # append the query result to the output json dump with the download date
                json_dump.append({
                    'query':r['query']['pages'][page_id],
                    'batch_download_date':str(datetime.utcnow())
                })
                # try to update the next revision ID
                # if query does not have a next ID, increase query limit by 1
                try:
                    next_rev = r['query']['pages'][page_id]['revisions'][-1]['diff']['to']
                    rvlimit = 1
                except KeyError as e:
                    print(e)
                    print(r['query'])
                    rvlimit += 1
                download_count += 1
            # log number of queries performed to stdout
            if download_count % 100 == 0:
                print('downloaded {0} revisions'.format(download_count))
            # if no more revision, return output json dump
            if 'next_rev' == 0:
                print('query_complete')
                return json_dump
        # handle keyboardinterrupt exception, return collected data
        except KeyboardInterrupt as e:
            print(e)
            return json_dump

def create_json_dump_from_web(outfile_path,title,infile_path=None):
    if not infile_path:
        json_dump = []
    else:
        infile = open(infile_path,'r')
        json_dump = json.load(infile)
        infile.close()
    json_dump = get_revisions_from_web(title=title,json_dump=json_dump)
    outfile = open(outfile_path,'w')
    json.dump(json_dump,outfile)

def main():
    description = 'Collect the revision history of a Wikipedia page and output a json file.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i','--infile',
                        help='input json dump if appending to an existing dump')
    parser.add_argument('-o','--outfile',
                        help='output json dump file path')
    parser.add_argument('-t','--title',
                        default='Talk:November 2015 Paris attacks',
                        help='the title of the wikipedia page to download')
    args = parser.parse_args()
    create_json_dump_from_web(outfile_path=args.outfile,
                              title=args.title,
                              infile_path=args.infile)

if __name__ == "__main__":
    main()
