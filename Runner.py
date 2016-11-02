from time import time
from Scraper import GetCraiglistSites, GetCraiglistData

start = time()
try:
    '''
        Use GetCraiglistSites() To configure/search url /print list of craigslist site urls.
        Continent is optional parameter which can be -
                US = United States
                EU = Europe
                ASIA = Asia
                Oceana = Australia/New Zealand
                LATAM = Latin America
                AF = Africa
        Default continent is "US".
    '''
    site = GetCraiglistSites()

    '''sample usage : print list of all '''
    # site.printsitelist()

    ''' sample usage : to get site url for particular city'''
    # site_url = site.forcity("New York City")

    ''' sample usage : to get recommendation based on partial city name'''
    # site_url = site.getsuggestions("ALB")
    # print(site_url)

    ''' Use GetCraiglistData() to search item on cragslist site. Default site url is set to
        https://newyork.craigslist.org/. This can be changed using seturl() method.
        if no search item specified, scraper will pull all available items for sale.
        *warning* - This may take significant amount of time to process
    '''
    s1 = GetCraiglistData((input("Enter search item : ")))

    ''' Search specific city craglist site using seturl() method.
        seturl() accepts a direct link passed as string as well as
        url returned by forcity() method of GetCraiglistSite() class
    '''
    # Passing direct link as string
    # s1.seturl("https://newyork.craigslist.org/")
    
    #Using forcity() method.
    s1.seturl(site.forcity("new york city"))

    ''' Export and save the result in .csv file. 
        File will be saved as current_path/SearchResutls.csv
    '''
    # s1.saveresults()
    
    '''
        display basic details of search i.e. title,posting url and price
        on output console.
        'limit' is and optional argument that limits number of postings displayed
        on output console. By default, if ignored, it will print all.
        
    '''
    s1.printresults(100)

except ConnectionError:
    print("Error retrieving data from site.")

print("Time elapsed: %f seconds" %(time() - start))
