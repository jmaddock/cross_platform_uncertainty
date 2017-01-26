import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import json
import pandas as pd
from bs4 import BeautifulSoup
import mwparserfromhell as mw
import abc
import twitter_url_expander

## WIKIPEDIA SPECIFIC METHODS
def traverse_wiki_query(query):
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
        if 'diff' in rev and '*' in rev['diff']:
            text = parse_revision_xml(rev['diff']['*'])
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

## strip all wikicode templates from a wikipedia edit
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

## find diff xml tags from wikipedia dump
## return the diff between 2 edits
def parse_revision_xml(xml):
    diff_text = ''
    parsed_xml = BeautifulSoup(xml,'html.parser')
    added_line_list = parsed_xml.select('.diff-addedline')
    for line in added_line_list:
        diff_text = '{0}{1}\n'.format(diff_text,line.text)
    return diff_text

## REDDIT SPECIFIC METHODS
def traverse_reddit_query(query,title):
    df = pd.DataFrame()
    title = title
    page_id = title
    rev_id = query['data']['id']
    try:
        ts = pd.to_datetime(query['data']['created_utc'],unit='s')
    except:
        print(query)
        sys.exit(0)
    user = query['data']['author']
    text = query['data']['body']
    url_list = []
    tweet_text = []
    if len(query['data']['embeds']) > 0:
        for embed in query['data']['embeds']:
            if embed['url']:
                if 'twitter.com' in embed['url']:
                    try:
                        tweet_text.append(twitter_url_expander.expand_url(embed['url']))
                    except:
                        print('twitter url expander failed: {0}'.format(embec['url']))
                url_list.append(embed['url'])
    df = df.append(pd.DataFrame([{
        'title':title,
        'page_id':page_id,
        'rev_id':rev_id,
        'ts':ts,
        'user':user,
        'text':text,
        'url_list':url_list,
        'tweet_text':tweet_text
    }]))
    return df

## load a single wikipedia or reddit dump from a .json file
def load_from_json(infile_path):
    try:
        infile = open(infile_path,'r')
        json_dump = json.load(infile)
    except json.decoder.JSONDecodeError:
        infile.close()
        infile = open(infile_path,'r')
        json_dump = []
        for line in infile:
            json_line = json.loads(line)
            json_dump.append(json_line)
    infile.close()
    return json_dump

def main():
    description = 'parse a json dump containing the revision history of a wikipage and return a csv of diffs for coding'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i','--infile',
                        nargs='+',
                        help='input json dump file path(s)')
    parser.add_argument('-o','--outfile',
                        help='output csv file path')
    parser.add_argument('-s','--data_source',
                        choices=['wikipedia','reddit'],
                        required=True,
                        nargs=1,
                        help='the source of the .json dump')
    args = parser.parse_args()
    df = pd.DataFrame()
    for infile_path in args.infile:
        json_dump = load_from_json(infile_path)
        for query in json_dump:
            if args.data_source[0] == 'wikipedia':
                df = df.append(traverse_wiki_query(query['query']))
            else:
                title=os.path.basename(infile_path).replace('.json','')
                df = df.append(traverse_reddit_query(query,title=title))
    df.to_csv(args.outfile,na_rep='NaN',encoding='utf-8')
            
if __name__ == "__main__":
    main()
