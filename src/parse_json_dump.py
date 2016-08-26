import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import json
import pandas as pd
from bs4 import BeautifulSoup

def traverse_query(query):
    df = pd.DataFrame()
    page_list = query['pages']
    for page in page_list:
        title = page_list[page]['title']
        page_id = page_list[page]['pageid']
        revision_list = page_list[page]['revisions']
        for rev in revision_list:
            rev_id = rev['revid']
            parent_id = rev['parentid']
            ts = pd.to_datetime(rev['timestamp'],format="%Y-%m-%d %H:%M:%S")
            comment = rev['comment']
            user = rev['user']
            if 'from' in rev['diff']:
                text = parse_revision_xml(rev['diff']['*'])
            else:
                text = rev['*']
            df = df.append(pd.DataFrame([{
                'title':title,
                'page_id':page_id,
                'rev_id':rev_id,
                'parent_rev_id':parent_id,
                'ts':ts,
                'user_comment':comment,
                'user':user,
                'text':text
            }]))
    return df

def parse_revision_xml(xml):
    text = ''
    parsed_xml = BeautifulSoup(xml,'html.parser')
    added_line_list = parsed_xml.select('.diff-addedline')
    for line in added_line_list:
        text = '{0}{1}\n'.format(text,line.text)
    return text

def main():
    description = 'parse a json dump containing the revision history of a wikipage and return a csv of diffs for coding'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i','--infile',
                        nargs='+',
                        help='input json dump file path(s)')
    parser.add_argument('-o','--outfile',
                        help='output csv file path')
    args = parser.parse_args()
    df = pd.DataFrame()
    for infile_path in args.infile_path:
        infile = open(infile_path,'r')
        json_dump = json.load(infile)
        infile.close()
        for query in json_dump:
            df = df.append(traverse_query(query))
    df.to_csv(args.outfile_path,na_rep='NaN',columns=columns,encoding='utf-8')
            
if __name__ == "__main__":
    main()
