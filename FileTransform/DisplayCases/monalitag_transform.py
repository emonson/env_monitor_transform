import pandas as pd

df = pd.read_csv('2017-12-12_145508.csv', delimiter=';', encoding='iso-8859-1')

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
df[['Location','DateTime','Measurement','Value']].to_csv('2017-12-12_145508_clean.csv',index=False,encoding='utf-8')
