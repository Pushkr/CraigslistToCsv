[![Code Climate](https://codeclimate.com/github/Pushkr/CraigslistToCsv/badges/gpa.svg)](https://codeclimate.com/github/Pushkr/CraigslistToCsv)    [![Issue Count](https://codeclimate.com/github/Pushkr/CraigslistToCsv/badges/issue_count.svg)](https://codeclimate.com/github/Pushkr/CraigslistToCsv)
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
from Scraper import GetCraiglistSites, GetCraiglistData

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


##Classes and their methods:

`Class GetCraiglistSites`

Use `GetCraiglistSites` To configure/search url /print list of craigslist site urls.
`continent` is optional parameter which can be set to -
- US = United States
- EU = Europe
- ASIA = Asia
- Oceana = Australia/New Zealand
- LATAM = Latin America
- AF = Africa

*Default continent is*  **US**.

`GetCraiglistSites` has following methods -

- `forcity(<city name>)` - Use this method to find site url for given city name. A string `<city name>` is only acceptable argument. 

- `printsitelist()` - Use this method to print list of all available cities & their site urls for `continent`. This method requires no arguments.

- `getsuggestions(<city name>)` - Use this method to get/print suggestions for a partial city name.This method is called internally when `forcity()` can not find the site url


=================

`Class GetCraiglistData`

Use `GetCraiglistData` to search item on cragslist site. Default site url is set to
*https://newyork.craigslist.org/* This can be changed using `seturl()` method.
Item to search can be passed as string. if no search item specified, scraper will pull all available items for sale.Craiglist server usually responds with only 2500 postings at the max. (**warning** - *This may take significant amount of time to process*)

`GetCraiglistData` has following methods -
- `seturl()` - Use this method instruct scrapper to search craigslist posting in specific city url.`seturl()` accepts a link passed as string as well as url returned by `forcity()` method of `GetCraiglistSite` class

- `printresults()` - Use this method to print the result of search on output console. This method has optional argument of `int`. Method will print first `int` number of results. If not speficied, it will print all result.

- `saveresults()` - Use this method to save the result of search in .csv format. This will save data in **current_path/SearchResults.csv** file.

csv file has following headers - 

`Post Title` `Posting URL` `Price` `Location` `Posted on` `Posted Time` `Updated on` `Updated Time` `Description`

`GetCraiglistSites` properties -
 - `getterm` to retrive search string that was passed to class while creating an object 
 - `geturl` to get the craiglist url that was used while performing search. 



=================

## To-Do
- [ ] Build a GUI
- [ ] Build a stand-alone executable
- [ ] Extract keywords
- [ ] Add additonal configurations methods for searching.
- [x] Add threading to optimize performance.

##Notice
This script is developed solely for the purpose of research and education. Any commertial use of this script may violate cragslist's [terms of use](https://www.craigslist.org/about/terms.of.use.en)
