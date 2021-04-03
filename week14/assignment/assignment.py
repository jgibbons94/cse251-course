"""
Course: CSE 251
Lesson Week: 14
File: assignment.py
Author: Jesse Gibbons
Purpose: Assignment 13 - Family Search

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Describe how to sped up part 1

<Add your comments here>


Describe how to sped up part 2

<Add your comments here>


10% Bonus to speed up part 2

<Add your comments here>

"""
import time
import threading
import multiprocessing as mp
from multiprocessing.pool import ThreadPool
import json
import random
import requests

# Include cse 251 common Python files - Dont change
import os, sys
sys.path.append('../../code')
from cse251 import *


TOP_API_URL = 'http://127.0.0.1:8123'


# ----------------------------------------------------------------------------
class Person:
    def __init__(self, data):
        super().__init__()
        self.id = data['id']
        self.name = data['name']
        self.parents = data['parent_id']
        self.family = data['family_id']
        self.birth = data['birth']

    def __str__(self):
        output  = f'id        : {self.id}\n'
        output += f'name      : {self.name}\n'
        output += f'birth     : {self.birth}\n'
        output += f'parent id : {self.parents}\n'
        output += f'family id : {self.family}\n'
        return output

# ----------------------------------------------------------------------------
class Family:

    def __init__(self, id, data):
        super().__init__()
        self.id = data['id']
        self.husband = data['husband_id']
        self.wife = data['wife_id']
        self.children = data['children']

    def children_count(self):
        return len(self.children)

    def __str__(self):
        output  = f'id         : {self.id}\n'
        output += f'husband    : {self.husband}\n'
        output += f'wife       : {self.wife}\n'
        for id in self.children:
            output += f'  Child    : {id}\n'
        return output

# -----------------------------------------------------------------------------
class Tree:

    def __init__(self, start_family_id):
        super().__init__()
        self.people = {}
        self.families = {}
        self.start_family_id = start_family_id

    def add_person(self, person):
        if self.does_person_exist(person.id):
            print(f'ERROR: Person with ID = {person.id} Already exists in the tree')
        else:
            self.people[person.id] = person

    def add_family(self, family):
        if self.does_family_exist(family.id):
            print(f'ERROR: Family with ID = {family.id} Already exists in the tree')
        else:
            self.families[family.id] = family

    def get_person(self, id):
        if id in self.people:
            return self.people[id]
        else:
            return None

    def get_family(self, id):
        if id in self.families:
            return self.families[id]
        else:
            return None

    def get_person_count(self):
        return len(self.people)

    def get_family_count(self):
        return len(self.families)

    def does_person_exist(self, id):
        return id in self.people

    def does_family_exist(self, id):
        return id in self.families

    def display(self, log):
        log.write('Tree Display')
        for family_id in self.families:
            fam = self.families[family_id]

            log.write(f'Family id: {family_id}')

            # Husband
            husband = self.get_person(fam.husband)
            if husband == None:
                log.write(f'  Husband: None')
            else:
                log.write(f'  Husband: {husband.name}, {husband.birth}')

            # wife
            wife = self.get_person(fam.wife)
            if wife == None:
                log.write(f'  Wife: None')
            else:
                log.write(f'  Wife: {wife.name}, {wife.birth}')

            # Parents of Husband
            if husband == None:
                log.write(f'  Husband Parents: None')
            else:
                parent_fam_id = husband.parents
                if parent_fam_id in self.families:
                    parent_fam = self.get_family(parent_fam_id)
                    father = self.get_person(parent_fam.husband)
                    mother = self.get_person(parent_fam.wife)
                    log.write(f'  Husband Parents: {father.name} and {mother.name}')
                else:
                    log.write(f'  Husband Parents: None')

            # Parents of Wife
            if wife == None:
                log.write(f'  Wife Parents: None')
            else:
                parent_fam_id = wife.parents
                if parent_fam_id in self.families:
                    parent_fam = self.get_family(parent_fam_id)
                    father = self.get_person(parent_fam.husband)
                    mother = self.get_person(parent_fam.wife)
                    log.write(f'  Wife Parents: {father.name} and {mother.name}')
                else:
                    log.write(f'  Wife Parents: None')

            # children
            output = []
            for index, child_id in enumerate(fam.children):
                person = self.people[child_id]
                output.append(f'{person.name}')
            out_str = str(output).replace("'", '', 100)
            log.write(f'  Children: {out_str[1:-1]}')


    def _test_number_connected_to_start(self):
        # start with first family, how many connected to that family
        inds_seen = set()

        def _recurive(family_id):
            nonlocal inds_seen
            if family_id in self.families:
                # count people in this family
                fam = self.families[family_id]

                husband = self.get_person(fam.husband)
                if husband != None:
                    if husband.id not in inds_seen:
                        inds_seen.add(husband.id)
                    _recurive(husband.parents)
                
                wife = self.get_person(fam.wife)
                if wife != None:
                    if wife.id not in inds_seen:
                        inds_seen.add(wife.id)
                    _recurive(wife.parents)

                for child_id in fam.children:
                    if child_id not in inds_seen:
                        inds_seen.add(child_id)


        _recurive(self.start_family_id)
        return len(inds_seen)


    def _count_generations(self, family_id):
        max_gen = -1

        def _recurive_gen(id, gen):
            nonlocal max_gen
            if id in self.families:
                if max_gen < gen:
                    max_gen = gen

                fam = self.families[id]

                husband = self.get_person(fam.husband)
                if husband != None:
                    _recurive_gen(husband.parents, gen + 1)
                
                wife = self.get_person(fam.wife)
                if wife != None:
                    _recurive_gen(wife.parents, gen + 1)

        _recurive_gen(family_id, 0)
        return max_gen + 1

    def __str__(self):
        out = '\nTree Stats:\n'
        out += f'Number of people                    : {len(self.people)}\n'
        out += f'Number of families                  : {len(self.families)}\n'
        out += f'Max generations                     : {self._count_generations(self.start_family_id)}\n'
        out += f'People connected to starting family : {self._test_number_connected_to_start()}\n'
        return out


# ----------------------------------------------------------------------------
# Do not change
class Request_thread(threading.Thread):

    def __init__(self, url):
        # Call the Thread class's init function
        threading.Thread.__init__(self)
        self.url = url
        self.response = {}

    def run(self):
        response = requests.get(self.url)
        # Check the status code to see if the request succeeded.
        if response.status_code == 200:
            self.response = response.json()
        else:
            print('RESPONSE = ', response.status_code)


# -----------------------------------------------------------------------------
# Change this function to speed it up
def depth_fs_pedigree(family_id, tree):
    if family_id == None:
        return

    print(f'Retrieving Family: {family_id}')

    req_family = Request_thread(f'{TOP_API_URL}/family/{family_id}')
    req_family.start()
    req_family.join()

    new_family = Family(family_id, req_family.response)
    tree.add_family(new_family)

    husband = None
    wife = None
    # Get husband details
    husband_id, wife_id, children_ids = new_family.husband, new_family.wife, [c for c in new_family.children if not tree.does_person_exist(c)]
    print(f'   Retrieving Husband : {husband_id}')
    print(f'   Retrieving Wife    : {wife_id}')
    print(f'   Retrieving children: {str(children_ids)[1:-1]}')
    req_person = [Request_thread(f'{TOP_API_URL}/person/{id}') for id in [husband_id, wife_id] + children_ids]

    [t.start() for t in req_person]
    [t.join() for t in req_person]
    [husband, wife] = [Person(r.response) for r in req_person[0:2]]
    for person in req_person:
        if person is not None:
            tree.add_person(Person(person.response))
    threads = [threading.Thread(target=depth_fs_pedigree, args=(p.parents, tree)) for p in [husband, wife] if p is not None]
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]

# -----------------------------------------------------------------------------
# You should not change this function
def part1(log, start_id, generations):
    tree = Tree(start_id)

    req = Request_thread(f'{TOP_API_URL}/start/{generations}')
    req.start()
    req.join()

    log.start_timer('Depth-First')
    depth_fs_pedigree(start_id, tree)
    total_time = log.stop_timer()

    req = Request_thread(f'{TOP_API_URL}/end')
    req.start()
    req.join()

    tree.display(log)
    log.write(tree)
    log.write(f'total_time                   : {total_time}')
    log.write(f'People and families / second : {(tree.get_person_count()  + tree.get_family_count()) / total_time}')
    log.write('')
    
# -----------------------------------------------------------------------------
def breadth_fs_pedigree(start_id, tree):
    #      - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5
    # This video might help understand BFS
    # https://www.youtube.com/watch?v=86g8jAQug04

    req_sem = threading.Semaphore(5)
    #tree_lock = threading.Lock()
    #Used internally.
    def get_family(family_id):
        """
        Fetches the family from id.
        Add family to tree.
        Put parents in current_parent_id_list
        put children in current_child_id_list
        """
        req_family = Request_thread(f'{TOP_API_URL}/family/{family_id}')
        with req_sem:
            #We are in a helper thread, so fetch without making a new thread.
            req_family.run()
        new_family = Family(family_id, req_family.response)
        #with tree_lock:
        tree.add_family(new_family)
        parents_ids = [new_family.husband, new_family.wife]
        current_parent_id_list.extend(parents_ids)
        children_ids = [c for c in new_family.children if not tree.does_person_exist(c)]
        current_child_id_list.extend(children_ids)

    def get_parent(id):
        """
        Fetch the person of the given id.
        Append the result's parents' family id to next_family_id_list
        Return the result person
        """
        req_person = Request_thread(f'{TOP_API_URL}/person/{id}')
        with req_sem:
            req_person.run()
        new_person = Person(req_person.response)
        if new_person != None:
            #with tree_lock:
            tree.add_person(new_person)
            return new_person.parents

    def get_child(id):
        """
        Fetch the person of the given id.
        Return the result person.
        """
        get_parent(id)

    current_family_id_list = [start_id]
    next_family_id_list = []
    while len(current_family_id_list) !=  0:
        current_parent_id_list = []
        current_child_id_list = []
        with ThreadPool(10) as pool:
            # get family and collect parents, children
            pool.map(get_family, current_family_id_list)
            print("got all the family pool")
            print(f"parents: {current_parent_id_list}")
            print(f"children: {current_child_id_list}")
            # get parents and collect people, next generation family ids
            next_family_id_list = pool.map(get_parent, current_parent_id_list)
            print(f"next family id list: {next_family_id_list}")
            # get children and collect people
            pool.map(get_child, current_child_id_list)
        current_family_id_list = [id for id in next_family_id_list if id is not None]
        next_family_id_list = []
    

# -----------------------------------------------------------------------------
# You should not change this function
def part2(log, start_id, generations):
    tree = Tree(start_id)

    req = Request_thread(f'{TOP_API_URL}/start/{generations}')
    req.start()
    req.join()

    log.start_timer('Breadth-First')
    breadth_fs_pedigree(start_id, tree)
    total_time = log.stop_timer()

    req = Request_thread(f'{TOP_API_URL}/end')
    req.start()
    req.join()

    tree.display(log)
    log.write(tree)
    log.write(f'total_time      : {total_time}')
    log.write(f'People / second : {tree.get_person_count() / total_time}')
    log.write('')


# -----------------------------------------------------------------------------
def main():
    log = Log(show_terminal=True, filename_log='assignment.log')

    # starting family
    req = Request_thread(TOP_API_URL)
    req.start()
    req.join()

    print(f'Starting Family id: {req.response["start_family_id"]}')
    start_id = req.response['start_family_id']

    part1(log, start_id, 6)

    part2(log, start_id, 6)


if __name__ == '__main__':
    main()

