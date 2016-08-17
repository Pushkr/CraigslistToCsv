# CraigslistToCsv
python script to search and export craiglists search data into .csv file.


##Dependency
- Python packages 
  - urllib
  - requests
  - csv
  - BeautifulSoup

## How to use:
To search posting for "Honda 2015" in Albany region 
```
site = GetCraiglistSites()
g_data = GetCraiglistData("Honda 2015")
g_data.seturl(site.forcity("albany"))
g_data.saveresults()
```
Above code will export result in SearchResult.csv file in current path.
To print first 50 results to output console rather than exporting to csv
```
g_data.printresults(50)
```

See more sample usages in runner.py
 


## To-Do
- [ ] Build a GUI
- [ ] Build a stand-alone executable
- [ ] Extract keywords
- [ ] Add additonal configurations methods for searching.

##Notice
This script is developed solely for the purpose of research and education. Any commertial use of this script may violate cragslist's [terms of use](https://www.craigslist.org/about/terms.of.use.en)
