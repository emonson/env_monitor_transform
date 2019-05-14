import pandas as pd
import datetime
import glob
import os
import re
import datetime
import json

# Edit this for desired data directory where all the individual Hobo files are located
# that you want cleaned and concatenated. 
# The output file will be hobo_clean_YYYY-MM-DD.csv

# config.json file in root directory of the repository should contain the path
# to that directory
opts = json.loads(open("../config.json").read())
data_dir = os.path.join(opts['repo_dir'],'Hobos','data')

# Load function for exporting data from DataFrame to MySQL DB
#   (Not sure what the "name" part is for in spec_from_file_location()... putting "name" for now...)
# This allows me to use db.env_df_to_mysql() later
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("name", os.path.join(opts['repo_dir'],'MySQL/db_load_function.py'))
db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(db)


# Shouldn't have to edit below here...
now = datetime.datetime.now()
out_name = 'hobo_clean_' + now.strftime("%Y-%m-%d") + '.csv'

# Extensions tend to be in lowercase for Hobo data, but just in case, checking for both
files_list = glob.glob(os.path.join(data_dir,'*.[Cc][Ss][Vv]'))
# Exclude output files, assuming starting with 'hobo'
files_list = [f for f in files_list if not os.path.basename(f).startswith('hobo')]
n_files = len(files_list)

df_list = []

for ii, in_file in enumerate(files_list):
  print(ii+1, ' / ', n_files, ' : ', os.path.basename(in_file))
  location = 'default'
  
  # This will work for CSV files
#   with open(file,'r') as f:
#     firstline = f.readline().strip()
#     # first line should be of form "Plot title: Center table", and we want "Center table"
#     location = firstline.split(': ')[1]
  
  # Can't figure out another way to get first element but to read the Excel file twice...
#   df_first = pd.read_excel(file, header=None, usecols=[0])
#   firstline = df_first.loc[0,0]
#   location = firstline.split(': ')[1]
  
  # NOTE: Should probably just pull the location name from the filename...!!
  aa = re.match(r'(.+) \d\d\d\d-\d\d-\d\d \d\d_\d\d_\d\d -\d\d00\.csv', os.path.basename(in_file))
  if aa is not None:
    location = aa.groups()[0]
  
  # EXCEL VERSION
#   df_tmp = pd.read_excel(file, header=1)
#   # For now drop dewpoint since it can be calculated from the other two
#   df_tmp = df_tmp.drop(['#', 'DewPt, °F'], axis=1)
#   # Find date time column, but name can change depending on daylight savings time
#   datecol = [l.startswith('Date Time') for l in df_tmp.columns].index(True)
#   df_tmp = df_tmp.rename(columns={df_tmp.columns[datecol]:"DateTime"})

  # CSV VERSION
  # "Date Time, GMT -0400","Temp, (*F)","RH, (%)","DewPt, (*F)","Host Connect","EOF"
  # Note: Not sure why it's not header=2, since there seem to be two lines before header...
  df_tmp = pd.read_csv(os.path.join(data_dir,in_file), sep=',', header=1, na_values=[' '])

  # Find date time column, but name can change depending on daylight savings time
  datecol = [l.startswith('Date Time') for l in df_tmp.columns].index(True)
  df_tmp = df_tmp.rename(columns={df_tmp.columns[datecol]:"datetime", "Temp, (*F)":"Temp F", "RH, (%)":"RH %"})

  # For now drop dewpoint since it can be calculated from the other two...
  df_tmp = df_tmp[["datetime", "Temp F", "RH %"]]
    
  # Pivot measurements from columns into rows
  df_tmp = pd.melt(df_tmp, id_vars=["datetime"], var_name="measurement", value_name="value")
  
  # Tableau had some trouble with Union when some Nulls existed in the value column...
  df_tmp = df_tmp.dropna(axis=0, subset=['value'])
  
  # RL Stacks rooms have a comma in the filename, but our locations DB doesn't
  df_tmp['location'] = location.replace(',','')
  
  df_list.append(df_tmp)

# Put all of the individuals together
df = pd.concat(df_list, axis=0)

# Don't need any other columns (which may screw up later manipulations, anyway)
df = df[['location','datetime','measurement','value']]

# In case there are some bad data string values in the original spreadsheet.
# to_numeric(errors='coerce') will force them to NaNs
df.value = pd.to_numeric(df.value, errors='coerce')

# Duplicate measurements often downloaded
# NOTE: This will only keep the first instance, so if there are problem duplicates
#   with non-equal measurement values, this will ignore them, whereas df.drop_duplicates()
#   will only drop if really duplicated across all colunns!!
df = df.drop_duplicates(['location','datetime','measurement'])


# Import dew point formula function
spec = importlib.util.spec_from_file_location("name", os.path.join(opts['repo_dir'],'Tdf/Tdf.py'))
dewpoint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dewpoint)

# Need to pivot so Temp and RH are in their own columns
# .reset_index() puts hierarchical index from pivot table back as real columns
df_pivot = pd.pivot_table(df, values='value', index=['location','datetime'], columns=['measurement']).reset_index()

# Calculate dew point from Temp and RH (vectorized with numpy arrays)
df_pivot['DewPt F'] = dewpoint.tdf_np(df_pivot['Temp F'].values, df_pivot['RH %'].values)

# Melt back into tidy data, dropping NAs
df_wdp = pd.melt(df_pivot, id_vars=['location','datetime'], var_name='measurement', value_name='value')
df_wdp = df_wdp.dropna(axis=0, subset=['value'])

# Save to MySQL DB
db.env_df_to_mysql(df_wdp, opts)
# print(df_wdp.location.value_counts())
# print(df_wdp.groupby(["location","measurement"]).size().reset_index(name='count'))
  