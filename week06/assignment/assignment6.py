"""
Course: CSE 251
Lesson Week: 06
File: assignment.py
Author: Brother Comeau

Purpose: Processing Plant

Instructions:

- Implement the classes to allow gifts to be created.

"""

from datetime import datetime, timedelta
import random
import json
import threading
import multiprocessing as mp
from matplotlib.pylab import plt
import numpy as np
import os.path
import datetime
import time

# Include cse 251 common Python files - Don't change
import os, sys
sys.path.append('../../code')
from cse251 import *

CONTROL_FILENAME = 'settings.txt'
BOXES_FILENAME   = 'boxes.txt'

# Settings consts
MARBLE_COUNT = 'marble-count'
CREATOR_DELAY = 'creator-delay'
BAG_COUNT = 'bag-count'
BAGGER_DELAY = 'bagger-delay'
ASSEMBLER_DELAY = 'assembler-delay'
WRAPPER_DELAY = 'wrapper-delay'

# No Global variables

class Bag():
    """ bag of marbles - Don't change for the 93% """

    def __init__(self):
        self.items = []

    def add(self, marble):
        self.items.append(marble)

    def get_size(self):
        return len(self.items)

    def __str__(self):
        return str(self.items)

class Gift():
    """ Gift of a large marble and a bag of marbles - Don't change for the 93% """

    def __init__(self, large_marble, marbles):
        self.large_marble = large_marble
        self.marbles = marbles

    def __str__(self):
        marbles = str(self.marbles)
        marbles = marbles.replace("'", "")
        return f'Large marble: {self.large_marble}, marbles: {marbles[1:-1]}'

class Marble_Creator(mp.Process):
    """ This class "creates" marbles and sends them to the bagger """

    colors = ('Gold', 'Orange Peel', 'Purple Plum', 'Blue', 'Neon Silver', 
        'Tuscan Brown', 'La Salle Green', 'Spanish Orange', 'Pale Goldenrod', 'Orange Soda', 
        'Maximum Purple', 'Neon Pink', 'Light Orchid', 'Russian Violet', 'Sheen Green', 
        'Isabelline', 'Ruby', 'Emerald', 'Middle Red Purple', 'Royal Orange', 'Big Dip O’ruby', 
        'Dark Fuchsia', 'Slate Blue', 'Neon Dark Green', 'Sage', 'Pale Taupe', 'Silver Pink', 
        'Stop Red', 'Eerie Black', 'Indigo', 'Ivory', 'Granny Smith Apple', 
        'Maximum Blue', 'Pale Cerulean', 'Vegas Gold', 'Mulberry', 'Mango Tango', 
        'Fiery Rose', 'Mode Beige', 'Platinum', 'Lilac Luster', 'Duke Blue', 'Candy Pink', 
        'Maximum Violet', 'Spanish Carmine', 'Antique Brass', 'Pale Plum', 'Dark Moss Green', 
        'Mint Cream', 'Shandy', 'Cotton Candy', 'Beaver', 'Rose Quartz', 'Purple', 
        'Almond', 'Zomp', 'Middle Green Yellow', 'Auburn', 'Chinese Red', 'Cobalt Blue', 
        'Lumber', 'Honeydew', 'Icterine', 'Golden Yellow', 'Silver Chalice', 'Lavender Blue', 
        'Outrageous Orange', 'Spanish Pink', 'Liver Chestnut', 'Mimi Pink', 'Royal Red', 'Arylide Yellow', 
        'Rose Dust', 'Terra Cotta', 'Lemon Lime', 'Bistre Brown', 'Venetian Red', 'Brink Pink', 
        'Russian Green', 'Blue Bell', 'Green', 'Black Coral', 'Thulian Pink', 
        'Safety Yellow', 'White Smoke', 'Pastel Gray', 'Orange Soda', 'Lavender Purple',
        'Brown', 'Gold', 'Blue-Green', 'Antique Bronze', 'Mint Green', 'Royal Blue', 
        'Light Orange', 'Pastel Blue', 'Middle Green')

    def __init__(self, pipeout, marble_count, creator_delay):
        mp.Process.__init__(self)
        self.pipeout = pipeout
        self.marble_count = marble_count
        self.creator_delay = creator_delay

    def run(self):
        '''
        for each marble:
            send the marble (one at a time) to the bagger
              - A marble is a random name from the colors list above
            sleep the required amount
        Let the bagger know there are no more marbles
        '''
        for _ in range(self.marble_count):
            self.pipeout.send(random.choice(Marble_Creator.colors))
            time.sleep(self.creator_delay)
        self.pipeout.send(None)

class Bagger(mp.Process):
    """ Receives marbles from the marble creator, then there are enough
        marbles, the bag of marbles are sent to the assembler """
    def __init__(self,  pipein, pipeout, bag_count, bagger_delay):
        mp.Process.__init__(self)
        self.pipeout = pipeout
        self.pipein = pipein
        self.bag_count = bag_count
        self.bagger_delay = bagger_delay

    def make_bag(self):
        bag = Bag()
        for _ in range(self.bag_count):
            marble = self.pipein.recv()
            if marble is not None:
                bag.add(marble)
            else:
                break
        return bag

    def run(self):
        '''
        while there are marbles to process
            collect enough marbles for a bag
            send the bag to the assembler
            sleep the required amount
        tell the assembler that there are no more bags
        '''
        while True:
            bag = self.make_bag()
            if bag.get_size() == self.bag_count:
                pass
                self.pipeout.send(bag)
            else:
                self.pipeout.send(None)
                break
            time.sleep(self.bagger_delay)

class Assembler(mp.Process):
    """ Take the set of marbles and create a gift from them.
        Sends the completed gift to the wrapper """
    marble_names = ('Lucky', 'Spinner', 'Sure Shot', 'The Boss', 'Winner', '5-Star', 'Hercules', 'Apollo', 'Zeus')

    def __init__(self, pipein, pipeout, assembler_delay):
        mp.Process.__init__(self)
        self.pipeout = pipeout
        self.pipein = pipein
        self.assembler_delay = assembler_delay

    def run(self):
        '''
        while there are bags to process
            create a gift with a large marble (random from the name list) and the bag of marbles
            send the gift to the wrapper
            sleep the required amount
        tell the wrapper that there are no more gifts
        '''
        while True:
            bag = self.pipein.recv()
            if bag is None:
                self.pipeout.send(None)
                break
            gift = Gift(random.choice(Assembler.marble_names), bag)
            self.pipeout.send(gift)
            time.sleep(self.assembler_delay)

class Wrapper(mp.Process):
    """ Takes created gifts and wraps them by placing them in the boxes file """
    def __init__(self, pipein, wrapper_delay, gift_count):
        mp.Process.__init__(self)
        self.pipein = pipein
        self.wrapper_delay = wrapper_delay
        self.gift_count = gift_count

    def run(self):
        '''
        open file for writing
        while there are gifts to process
            save gift to the file with the current time
            sleep the required amount
        '''
        with open("boxes.txt", mode='w') as f:
            while True:
                gift = self.pipein.recv()
                if gift is  None:
                    break
                f.write(str(gift))
                self.gift_count.value += 1
                time.sleep(self.wrapper_delay)

def display_final_boxes(filename, log):
    """ Display the final boxes file to the log file -  Don't change """
    if os.path.exists(filename):
        log.write(f'Contents of {filename}')
        with open(filename) as boxes_file:
            for line in boxes_file:
                log.write(line.strip())
    else:
        log.write_error(f'The file {filename} doesn\'t exist.  No boxes were created.')

def main():
    """ Main function """

    log = Log(show_terminal=True)

    log.start_timer()

    # Load settings file
    settings = load_json_file(CONTROL_FILENAME)
    if settings == {}:
        log.write_error(f'Problem reading in settings file: {CONTROL_FILENAME}')
        return

    log.write(f'Marble count                = {settings[MARBLE_COUNT]}')
    log.write(f'settings["creator-delay"]   = {settings[CREATOR_DELAY]}')
    log.write(f'settings["bag-count"]       = {settings[BAG_COUNT]}') 
    log.write(f'settings["bagger-delay"]    = {settings[BAGGER_DELAY]}')
    log.write(f'settings["assembler-delay"] = {settings[ASSEMBLER_DELAY]}')
    log.write(f'settings["wrapper-delay"]   = {settings[WRAPPER_DELAY]}')

    creator_out, bagger_in = mp.Pipe()
    bagger_out, assembler_in = mp.Pipe()
    assembler_out, wrapper_in = mp.Pipe()

    gift_count = mp.Value('i', 0)

    # delete final boxes file
    if os.path.exists(BOXES_FILENAME):
        os.remove(BOXES_FILENAME)

    log.write('Create the processes')

    processes = [
            Marble_Creator(creator_out, settings[MARBLE_COUNT], settings[CREATOR_DELAY]),
            Bagger(bagger_in, bagger_out,settings[BAG_COUNT], settings[BAGGER_DELAY]), 
            Assembler(assembler_in, assembler_out, settings[ASSEMBLER_DELAY]),
            Wrapper(wrapper_in, settings[WRAPPER_DELAY], gift_count)
            ]

    log.write('Starting the processes')
    for process in processes:
        process.start()

    log.write('Waiting for processes to finish')
    for process in processes:
        process.join()

    display_final_boxes(BOXES_FILENAME, log)

    log.write(f"{settings[MARBLE_COUNT] // settings[BAG_COUNT]} gifts are expected. Ho ho ho!")
    log.write(f"{gift_count.value} gifts were created. Ho ho ho!")

if __name__ == '__main__':
    main()

