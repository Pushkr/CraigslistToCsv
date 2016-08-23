#!/usr/bin/python3

import csv
import sys
import requests
from bs4 import BeautifulSoup
from requests.exceptions import ChunkedEncodingError
from urllib.parse import urlparse


class GetCraiglistData:
    """ Use this class to search,save and/or print craiglist data"""

    url = "https://newyork.craigslist.org/"
    s_page = "&s="
    search_url = "search/sss?&query="

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
        :return: craiglist site url used for searching
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

    def __getTotalresults__(self):
        # self.rangeFrom = 0
        # self.rangeTo = 0
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
            # self.rangeFrom = int(pages.find("span", {"class": "rangeFrom"}).text)
            # self.rangeTo = int(pages.find("span", {"class": "rangeTo"}).text)
            self.totalCount = int(pages.find("span", {"class": "totalcount"}).text)
        else:
            # self.rangeFrom = 0
            # self.rangeTo = 0
            self.totalCount = 0

    def printresults(self, limit=None):
        """print the search results on output console
        """
        self.__retrievedata__()
        if len(self.items) == 0:
            print("No results")
        elif limit is None:
            for item in self.items:
                print(item[0], "\t", item[1], "\t", item[2])
        elif 0 < limit <= len(self.items):
            for i in range(0, limit + 1):
                print(self.items[i][0], "\t", self.items[i][1], "\t", self.items[i][2])
        elif limit > len(self.items):
            print("Warning : not enough search results. Printing available items.. ")
            for item in self.items:
                print(item[0], "\t", item[1], "\t", item[2])

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

    def __retrievedata__(self):
        self.__getTotalresults__()
        if self.totalCount == 0:
            return self.items

        rows = []
        # del soup, webdata
        print("\nFound %s items" % self.totalCount)
        print("\nFetching data...")
        for i in range(0, self.totalCount // 100 + 2):
            qualifiedurl = (self.url + self.search_url + self.search_term + self.s_page + str(i * 100))
            # print("Fetching data from %s......" % qualifiedurl)
            try:
                webdata_full = requests.get(qualifiedurl)
                # print("web response: ", webdata_full)
                soup = BeautifulSoup(webdata_full.text, "html.parser")
                result1 = soup.find("div", {"class": "content"})
                temp_rows = result1.find_all("p", {"class": "row"})
                # near_areas = (soup.find("li", {"class": "crumb area"})).find_all("option")
            except (ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError) as err:
                print("\nError connecting site : {0} \n".format(err))
                return
            except ChunkedEncodingError:
                print("\nSite response delayed, skipping retrieval..: {0}".format(sys.exc_info()[0]))
            finally:
                if len(temp_rows) > 0:
                    rows.append(temp_rows)

        # # print(near_areas)
        # for area in near_areas:
        #     print(area['value'], area.text)

        for elements in rows:
            for row in elements:
                id_url = row.find("a", {"class": "hdrlnk"})
                lurl = (id_url.get("href"))
                posting = urlparse(lurl)
                if posting.netloc == '':
                    post_url = urlparse(self.url).scheme + "://" + urlparse(self.url).netloc + posting.path
                else:
                    post_url = urlparse(self.url).scheme + "://" + posting.netloc + posting.path

                # print(post_url)

                title = (id_url.find("span", {"id": "titletextonly"})).text

                span = row.find("span", {"class": "price"})
                price = (span.text if span is not None else "Not Listed")

                # Retrieve post details
                try:
                    post_data = requests.get(post_url)
                    post_soup = BeautifulSoup(post_data.text, "html.parser")
                except (ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError) as err:
                    print("\nError connecting site : {0} \n".format(err))
                    return
                except ChunkedEncodingError:
                    print("\nSite response delayed, skipping retrieval..: {0}".format(sys.exc_info()[0]))

                pspan = post_soup.find("span", {"class": "postingtitletext"})
                pbody = post_soup.find("section", {"id": "postingbody"})

                location = pspan.small.text if pspan.small is not None else "Not Listed"

                body_text = pbody.text if pbody is not None else "Not Listed"

                pbody = post_soup.find_all("p", {"class": "postinginfo"})

                if pbody[2].find("time", {"class": "timeago"}) is not None:
                    post_time = (pbody[2].find("time", {"class": "timeago"}))['datetime'].split("T")
                else:
                    post_time = ["N/A", "N/A"]

                if pbody[3].find("time", {"class": "timeago"}) is not None:
                    upd_time = (pbody[3].find("time", {"class": "timeago"}))['datetime'].split("T")
                else:
                    upd_time = ["N/A", "N/A"]

                self.items.append((title, post_url, price, location, post_time[0], post_time[1][:-5],
                                   upd_time[0], upd_time[1][:-5], body_text))

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
        except :
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
        city_found = 0
        i = 1
        city = city.lower()
        for keys, values in self.site_map.items():
            if city[:3] == keys[:3]:
                city_found = 1
                print("%d . City : %s URL : %s " % (i, keys, values))
                i += 1

        if city_found == 0:
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
