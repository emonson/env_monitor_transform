# Environmental monitors data transform

Base scripts for Python for Duke Libraries environmental data transformation 
in preparation for Tableau visualization.

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
Rows per pages -> 1000
Excel spreadsheet report (on right)
```

## 

---

## notebook_solution

Application using Jupyter notebook.
Structure based on [https://medium.com/namely-labs/creating-business-data-tools-with-jupyter-ee152f5a8f95]()


