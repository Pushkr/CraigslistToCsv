#!/usr/bin/python3
__author__ = "Pushkar Gujar"

import csv
import sys
import requests
from bs4 import BeautifulSoup
from requests.exceptions import ChunkedEncodingError
from urllib.parse import urlparse
from queue import Queue
import threading

class GetCraiglistData:
    """ Use this class to search,save and/or print craiglist data"""

    url = "https://newyork.craigslist.org/"
    s_page = "&s="
    search_url = "search/sss?&query="
    Qurl = Queue()
    pageWorkerQueue = Queue()
    rowWorkerQueue = Queue()
    fetchList_lock = threading.Lock()
    appendList_lock = threading.Lock()
    result_pages = []
    items = []
    targetName = ''

    def __init__(self, search_term):
        """ Enter item to search on craigslist.
            if no item is specified, all available items for sale will be retrieved.
        """
        self.search_term = search_term.replace(' ', '+')
        self.items = []

    @property
    def getterm(self):
        """returns search term """
        return self.search_term

    @property
    def geturl(self):
        """
        :rtype: craiglist site url used for searching
        """
        return self.url

    def seturl(self, url):
        try:
            scode = requests.get(url).status_code
        except:
            scode = 404

        if url != 404 and scode == 200:
            self.url = url
        else:
            print("\nCannot set requested URL, Site response code : %s" % scode)
            print("\nreverting back to default url.. %s" % url)

    def pageFetcher(self,worker):
        temp_url = None
        with self.fetchList_lock:
            if self.Qurl.empty() is False:
                temp_url = self.Qurl.get()

        if temp_url is not None:
            try:
                webdata_full = requests.get(temp_url)
                soup = BeautifulSoup(webdata_full.text, "html.parser")
                result1 = soup.find("div", {"class": "content"})
                temp_rows = result1.find_all("p", {"class": "row"})
            except (ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError) as err:
                print("\nError connecting site : {0} \n".format(err))
                return
            except ChunkedEncodingError:
                print("\nSite response delayed, skipping retrieval..: {0}".format(sys.exc_info()[0]))
            finally:
                with self.appendList_lock:
                    #print(threading.current_thread().name, self.Qurl.qsize(), temp_url)
                    if len(temp_rows) > 0:
                        self.result_pages.append(temp_rows)
        else:
            pass

    def rowFetcher(self, worker):
        row = None
        with self.fetchList_lock:
            if self.Qurl.empty() is False:
                row = self.Qurl.get()

        id_url = row.find("a", {"class": "hdrlnk"})
        lurl = (id_url.get("href"))
        posting = urlparse(lurl)
        if posting.netloc == '':
            post_url = urlparse(self.url).scheme + "://" + urlparse(self.url).netloc + posting.path
        else:
            post_url = urlparse(self.url).scheme + "://" + posting.netloc + posting.path

        title = id_url.text if id_url is not None else "No Title"

        span = row.find("span", {"class": "price"})
        price = (span.text if span is not None else "Not Listed")

        # Retrieve post details
        try:
            post_data = requests.get(post_url)
            post_soup = BeautifulSoup(post_data.text, "html.parser")
            pspan = post_soup.find("span", {"class": "postingtitletext"})
            pbody = post_soup.find("section", {"id": "postingbody"})
        except (ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError) as err:
            print("\nError connecting site : {0} \n".format(err))
            return
        except ChunkedEncodingError:
            print("\nSite response delayed, skipping retrieval..: {0}".format(sys.exc_info()[0]))

        location = "Not Listed"
        try:
            location = pspan.small.text if pspan is not None  else "Not Listed"
        except AttributeError:
            pass

        body_text = pbody.text if pbody is not None else "Not Listed"

        pbody = post_soup.find_all("p", {"class": "postinginfo"})

        post_time, upd_time = ["N/A", "N/A"]
        try:
            if pbody[2].find("time", {"class": "timeago"}) is not None:
                post_time = (pbody[2].find("time", {"class": "timeago"}))['datetime'].split("T")
            if pbody[3].find("time", {"class": "timeago"}) is not None:
                upd_time = (pbody[3].find("time", {"class": "timeago"}))['datetime'].split("T")
        except:
            pass

        with self.appendList_lock:
            self.items.append((title, post_url, price, location, post_time[0], post_time[1][:-5],
                           upd_time[0], upd_time[1][:-5], body_text))

    def pageThreader(self):
        while True:
            worker = self.pageWorkerQueue.get()
            self.pageFetcher(worker)
            self.pageWorkerQueue.task_done()


    def start_pageThreads(self):
        for x in range(4): # Four threads
            t = threading.Thread(target=self.pageThreader)
            t.daemon = True
            t.start()

        for worker in range(self.Qurl.qsize()):
            self.pageWorkerQueue.put(worker)
        self.pageWorkerQueue.join() # block until item in queue is processed

    def rowThreader(self):
        while True:
            worker = self.rowWorkerQueue.get()
            self.rowFetcher(worker)
            self.rowWorkerQueue.task_done()

    def start_rowThreads(self):
        for x in range(4):  # Four threads
            t = threading.Thread(target=self.rowThreader)
            t.daemon = True
            t.start()
        for worker in range(self.Qurl.qsize()):
            self.rowWorkerQueue.put(worker)
        self.rowWorkerQueue.join() # block until item in queue is processed

    def __getTotalresults__(self):
        self.totalCount = 0
        pages = {}
        try:

            # make http request to get search result from craiglist
            webdata = requests.get(self.url + self.search_url + self.search_term)
            # use soup
            soup = BeautifulSoup(webdata.text, "html.parser")
            # find number of search items returned
            pages = soup.find("span", {"class": "button pagenum"})
        except ConnectionError as err:
            print("\nError connecting site : {0}".format(err))
        except:
            print("\n Unexpected error : {0}".format(sys.exc_info()[0]))
            return

        if pages is not None and pages.text != 'no results':
           self.totalCount = int(pages.find("span", {"class": "totalcount"}).text)
        else:
            self.totalCount = 0

    def printresults(self, limit=None):
        """print the search results on output console
        """
        self.__retrievedata__(limit)
        if len(self.items) == 0:
            print("No results")
        elif limit is None:
            for item in self.items:
                print(item[0], "\t", item[1], "\t", item[2])
        elif 0 < limit <= len(self.items):
            for i in range(0, limit):
                print(self.items[i][0], "\t", self.items[i][1], "\t", self.items[i][2])
        elif limit > len(self.items):
            print("Warning : not enough search results. Printing available items.. ")
            for item in self.items:
                print(item[0], "\t", item[1], "\t", item[2])
        sys.exit(1)

    def saveresults(self):
        """ Save the search result in current_path/SearchResults.csv
        """
        self.__retrievedata__()
        if len(self.items) == 0:
            print("\nNo results")
        else:
            try:
                with open('SearchResults.csv', 'wt', encoding="UTF-8") as fobj:
                    cwriter = csv.writer(fobj, dialect='excel')
                    cwriter.writerow(("Title", "Posting URL", "Price", "Location", "Posted on", "Post Time",
                                      "Updated on", "Update time", "Description"))
                    for item in self.items:
                        cwriter.writerow(item)
                print("\nResult saved in SearchResults.csv\nGoodbye.")
            except IOError:
                print("\nError saving data in file : %s" % sys.exc_info()[0])
        #sys.exit(1)

    def __retrievedata__(self,limit=None):
        self.__getTotalresults__()
        if self.totalCount == 0:
            return self.items

        if limit is None:
            print("\nFound %s items" % self.totalCount)
        else:
            print("\nFound {} items, retrieving first {} ".format(self.totalCount,limit))
            self.totalCount = limit

        print("\nFetching data...")

        # Flush queue
        self.Qurl.queue.clear()
        # Fill queue
        for i in range(0, self.totalCount // 100):
            self.Qurl.put((self.url + self.search_url + self.search_term + self.s_page + str(i * 100)))

        #print(self.Qurl.qsize())
        self.start_pageThreads()

        # Flush queue
        self.Qurl.queue.clear()
        # Fill queue
        for aPage in self.result_pages:
            for row in aPage:
                self.Qurl.put(row)
        print(self.Qurl.qsize())
        self.start_rowThreads()
        self.items = list(set(self.items))  # remove the duplicates.
        print("\nRetrieved %d items \n" % (len(self.items)))

        return self.items


class GetCraiglistSites:
    dict_map = {"US": 0, "CA": 1, "EU": 2, "ASIA": 3, "OCEANIA": 4, "LATAM": 5, "AF": 6}
    site_map = {}

    def __init__(self, continent="US"):
        self.continent = continent
        self.url = "https://www.craigslist.org/about/sites#" + self.continent
        self.__fetchPage__()

    def __fetchPage__(self):
        # print(self.url)
        try:
            webdata = requests.get(self.url)
            soup = BeautifulSoup(webdata.text, "html.parser")
            sites = soup.find_all("div", {"class": "colmask"})
            self.ListA = sites[self.dict_map.get(self.continent)]
            self.__extractFromList__()
        except ConnectionError as err:
            print("\nError connecting site : {0} \n".format(err))
            return
        except ChunkedEncodingError:
            print("\n Site data delayed, skipping retrieval.. : {0} \n".format(sys.exc_info()[0]))
        except TypeError:
            print("\n Continent not found.")
            print(" Hint: Use one of these - {0}".format(set(self.dict_map)))
        except:
            print("\n Unknown error : {0} \n".format(sys.exc_info()[0]))

    def __extractFromList__(self):
        anchors = self.ListA.find_all("a")
        for anchor in anchors:
            # print(anchor.text,"https:"+anchor.get("href"))
            self.site_map[anchor.text] = "http:" + anchor.get("href")

    def printsitelist(self):
        print("=" * 20 + " List of available sites " + "=" * 20)

        for keys, values in sorted(self.site_map.items()):
            print(keys, "\t" * 5, values)
        print("=" * 20 + "                         " + "=" * 20)

    def getsuggestions(self, city):
        print("finding recommendations.. ")
        city_found = False
        i = 1
        city = city.lower()
        for keys, values in self.site_map.items():
            if city[:3] == keys[:3]:
                city_found = True
                print("%d . City : %s URL : %s " % (i, keys, values))
                i += 1

        if not city_found:
            print("sorry, no recommendations.")
            return 404

        print('\n ** Tip:use printsitelist() to get full list of cities and sites \n')
        # print(suggestion_list)

    def forcity(self, city):
        city = city.lower()
        try:
            return self.site_map[city]
        except KeyError:
            print("\nsite for city ' %s ' not found or unavailable \n" % city)
            self.getsuggestions(city)
            return 404
