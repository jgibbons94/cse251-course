"""
------------------------------------------------------------------------------
Course: CSE 251 
Lesson Week: 02
File: assignment.py 
Author: Brother Comeau

Purpose: Retrieve Star Wars details from a website

Instructions:

- each API call must only retrieve one piece of information
- You are not allowed to use any other modules/packages except for the ones used
  in this assignment.
- The only "fixed" or hard coded URL that you can use is TOP_API_URL.  Use this
  URL to retrieve other URLs that you can use to retrieve information form the
  website.
- You are limited to about 10,000 calls to the swapi website.  That sounds like
  a lot, but you can reach this limit. If you leave this assignment to the last
  day it's due, you might be locked out of the website and you will have to
  submit what you have at that point.  There are no extensions because you
  reached this server limit. Work ahead and spread working on the assignment
  over multiple days.
- You need to match the output outlined in the dcription of the assignment.
  Note that the names are sorted.
- You are requied to use a threaded class (inherited from threading.Thread) for
  this assignment.  This object will make the API calls to the swapi server. You
  can define your class within this Python file (ie., no need to have a seperate
  file for the class)
- Do not add any global variables except for the ones included in this program.

The call to TOP_API_URL will return the following Dictionary.  Do NOT have this
dictionary hard coded - use the API call to get this dictionary.  Then you can
use this dictionary to make other API calls for data.

{
   "people": "http://swapi.dev/api/people/", 
   "planets": "http://swapi.dev/api/planets/", 
   "films": "http://swapi.dev/api/films/",
   "species": "http://swapi.dev/api/species/", 
   "vehicles": "http://swapi.dev/api/vehicles/", 
   "starships": "http://swapi.dev/api/starships/"
}

------------------------------------------------------------------------------
This program does the following:
    1. In a separate thread, fetch the top level url.
    2. In a separate thread, fetch the url for the films given by the top level url.
    3. Get each url of each category of data in
    ['characters','planets','starships','vehicles','species'] in the returned results
    for episode 3 (the third star wars film). Use a separate thread for each url.
    4. Sort and output the results.
I made this assignment my own by having it output a message from Vader at the end.

"""

from datetime import datetime, timedelta
import requests
import json
import threading

# Include cse 251 common Python files
import os, sys
sys.path.append('../../code')
from cse251 import *

# Const Values
TOP_API_URL = 'https://swapi.dev/api'

# Global Variables
call_count = 0

# DONE Add your threaded class definition here
class URL_Fetcher(threading.Thread):
    def __init__(self, url, dct = {'data':[]}, key = "data"):
        threading.Thread.__init__(self)
        self.url = url
        self.error = False
        self.data = None
        self.dct = dct
        self.key = key

    def run(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            self.data = response.json()
            if "name" in self.data:
                self.dct[self.key].append(self.data['name'])
        else:
            self.error = True

    def join(self):
        global call_count
        call_count += 1
        threading.Thread.join(self)

# DONE Add any functions you need here
def fetch_single_json(url):
    thread = URL_Fetcher(url)
    thread.start()
    thread.join()
    return thread.data

def format_list(name, lst, log):
    lst.sort()
    log.write(f'{name}: {len(lst)}')
    log.write(f'{"".join([x + ",  " for x in lst])}')

def main():
    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from swapi.dev')

    # DONE Retrieve Top API urls

    films_url = fetch_single_json(TOP_API_URL)['films']
    films_data =  fetch_single_json(films_url)['results']

    # DONE Retireve Details on film 6
    film6_data = [x for x in films_data if x['episode_id'] == 3][0]
    film6dict = {'title':film6_data['title'],
                'director':film6_data['director'],
                'producer':film6_data['producer'],
                'released':film6_data['release_date'],
                'characters':[],
                'planets':[],
                'starships':[],
                'vehicles':[],
                'species':[],
                }
    categories = ['characters','planets','starships','vehicles','species']
    threads = [URL_Fetcher(url, film6dict, category) for category in categories for url in film6_data[category]]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # DONE Display results

    for category in ['title', 'director', 'producer', 'released']:
              log.write(f'{category}:{film6dict[category]}')
    for category in categories:
              format_list(category, film6dict[category], log)
    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to swapi server')
    log.write("""
 _________________
< Isn't this fun? >
 -----------------
        \\    ,-^-.
         \\   !oYo!
          \\ /./=\\.\\______
               ##        )\\/\\
                ||-----w||
                ||      ||

               Cowth Vader""")

if __name__ == "__main__":
    main()
