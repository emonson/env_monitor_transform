import pandas as pd
import os
import datetime
import glob

# Edit this for desired data directory where all the individual Hobo files are located
# that you want cleaned and concatenated. 
# The output file will be fmd_clean_YYYY-MM-DD.csv
data_dir = '/Users/emonson/Dropbox/People/WinstonAtkins/env_monitor_transform/PC_batch/FMD'

# Shouldn't have to edit below here...
now = datetime.datetime.now()
out_file = 'fmd_clean_' + now.strftime("%Y-%m-%d") + '.csv'

# Extensions tend to be in all caps for FMD data, but just in case, checking for both
files_list = glob.glob(os.path.join(data_dir,'*.csv'))
files_list.extend(glob.glob(os.path.join(data_dir,'*.CSV')))
# Exclude output files, assuming starting with 'fmd'
files_list = [f for f in files_list if not os.path.basename(f).startswith('fmd')]
n_files = len(files_list)

df = pd.DataFrame()

# Table with human-readable location names – "Name:Suffix" to "Rubenstein Location"
df_ref = pd.read_csv(os.path.join(data_dir,'RL_SensorsKey.txt'), sep=',', na_values=['NA'])

for ii, in_file in enumerate(files_list):
  print(ii+1, ' / ', n_files, ' : ', os.path.basename(in_file))

  first_table_end = 0
  main_table_start = 0

  # Need to find the bounds of the lookup and main tables
  with open(os.path.join(data_dir,in_file), 'r') as file:
      for ii,line in enumerate(file):
          if line.startswith('"Time Interval:"'):
              first_table_end = ii
          if line.startswith('"<>Date"'):
              main_table_start = ii
              break

  # Location lookup table doesn't have any well-formatted headers, and row numbers are 0-based
  df_loc = pd.read_csv(os.path.join(data_dir,in_file), sep=',', header=None, skiprows=1, nrows=first_table_end-1)
  df_loc.columns = ['Key','Name:Suffix','Junk','TimeIncrement']
  # Column headers won't have a colon at the end, so I prefer to remove them here
  df_loc.Key = df_loc.Key.str.replace(':','')

  # Main data table
  # Column names for real data are Point_0, Point_1, ... (without colons at the end)
  #   and need to be translated into real locations, plus measurement
  # Last line that looks like data is garbage, but it's easier to remove it later
  #   since you can't use the C-based reader with skipfooter
  df_tmp = pd.read_csv(os.path.join(data_dir,in_file), sep=',', header=main_table_start, na_values=['No Data'])
  df_tmp = df_tmp.rename(index=str, columns={'<>Date':'Date'})
  df_tmp = df_tmp[~df_tmp.Date.str.contains('\*\*\*')]

  # Pivot real data before translating column names into locations so can use a JOIN
  df_tmp = pd.melt(df_tmp, id_vars=["Date","Time"], var_name="Key", value_name="Value")

  # Tableau had some trouble with Union when some Nulls existed in the Value column...
  df_tmp = df_tmp.dropna(axis=0, subset=['Value'])

  # Turn Point_* names into location obscure names
  df_tmp = pd.merge(df_tmp, df_loc, left_on='Key', right_on='Key')
  df_tmp = df_tmp[['Date','Time','Value','Name:Suffix']]

  # Now join with human-readable location names and measurements
  df_tmp = pd.merge(df_tmp, df_ref, left_on='Name:Suffix', right_on='Name:Suffix')

  # Combine separate date and time columns into proper datetime object
  df_tmp['DateTime'] = pd.to_datetime(df_tmp.Date + " " + df_tmp.Time, format='%m/%d/%Y %H:%M:%S')

  df = pd.concat([df, df_tmp], axis=0)

# Duplicate measurements often downloaded
df = df.drop_duplicates()

# Save to file
df[['Location','DateTime','Measurement','Value']].to_csv(os.path.join(data_dir,out_file), index=False, encoding='utf-8')
