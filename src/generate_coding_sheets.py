import pandas as pd
import numpy as np
import argparse

def generate_coding_sheets(df,data_source):
    columns = ['rev_id','ts','text']
    if data_source == 'wikipedia':
        columns.append('stripped_text')
    if data_source == 'reddit':
        columns.append('url_list')
    coding_sheet = df[columns]
    coding_sheet = coding_sheet.sort_values(by='ts',ascending=True)
    return coding_sheet

def main():
    description = 'read a csv of processed wikipedia edits and generate a coding sheet'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i','--infile',
                        required=True,
                        help='input .csv file path')
    parser.add_argument('-o','--outfile',
                        required=True,
                        help='output coding .csv file path')
    parser.add_argument('-n','--num_sheets',
                        type=int,
                        help='number of times to split the output coding sheet')
    parser.add_argument('-s','--data_source',
                        choices=['wikipedia','reddit'],
                        required=True,
                        nargs=1,
                        help='the source of the original dump')
    args = parser.parse_args()
    df = pd.read_csv(args.infile,
                     na_values={'text':''},
                     keep_default_na=False,
                     dtype={'text': object})
    # generate a single coding df
    coding_sheet = generate_coding_sheets(df,data_source=args.data_source[0])
    # split into multiple files if --num_sheets flag is specified
    if args.num_sheets:
        # create list of split sheets
        coding_sheet_list = np.array_split(coding_sheet,args.num_sheets)
        for i,split_sheet in enumerate(coding_sheet_list):
            # append number to end of file path/name
            outfile = '{0}_{1}.csv'.format(args.outfile.replace('.csv',''),i)
            # write file
            split_sheet.to_csv(outfile,na_rep='NaN',encoding='utf-8',index=False)#,quotechar="'")
    else:
        # write file
        coding_sheet.to_csv(args.outfile,na_rep='NaN',encoding='utf-8',index=False)#,quotechar="'")
    
if __name__ == "__main__":
    main()

