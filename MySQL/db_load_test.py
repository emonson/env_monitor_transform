from sqlalchemy import create_engine, exc
import pandas as pd
import sys

engine = create_engine('mysql://tableau:tableau.log@rapid-902.vm.duke.edu:3306/environment')

df = pd.read_csv('../FMD/fmd_clean_2018-03-13.csv',encoding='utf-8')
df = df.drop_duplicates()

print(pd.read_sql_query('SELECT * FROM locations LIMIT 10', engine))

try: 
  df.to_sql('measurements', engine, if_exists='append', index=False)
except exc.IntegrityError as err:
  print("Integrity Error:")
  # Tuple containing all rows (as tuples) in the error
  params = err.params
  # SQL statement that gave the error
  statement = err.statement
  # 1062 is "duplicate entry"
  code, msg = err.orig.args
  print("Code: ", code)
  print("Msg: ", msg)
  print("Row count: ", len(params))
except:
  print("Unexpected error:", sys.exc_info()[0])
else:
  print("Successfully loaded ", len(df), " rows to DB")
  