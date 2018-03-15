# Environmental monitors data transform

Base scripts for Python for Duke Libraries environmental data transformation 
in preparation for Tableau visualization.

## Installation

### These scripts

If you've never used Git before, and don't have it installed on your machine, the easiest method for now
will be to just go to the green "Clone or download" button on this page, click it, and choose "Download ZIP"
on the lower right. Unzip that package into the place you'll want to run the routines. 

Before you can actuall run them, though, you need to have Python installed.

### Python: Miniconda

The Python requirements for these environmental sensor data transform routines
are pretty minimal, so it's not really necessary to install the entire
[Anaconda Python distribution](https://www.anaconda.com/download/) 
(which is what I recommend for most applications).
Instead, you can install something called Miniconda and then use the conda command-line
utility to install any necessary Python modules -- in this case, the [Pandas](https://pandas.pydata.org/)
high-performance structured data maniuplation module. 

Start by [downloading the appropriate Miniconda installer](https://conda.io/miniconda.html) for Python 3
(as opposed to Python 2). This will most likely be a 64-bit version, as most operating systems now are 64-bit.
You can choose to install Miniconda for just you, or for any users on your system. If you just install it
for you, you won't even need admin privileges. 

After that, all you should need for these scripts that isn't included with Python itself is Pandas.
So, in the Anaconda Prompt (somewhere under yor start menu on Windows), type:

```
conda install pandas
```

## Data Transformations

The three types of data that can be transformed by these routines should be placed in their respective
folders / directories and all you should need to do is double-click the associated .bat file to run the script
and produce a cleaned, concatenated single CSV file for visualizing. The final format of all three types of
data should be identical, so you can combine them for exploration and analysis.

Note that the output file name will be the original data type plus the current date, so if you run the scripts
again on the same day it will just overwrite the CSV file.

### Data placement

NOTE: The scripts are written to load in CSV files with either .CSV or .csv extensions, and not Excel workbooks.
There are additional details about each data type in the respective folders.

*Don't use these directories as your main data storage area!* Move copies of the CSV files you want to clean and
combine into these folders before running the scripts, and then delete them afterwards. 
The routines will combine any data in the directory, so it's not too hard to end up with millions of rows
if you have too many files of high-density data to begin with.

