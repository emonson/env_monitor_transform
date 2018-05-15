from odo import odo
import datashape as ds
import pandas as pd

data_file = '../Monalitag/monalitag_clean_2018-03-13.csv'
db_table = 'mysql://tableau:tableau.log@rapid-902.vm.duke.edu:3306/environment::locations'

# odo(df, db_table, dshape='var * {Location:string, DateTime:datetime, Measurement:string, Value:float32}')

odo(db_table, 'tst.csv')