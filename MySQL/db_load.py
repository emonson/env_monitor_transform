from sqlalchemy import create_engine, exc
from sqlalchemy.sql import text
import pandas as pd
from numpy import float32, float64
import sys
import json

# config.json file in root directory of the repository should contain the path
# to that directory
opts = json.loads(open("../config.json").read())
url = opts["mysql_server"]
port = opts["mysql_port"]
user = opts["mysql_username"]
pswd = opts["mysql_password"]

engine = create_engine("mysql://"+user+":"+pswd+"@"+url+":"+port+"/environment")

# Keep DateTime as string upon read so don't have the conversion time.
# MySQL takes the string and interprets as datetime just fine.
df = pd.read_csv('../Hobos/hobo_clean_2018-05-17.csv',encoding='utf-8',dtype={"location":"str", "datetime":"str", "measurement":"str", "value":float32})
print("data loaded")
# NOTE: Keeping only first instance if all other keys match
df = df.drop_duplicates(['location','datetime','measurement'])
print("deduplicated")

def execute_sql(statement: str):
  if statement is not None:
    # Create new temporary table
    try:
      rs = con.execute(statement)
      if statement.startswith("INSERT"):
        print(rs.rowcount, " Rows inserted")
    except (exc.OperationalError, exc.ProgrammingError) as err:
      print("Error:")
      # Tuple containing all rows (as tuples) in the error
      params = err.params
      # SQL statement that gave the error
      st = err.statement
      code, msg = err.orig.args
      print("Code: ", code)
      print("Msg: ", msg)
      print("Row count: ", len(params))
    except:
      print("Unexpected error:", sys.exc_info()[0])

    
with engine.connect() as con:

  # Dropping old temp table if exists
  statement = """DROP TABLE IF EXISTS `measure_temp`;"""
  execute_sql(statement)
  print("Successfully dropped old temporary table")

  # Creating a table not using nice ORM methods for now...
  # Create new temporary table
  statement = """CREATE TABLE `measure_temp` (
    `location` varchar(255) NOT NULL,
    `datetime` datetime NOT NULL,
    `measurement` varchar(20) NOT NULL,
    `value` float DEFAULT NULL,
    PRIMARY KEY (`location`,`datetime`,`measurement`) USING BTREE
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
  execute_sql(statement)
  print("Successfully created temporary table")

  # Transfer data to temporary table
  try: 
    print("Transferring data to temporary table...")
    df.to_sql('measure_temp', engine, if_exists='append', index=False)
  except (exc.IntegrityError, exc.DataError) as err:
    print("Error:")
    # Tuple containing all rows (as tuples) in the error
    params = err.params
    # SQL statement that gave the error
    st = err.statement
    # 1062 is "duplicate entry"
    code, msg = err.orig.args
    print("Code: ", code)
    print("Msg: ", msg)
    print("Row count: ", len(params))
  except:
    print("Unexpected error:", sys.exc_info()[0])
  else:
    print("Successfully loaded ", len(df), " rows to DB")
  
  # Transfer data from temp table to real measurements
  # but only new measurements that weren't already there
  print("Transferring new data into measurements table...")
  statement = """INSERT INTO measurements
    SELECT s.location, s.datetime, s.measurement, s.value
    FROM measure_temp s 
       LEFT JOIN measurements d ON (d.location = s.location AND d.datetime = s.datetime AND d.measurement = s.measurement)
    WHERE d.location IS NULL;"""
  execute_sql(statement)
  print("Successfully transferred new data to measurements table")

