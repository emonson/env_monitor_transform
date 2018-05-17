import pandas as pd
import os
import datetime
import glob
import json

# Edit this for desired data directory where all the individual Hobo files are located
# that you want cleaned and concatenated. 
# The output file will be monalitag_clean_YYYY-MM-DD.csv

# config.json file in root directory of the repository should contain the path
# to that directory
opts = json.loads(open("../config.json").read())
data_dir = os.path.join(opts['repo_dir'],'Monalitag')

# Shouldn't have to edit below here...
now = datetime.datetime.now()
out_file = 'monalitag_clean_' + now.strftime("%Y-%m-%d") + '.csv'

# Extensions tend to be in lowercase for Monalitag data, but just in case, checking for both
files_list = glob.glob(os.path.join(data_dir,'*.[Cc][Ss][Vv]'))
# Exclude output files, assuming starting with 'monalitag'
files_list = [f for f in files_list if not os.path.basename(f).startswith('monalitag')]
n_files = len(files_list)

df = pd.DataFrame()

for ii, in_file in enumerate(files_list):
  print(ii+1, ' / ', n_files, ' : ', os.path.basename(in_file))

  df_tmp = pd.read_csv(os.path.join(data_dir,in_file), delimiter=';', encoding='iso-8859-1')

  # Don't need all the columns
  df_tmp = df_tmp.drop(['Acknowledged', 'Recording #', 'Priority', 'Previous value', \
         'Action taken', 'Audited object property name', 'Mission', 'Comments', \
         'Unnamed: 24','Category','State','EndUser','Is active','LogType','objectType'], axis=1)

  # could also do a string split and get(2) element
  df_tmp.Location = df_tmp.Location.str.extract('.+>.+>(.+)', expand=False)

  df_tmp.Message = df_tmp.Message.str.replace("Température \(°\)", "Temp C")
  df_tmp.Message = df_tmp.Message.str.replace("Temperature \(°F\)", "Temp F")
  df_tmp.Message = df_tmp.Message.str.replace("Hygrométrie \(%\)", "RH %")
  df_tmp.Message = df_tmp.Message.str.replace("Hygrometry ratio", "RH %")

  # Any temps in C convert to F and change label
  # T(°F) = T(°C) × 1.8 + 32
  df_tmp.loc[df_tmp.Message.str.match('Temp C'),'Value'] = df_tmp.loc[df_tmp.Message.str.match('Temp C'),'Value']*1.8 + 32
  df_tmp.Message = df_tmp.Message.str.replace("Temp C", "Temp F")

  # Rename columns
  df_tmp = df_tmp.rename(index=str, columns={'Location':'Room', 'Message':'measurement', 'Date':'datetime', 'Value':'value'})
  df_tmp['location'] = df_tmp.Room + ' : ' + df_tmp.Name

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
df[['location','datetime','measurement','value']].to_csv(os.path.join(data_dir,out_file), index=False, encoding='utf-8')
