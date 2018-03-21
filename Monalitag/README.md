# Environmental monitors data transform

Base scripts for Python for Duke Libraries environmental data transformation in preparation for
Tableau visualization.

## Script customization

*Before you can run the scripts* you'll need to modify one line of text in each of the `.py`
and `.bat` files to specify the path to this directory on your machine.

### monalitag\_transform.bat -- specify path to Python executable

The original `monalitag_tranform.bat` file looks like this:

```
@echo off
C:\Users\emonson\AppData\Local\Continuum\miniconda3\python.exe monalitag_transform.py %*
pause
```

This is the default install location for Miniconda, so all you should need to do is
open this file in a text editor *(something like Notepad++, not a word processor like Word)*
and replace `emonson` with your user name, or the whole path to Python with the proper one
for your install location. Save the file.

### monalitag\_transform.py -- specify path this data/script directory

The original `monalitag_tranform.py` file line 9 looks like this:

```
data_dir = r'C:\Users\emonson\Downloads\env_monitor_transform-master\Monalitag'
```

Open this Python script file in a text editor *(something like Notepad++, not a word processor like MS Word)*.
Navigate in a file explorer window to the `Monalitag` directory, right click in the address bar
at the top, and select `Copy address as text`. Paste the address inside the single quotes
and *leave the lowercase r before the first quote -- it's not a mistake -- it needs to be there!*
Save the file.

## Running the scripts

Put copies of the CSV files downloaded from the Editag online system into this directory, 
double-click on the `monalitag_transform.bat` file, and the python script will 
clean up the data into a common form, concatene all files, and put the results
into a file `monalitag_clean_YYYY-MM-DD.csv`.

### Data placement
NOTE: The scripts are written to load in CSV files with either .CSV or .csv extensions, and not Excel workbooks.

*Don't use these directories as your main data storage area!* Move copies of the CSV files you want to clean and
combine into this folder before running the scripts, and then delete them afterwards. 
The routine will combine any data in the directory, so it's not too hard to end up with millions of rows
if you have too many files of high-density data to begin with.

## Monalitag data download procedure

Get data download on all sensors temp and humidity for a year

```
Monitoring -> Monitored Objects
Uncheck Spare 1, Spare 2
More actions... (on right) -> View history of selected objects...
Uncheck Event
Check Physical Value
Date -> Last year
Add filter -> Property name -> Starts with -> sensor
Fetched rows -> 500000
Hit Filter
Rows per pages -> 1000
Excel spreadsheet report (on right)
```
