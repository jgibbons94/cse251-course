"""
Course: CSE 251
Lesson Week: 04
File: assignment.py
Author: Brother Comeau

Purpose: Assignment 04 - Factory and Dealership

Instructions:

- Read the comments in the following code.  
- Implement your code where the TODO comments are found.
- No global variables, all data must be passed to the objects.
- Only the included/imported packages are allowed.  
- Thread pools are not allowed
- the shared queue between the threads that are used to hold the Car objects
  can not be greater than MAX_QUEUE_SIZE

--------------------
I think I earned a 100 on this assignment.
I followed instructions as given.
I also made it my own by saving the graph to a file instead of displaying it.
"""

import time
import queue
import threading
import random

# Include cse 251 common Python files
import os, sys
sys.path.append('../../code')
from cse251 import *

# Global Consts - Do not change
CARS_TO_PRODUCE = 500
MAX_QUEUE_SIZE = 10
SLEEP_REDUCE_FACTOR = 50

# NO GLOBAL VARIABLES!

class Car():
    """ This is the Car class that will be created by the factories """

    # Class Variables
    car_makes = ('Ford', 'Chevrolet', 'Dodge', 'Fiat', 'Volvo', 'Infiniti', 'Jeep', 'Subaru', 
                'Buick', 'Volkswagen', 'Chrysler', 'Smart', 'Nissan', 'Toyota', 'Lexus', 
                'Mitsubishi', 'Mazda', 'Hyundai', 'Kia', 'Acura', 'Honda')

    car_models = ('A1', 'M1', 'XOX', 'XL', 'XLS', 'XLE' ,'Super' ,'Tall' ,'Flat', 'Middle', 'Round',
                'A2', 'M1X', 'SE', 'SXE', 'MM', 'Charger', 'Grand', 'Viper', 'F150', 'Town', 'Ranger',
                'G35', 'Titan', 'M5', 'GX', 'Sport', 'RX')

    car_years = [i for i in range(1990, datetime.now().year)]

    def __init__(self):
        # Make a random car
        self.model = random.choice(Car.car_models)
        self.make = random.choice(Car.car_makes)
        self.year = random.choice(Car.car_years)
           
    def display(self):
        print(f'{self.make} {self.model}, {self.year}')

class Factory(threading.Thread):
    """ This is a factory.  It will create cars and place them on the car queue """

    def __init__(self, full, empty, q):
        threading.Thread.__init__(self)
        self.full = full
        self.empty = empty
        self.q = q
        self.car_count = CARS_TO_PRODUCE
        pass

    def run(self):
        for i in range(self.car_count):
            self.full.release()
            self.empty.acquire()
            self.q.put(Car())
            # Sleep a little - don't change
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR + 4))

class Dealer(threading.Thread):
    """ This is a dealer that receives cars """

    def __init__(self, full, empty, q, queue_stats):
        threading.Thread.__init__(self)
        self.full = full
        self.empty = empty
        self.q = q
        self.queue_stats = queue_stats
        self.cars_processed = 0
        pass

    def run(self):
        while True:
            size = self.q.qsize()
            #print(f"dealer: {size}")
            self.full.acquire()
            self.empty.release()
            self.queue_stats[size-1] += 1
            car = self.q.get()
            self.cars_processed += 1
            if self.cars_processed == CARS_TO_PRODUCE:
                return

            # Sleep a little - don't change
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR + 0))

def main():
    log = Log(show_terminal=True)

    full = threading.Semaphore(0)
    empty = threading.Semaphore(MAX_QUEUE_SIZE)
    q = queue.Queue()

    # This tracks the length of the car queue during receiving cars by the dealership
    # i.e., update this list each time the dealer receives a car
    queue_stats = [0] * MAX_QUEUE_SIZE

    factory = Factory(full, empty, q)

    dealer = Dealer(full, empty, q, queue_stats)

    log.start_timer()

    dealer.start()
    factory.start()

    dealer.join()
    factory.join()

    log.stop_timer(f'All {sum(queue_stats)} have been created')

    xaxis = [i for i in range(1, MAX_QUEUE_SIZE + 1)]
    plot = Plots()
    #Showing the plot hangs. Don't show the plot.
    plot.bar(xaxis, queue_stats, title=f'{sum(queue_stats)} Produced: Count VS Queue Size', x_label='Queue Size', y_label='Count', show_plot = False, filename="cars.png")

if __name__ == '__main__':
    main()
