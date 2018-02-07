import pandas as pd
import os

# Edit this for desired data directory, input CSV file and output file name
data_dir = '/Users/emonson/Dropbox/People/WinstonAtkins/env_monitor_transform/notebook_solution/Data/FMD'
in_file = '7704 PRESERVATION TRENDS_09-06-17_15-37.CSV'
out_file = 'fmd_09-06-17_15-37_clean.csv'

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
df = pd.read_csv(os.path.join(data_dir,in_file), sep=',', header=main_table_start, na_values=['No Data'])
df = df.rename(index=str, columns={'<>Date':'Date'})
df = df[~df.Date.str.contains('\*\*\*')]

# Table with human-readable location names – "Name:Suffix" to "Rubenstein Location"
df_ref = pd.read_csv('RL_SensorsKey.csv', sep=',', na_values=['NA'])

# Pivot real data before translating column names into locations so can use a JOIN
df = pd.melt(df, id_vars=["Date","Time"], var_name="Key", value_name="Value")

# Tableau had some trouble with Union when some Nulls existed in the Value column...
df = df.dropna(axis=0, subset=['Value'])

# Turn Point_* names into location obscure names
df = pd.merge(df, df_loc, left_on='Key', right_on='Key')
df = df[['Date','Time','Value','Name:Suffix']]

# Now join with human-readable location names and measurements
df = pd.merge(df, df_ref, left_on='Name:Suffix', right_on='Name:Suffix')

# Combine separate date and time columns into proper datetime object
df['DateTime'] = pd.to_datetime(df.Date + " " + df.Time, format='%m/%d/%Y %H:%M:%S')

# Save to file
df[['Location','DateTime','Measurement','Value']].to_csv(os.path.join(data_dir,out_file), index=False, encoding='utf-8')
