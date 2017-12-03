
# coding: utf-8

# In[68]:

from sklearn.metrics import cohen_kappa_score
import pandas as pd
import numpy as np


# In[94]:

# import coded sheets
coder1_df = pd.read_csv('/srv/cross_platform_uncertainty/coded/Copy of reddit_paris_attacks_vwwmdb26t78v_01-26-17.csv - reddit_paris_attacks_vwwmdb26t78v_01-26-17.csv.csv',
                        header=2,)
coder2_df = pd.read_csv('/srv/cross_platform_uncertainty/coded/tomwi-reddit_paris_attacks_vwwmdb26t78v_01-26-17.csv - reddit_paris_attacks_vwwmdb26t78v_01-26-17.csv.csv',
                       header=2)


# In[97]:

# get subset of rows (0,100)
coder1_df = coder1_df.iloc[range(100)]
coder2_df = coder2_df.iloc[range(100)]


# In[117]:

def to_binary(cell):
    if type(cell) == float:
        return 0
    else:
        return 1

binary_coder1_df = coder1_df.applymap(to_binary)
binary_coder2_df = coder2_df.applymap(to_binary)


# In[118]:

cohen_kappa_score(np.zeros(100,dtype='int64'),binary_coder1_df['yes/no'].values)


# In[119]:

cohen_kappa_score(binary_coder2_df['yes/no'].values,binary_coder1_df['yes/no'].values)


# In[82]:

coded_columns = ['yes/no', 'Event/Editing', 'Simple Pass',
       'Theorizing/ Building', 'Uncertain Space / Conflicting Info',
       'Stalling', 'Doubt or Challenge', 'Emotional Sensemaking', 'Named',
       'Linked', 'Unnamed', 'Implied', 'Impersonal', 'Personal',
       'Approximators', 'Leading Questions', 'Open Question',
       'Question Source', 'Wish/ Dread', 'Statement of Incredulity']


# In[84]:

for column in coded_columns:
    kappa = cohen_kappa_score(binary_coder2_df[column].values,binary_coder1_df[column].values)
    print('{0}: {1}'.format(column,kappa))


# In[126]:

def color_negative_red(val):
    color = 'red' if val != 0 and type(val) != str else 'black'
    return 'color: %s' % color


# In[116]:

agreement = binary_coder1_df.isin(binary_coder2_df)
agreement = agreement[~agreement.apply(lambda x: min(x) == max(x), 1)][coded_columns]
agreement = coder1_df[['text']].merge(agreement,how='inner',right_index=True,left_index=True)
agreement.style.applymap(color_negative_red)


# In[130]:

agreement = binary_coder1_df.add(binary_coder2_df.multiply(-1))
agreement = agreement[~agreement.apply(lambda x: min(x) == max(x), 1)][coded_columns]
agreement = coder1_df[['text','tweet_text']].merge(agreement,how='inner',right_index=True,left_index=True)
agreement.style.applymap(color_negative_red)


# In[131]:

agreement.to_csv('/srv/cross_platform_uncertainty/coded/agreement.csv')


# In[ ]:



