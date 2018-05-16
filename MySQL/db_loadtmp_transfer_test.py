from sqlalchemy import create_engine, exc
from sqlalchemy.sql import text
import pandas as pd
from numpy import float32, float64
import sys

engine = create_engine('mysql://tableau:tableau.log@rapid-902.vm.duke.edu:3306/environment')

# Keep DateTime as string upon read so don't have the conversion time.
# MySQL takes the string and interprets as datetime just fine.
df = pd.read_csv('../FMD/fmd_clean_2018-05-16.csv',encoding='utf-8',dtype={"Location":"str", "DateTime":"str", "Measurement":"str", "Value":float32})
# df = pd.read_csv('../Monalitag/monalitag_clean_2018-03-13.csv',encoding='utf-8')
print("data loaded")
df = df.drop_duplicates()
print("deduplicated")

# Creating a table not using nice ORM methods for now...
statement = """DROP TABLE IF EXISTS `measure_temp`;
  CREATE TABLE `measure_temp` (
  `location` varchar(255) NOT NULL,
  `datetime` datetime NOT NULL,
  `measurement` varchar(20) NOT NULL,
  `value` float DEFAULT NULL,
  PRIMARY KEY (`location`,`datetime`,`measurement`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

with engine.connect() as con:
  try:
    rs = con.execute(statement)
  except exc.OperationalError as err:
    print("Operational Error:")
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
    print("Successfully created temporary table")
    
  try: 
    df.to_sql('measure_temp', engine, if_exists='append', index=False)
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
  except exc.DataError as err:
    print("Data Error:")
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
  