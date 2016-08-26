import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import requests
import json
from datetime import datetime
#import config
#import utils

RVLIMIT = 'max'

def get_revisions_from_web(json_dump=[]):
    base_url = r'https://en.wikipedia.org/w/api.php'
    params = {
        'action':'query',
        'prop':'revisions',
        'titles':'Talk:Boston Marathon bombing',
        'rvprop':'ids|timestamp|comment|user|sha1|content',
        'rvlimit':RVLIMIT,
        'rvdiffto':'prev',
        'rvdir':'newer',
        'format':'json'
    }
    lastContinue = None
    while True:
        if lastContinue:
            params.update(lastContinue)
        r = requests.get(base_url, params=params).json()
        if 'error' in r:
            print(r['error'])
            return None
        if 'warnings' in r:
            print(r['warnings'])
        if 'query' in r:
            page_id = list(r['query']['pages'].keys())[0]
            json_dump.append({
                'query':r['query']['pages'][page_id],
                ' batch_download_date':str(datetime.utcnow())
            })
            #df = df.append(traverse_query(r['query']['categorymembers']))
            #utils.log('processed {0} bot names'.format(len(df)))
        if 'rvcontinue' not in r:
            return json_dump
        lastContinue = r['rvcontinue']

def create_json_dump_from_web(outfile_path,infile_path=None):
    if not infile_path:
        json_dump = []
    else:
        infile = open(infile_path,'r')
        json_dump = json.load(infile)
        infile.close()
    json_dump = get_revisions_from_web(json_dump)
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
                        help='the title of the wikipedia page to download')
    args = parser.parse_args()
    create_json_dump_from_web(outfile_path=args.outfile,
                              infile_path=args.infile)

if __name__ == "__main__":
    main()
