import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import json
import pandas as pd
from bs4 import BeautifulSoup
import mwparserfromhell as mw

def traverse_query(query):
    df = pd.DataFrame()
    title = query['title']
    page_id = query['pageid']
    revision_list = query['revisions']
    for rev in revision_list:
        rev_id = rev['revid']
        parent_id = rev['parentid']
        ts = pd.to_datetime(rev['timestamp'],format="%Y-%m-%d %H:%M:%S")
        comment = rev['comment']
        if 'user' in rev:
            user = rev['user']
        else:
            user = ''
        if 'diff' in rev:
            if 'from' in rev['diff']:
                text = parse_revision_xml(rev['diff']['*'])
            else:
                text = rev['*']
            stripped_text = strip_wikicode(text)
        else:
            text = ''
            stripped_text = ''
            
        df = df.append(pd.DataFrame([{
            'title':title,
            'page_id':page_id,
            'rev_id':rev_id,
            'parent_rev_id':parent_id,
            'ts':ts,
            'user_comment':comment,
            'user':user,
            'text':text,
            'stripped_text':stripped_text
        }]))
    return df

def strip_wikicode(text):
    # get all wikicode templates
    template_list = mw.parse(text).filter_templates()
    stripped_text = text
    # if there are templates remove each template from the text string
    if template_list:
        for t in template_list:
            stripped_text = stripped_text.replace(str(t),'')
    # strip all endline characters
    # add a space at the beginning for google sheets compatibility
    stripped_text = ' {0}'.format(stripped_text.strip('\n'))
    return stripped_text

def parse_revision_xml(xml):
    diff_text = ''
    parsed_xml = BeautifulSoup(xml,'html.parser')
    added_line_list = parsed_xml.select('.diff-addedline')
    for line in added_line_list:
        diff_text = '{0}{1}\n'.format(diff_text,line.text)
    return diff_text

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
    for infile_path in args.infile:
        infile = open(infile_path,'r')
        json_dump = json.load(infile)
        infile.close()
        for query in json_dump:
            df = df.append(traverse_query(query['query']))
    df.to_csv(args.outfile,na_rep='NaN',encoding='utf-8')
            
if __name__ == "__main__":
    main()
