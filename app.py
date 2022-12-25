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

# %%
group_str=f'group_{date_str}'
formal_df=formal_df.assign(**{group_str:None})

# %%
#filter for people available to assign them to groups
available_df=formal_df[formal_df['availability']=='yes']

# %%
while sum(available_df[group_str].isnull())>0:

    #Filter out people who have already been assigned to a group 
    temp_idx=available_df[available_df[group_str].isnull()].index.to_list()
    #Pick random integer
    host_number=np.random.choice(temp_idx)

    #Select hosts and the number of guests the host can bring
    #add group assignment in separate column to indicate the host
    host_name=available_df.iloc[host_number,available_df.columns.get_loc('name')]
    available_df.iloc[host_number,available_df.columns.get_loc(group_str)]=f'hosted by {host_name}'

    #extract number of guests 
    number_of_guests=available_df.iloc[host_number,available_df.columns.get_loc('number_of_people')]
    number_of_guests=int(number_of_guests)

    number_of_unassigned_guest=sum(available_df[group_str].isnull())
    #Check if number of guests is bigger than remaining number of students 
    if number_of_guests>number_of_unassigned_guest:
        #get index from remaining unassigned guest    
        rest_idx=available_df[available_df[group_str].isnull()].index
        available_df.iloc[rest_idx,available_df.columns.get_loc(group_str)] = f'hosted by {host_name}'
    #extract random number based on the number of guest that person can bring 
    else:
        #exclude host index from random number
        temp_idx_wo_host = [x for x in temp_idx if x != host_number]
        selected = np.random.choice(temp_idx_wo_host, number_of_guests,replace=False)
        available_df.iloc[selected,available_df.columns.get_loc(group_str)] = f'hosted by {host_name}'


# %%
formal_df.iloc[available_df.index,available_df.columns.get_loc(group_str)]=available_df[group_str]

# %%
#Identify starting cell 
column_no=formal_df.shape[1]-1
start_cell=f'{chr(97 +column_no).upper()}1'

# %%
#Create a list to append as a column for the formed groups
group_vals = []
#append first header and then the rest of the values
group_vals.append(group_str)
group_vals=group_vals+formal_df[group_str].to_list()

# %%
worksheet.append_table(group_vals,start=start_cell,dimension='COLUMNS',overwrite=True)


