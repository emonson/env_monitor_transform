import pandas as pd
import os

# Edit this for desired data directory and CSV file
# The output file will have _clean added to the original filename
data_dir = '/Users/emonson/Dropbox/People/WinstonAtkins/env_monitor_transform/notebook_solution/Data/DisplayCases'
in_file = '2017-12-12_145508.csv'

# Shouldn't have to edit below here...
fp = os.path.splitext(in_file)
out_file = fp[0] + '_clean' + fp[1]

df = pd.read_csv(os.path.join(data_dir,in_file), delimiter=';', encoding='iso-8859-1')

# Don't need all the columns
df = df.drop(['Acknowledged', 'Recording #', 'Priority', 'Previous value', \
       'Action taken', 'Audited object property name', 'Mission', 'Comments', \
       'Unnamed: 24','Category','State','EndUser','Is active','LogType','objectType'], axis=1)

# could also do a string split and get(2) element
df.Location = df.Location.str.extract('.+>.+>(.+)', expand=False)

df.Message = df.Message.str.replace("Température \(°\)", "Temp, °C")
df.Message = df.Message.str.replace("Temperature \(°F\)", "Temp, °F")
df.Message = df.Message.str.replace("Hygrométrie \(%\)", "RH, %")
df.Message = df.Message.str.replace("Hygrometry ratio", "RH, %")

# Any temps in C convert to F and change label
# T(°F) = T(°C) × 1.8 + 32
df.loc[df.Message.str.match('Temp, °C'),'Value'] = df.loc[df.Message.str.match('Temp, °C'),'Value']*1.8 + 32
df.Message = df.Message.str.replace("Temp, °C", "Temp, °F")

# Rename columns
df = df.rename(index=str, columns={'Location':'Room', 'Name':'Location', 'Message':'Measurement', 'Date':'DateTime'})

# Save to file
df[['Location','DateTime','Measurement','Value']].to_csv(os.path.join(data_dir,out_file), index=False, encoding='utf-8')
