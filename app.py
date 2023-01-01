'''
Appends columns with assigned groups for formal swap

        Parameters:
                --url: GSheet URL, e.g d/xyz/edit#gid=0 -> url=xyz

        Returns:
                column with randomly assigned groups
'''

# %%
import pygsheets
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# %%


# Ensure all required environment variables are set
try:  
  os.environ['url']
except KeyError: 
  print('[error]: `url` environment variable required')
  print('url refers to GSheet URL for formal swaps')
  sys.exit(1)



# %%
# Get today's date
today = datetime.today()

# Format the date as a string in the YYYYMMDD format
date_str = today.strftime('%Y%m%d')

# %%
#Path to service account
credentials="./formalswap-570b555259ad.json"
#Authorize service account to read GSheet
gc = pygsheets.authorize(service_file=credentials)

sh = gc.open_by_key(os.environ['url'])

# %%
#Create pandas df from worksheet
worksheet=sh[0]
values = worksheet.get_all_values()
# Create a Pandas dataframe from the list of lists, using the first row as column names
formal_df = pd.DataFrame(values[1:], columns=values[0])


# %%
#remove empty trailing rows and columns; an artifact from pygsheet
formal_df=formal_df.replace('',np.nan)
formal_df=formal_df.dropna(axis=0,how='all')
formal_df=formal_df.dropna(axis=1,how='all')
#Check column names to assure that sheet is in the right format
formal_df_col = ['name','college','number_of_people','availability']
if not(formal_df.columns.isin(formal_df_col).any()):
    raise Exception('Input sheet does not conform to the right format.')


# %%
group_str=f'group_{date_str}'
#Avoid duplicated column names
if group_str in formal_df.columns:
    raise Exception('Groups have already been assigned.')
formal_df=formal_df.assign(**{group_str:None})

# %%
#filter for people available to assign them to groups
available_df = formal_df[formal_df['availability']=='yes']
#drop rows with nans in college information columns
available_df = available_df.dropna(subset=['college', 'number_of_people'], how='any')


# %%
while sum(available_df[group_str].isnull())>0:
    print('start loop')

    #Filter out people who have already been assigned to a group 
    temp_idx=available_df[available_df[group_str].isnull()].index.to_list()
    #Pick random integer
    host_number=np.random.choice(temp_idx)

    #Select hosts and the number of guests the host can bring
    #add group assignment in separate column to indicate the host
    host_name=available_df.loc[host_number,'name']
    available_df.loc[host_number,group_str]=f'hosted by {host_name}'

    #extract number of guests 
    number_of_guests=available_df.loc[host_number,'number_of_people']
    number_of_guests=int(number_of_guests)

    number_of_unassigned_guest=sum(available_df[group_str].isnull())
    print(available_df)
    #Check if number of guests is bigger than remaining number of students 
    if number_of_guests>number_of_unassigned_guest:
       
        #get index from remaining unassigned guest    
        rest_idx=available_df[available_df[group_str].isnull()].index
        available_df.loc[rest_idx,group_str] = f'hosted by {host_name}'
    #extract random number based on the number of guest that person can bring 
    else:

        #exclude host index from random number
        temp_idx_wo_host = [x for x in temp_idx if x != host_number]
        selected = np.random.choice(temp_idx_wo_host, number_of_guests,replace=False)
        print(selected)
        available_df.loc[selected,group_str] = f'hosted by {host_name}'


# %%
formal_df.loc[available_df.index,group_str]=available_df[group_str]


# %%
#Identify starting cell 
column_no=available_df.shape[1]-1
start_cell=f'{chr(97 +column_no).upper()}1'
print(start_cell)


# %%
#Create a list to append as a column for the formed groups
group_vals = []

#append first header and then the rest of the values
group_vals.append(group_str)

group_vals=group_vals+formal_df[group_str].to_list()

# %%
worksheet.append_table(group_vals,start=start_cell,dimension='COLUMNS',overwrite=True)


