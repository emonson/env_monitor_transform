import pandas as pd
import os
import datetime
import glob
import json

# Edit this for desired data directory where all the individual Hobo files are located
# that you want cleaned and concatenated. 
# The output file will be fmd_clean_YYYY-MM-DD.csv

# config.json file in root directory of the repository should contain the path
# to that directory
# NOTE: This relative path may not be safe if the script is run from a different directory
#  but should be fine if initiated by .bat file in this directory...
opts = json.loads(open("../config.json").read())
script_dir = os.path.join(opts['repo_dir'],'FMD')
data_dir = os.path.join(opts['repo_dir'],'FMD','data')

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
out_file = 'fmd_clean_' + now.strftime("%Y-%m-%d") + '.csv'

# Extensions tend to be in all caps for FMD data, but just in case, checking for both
files_list = glob.glob(os.path.join(data_dir,'*.[Cc][Ss][Vv]'))
# Exclude output files, assuming starting with 'fmd'
files_list = [f for f in files_list if not os.path.basename(f).startswith('fmd')]
n_files = len(files_list)

df_list = []

# Table with human-readable location names – "Name:Suffix" to "Rubenstein Location"
df_ref = pd.read_csv(os.path.join(script_dir,'FMD_SensorsKey_rev.csv'), sep=',', na_values=['NA'])

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
  # PBR records have four columns, and LSC has five for some reason
  if len(df_loc.columns) == 5:
    df_loc.columns = ['Key','Name:Suffix','Junk','UnitDescription','TimeIncrement']
  else:
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
  df_tmp = pd.melt(df_tmp, id_vars=["Date","Time"], var_name="Key", value_name="value")

  # Tableau had some trouble with Union when some Nulls existed in the value column...
  df_tmp = df_tmp.dropna(axis=0, subset=['value'])

  # Turn Point_* names into location obscure names
  df_tmp = pd.merge(df_tmp, df_loc, left_on='Key', right_on='Key')
  df_tmp = df_tmp[['Date','Time','value','Name:Suffix']]

  # Now join with human-readable location names and measurements
  df_tmp = pd.merge(df_tmp, df_ref, left_on='Name:Suffix', right_on='Name:Suffix')

  # Combine separate date and time columns into proper datetime object
  df_tmp['datetime'] = pd.to_datetime(df_tmp.Date + " " + df_tmp.Time, format='%m/%d/%Y %H:%M:%S')

  df_list.append(df_tmp)

# Put all of the individuals together
df = pd.concat(df_list, axis=0)

# Don't need any other columns (which may screw up later manipulations, anyway)
df = df[['location','datetime','measurement','value']]

# There are often some bad data string values in the original spreadsheet.
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
# db.env_df_to_mysql(df_wdp, opts)
print(df_wdp)
