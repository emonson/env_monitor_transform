import pandas as pd
import glob
import os
import re

in_directory = '.'
out_name = 'hobo_clean.csv'

files_list = glob.glob(os.path.join(in_directory,'*.csv'))
# Exclude output files, assuming starting with 'hobo'
files_list = [f for f in files_list if not os.path.basename(f).startswith('hobo')]

df = pd.DataFrame()

for file in files_list:
  print(file)
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
  aa = re.match(r'(.+) \d\d\d\d-\d\d-\d\d \d\d_\d\d_\d\d -\d\d00\.csv', os.path.basename(file))
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
  df_tmp = pd.read_csv(file, sep=',', header=1, na_values=[' '])

  # Find date time column, but name can change depending on daylight savings time
  datecol = [l.startswith('Date Time') for l in df_tmp.columns].index(True)
  df_tmp = df_tmp.rename(columns={df_tmp.columns[datecol]:"DateTime", "Temp, (*F)":"Temp, °F", "RH, (%)":"RH, %"})

  # For now drop dewpoint since it can be calculated from the other two, plus others...
  df_tmp = df_tmp[["DateTime", "Temp, °F", "RH, %"]]
    
  # Pivot measurements from columns into rows
  df_tmp = pd.melt(df_tmp, id_vars=["DateTime"], var_name="Measurement", value_name="Value")
  
  # Tableau had some trouble with Union when some Nulls existed in the Value column...
  df_tmp = df_tmp.dropna(axis=0, subset=['Value'])
  
  df_tmp['Location'] = location
  
  df = pd.concat([df, df_tmp], axis=0)

# Duplicate measurements often downloaded
df = df.drop_duplicates()

# Save to file
df[['Location','DateTime','Measurement','Value']].to_csv(out_name, index=False, encoding='utf-8')

  