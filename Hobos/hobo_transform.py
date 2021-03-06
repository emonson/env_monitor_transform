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
data_dir = os.path.join(opts['repo_dir'],'Hobos')

# Shouldn't have to edit below here...
now = datetime.datetime.now()
out_name = 'hobo_clean_' + now.strftime("%Y-%m-%d") + '.csv'

# Extensions tend to be in lowercase for Hobo data, but just in case, checking for both
files_list = glob.glob(os.path.join(data_dir,'*.[Cc][Ss][Vv]'))
# Exclude output files, assuming starting with 'hobo'
files_list = [f for f in files_list if not os.path.basename(f).startswith('hobo')]
n_files = len(files_list)

df = pd.DataFrame()

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
  
  df = pd.concat([df, df_tmp], axis=0)

# In case there are some bad data string values in the original spreadsheet.
# to_numeric(errors='coerce') will force them to NaNs
df.value = pd.to_numeric(df.value, errors='coerce')

# Duplicate measurements often downloaded
# NOTE: This will only keep the first instance, so if there are problem duplicates
#   with non-equal measurement values, this will ignore them, whereas df.drop_duplicates()
#   will only drop if really duplicated across all colunns!!
df = df.drop_duplicates(['location','datetime','measurement'])

# Save to file
df[['location','datetime','measurement','value']].to_csv(out_name, index=False, encoding='utf-8')

  