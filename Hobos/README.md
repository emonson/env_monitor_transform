# Environmental monitors data transform

Base scripts for Python for Duke Libraries environmental data transformation in preparation for 
Tableau visualization.

Put copies of the CSV files downloaded from the Hobo units into this directory, 
double-click on the `hobo_transform.bat` file, and 
the python script will run, cleaning up the data into a common form and putting it into a file
`hobo_clean_YYYY-MM-DD.csv`.

### Data placement

NOTE: The scripts are written to load in CSV files with either .CSV or .csv extensions, and not Excel workbooks.

*Don't use these directories as your main data storage area!* Move copies of the CSV files you want to clean and
combine into this folder before running the scripts, and then delete them afterwards. 
The routine will combine any data in the directory, so it's not too hard to end up with millions of rows
if you have too many files of high-density data to begin with.

