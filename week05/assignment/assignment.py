"""
Course: CSE 251
Lesson Week: 05
File: assignment.py
Author: Brother Comeau
Purpose: Assignment 05 - Factories and Stores
Instructions:

- Read the comments in the following code.  
- Implement your code where the TODO comments are found.
- No global variables, all data must be passed to the objects.
- Only the included/imported packages are allowed.  
- Thread/process pools are not allowed
- the shared queue between the threads that are used to hold the Car objects
  can not be greater than MAX_QUEUE_SIZE
- 
--------------------
I think I earned a 100 on this assignment. (tier 5)
I followed instructions as given.
I also made it my own by saving the graph to a file instead of displaying it. I commented out this change so it will be easier to grade.
"""

from datetime import datetime, timedelta
import time
import queue
import threading
import random

# Include cse 251 common Python files
import os, sys
sys.path.append('../../code')
from cse251 import *

# Global Consts
MAX_QUEUE_SIZE = 10
SLEEP_REDUCE_FACTOR = 50
CARS_TO_CREATE_PER_FACTORY = 200

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

    def __init__(self, full, empty, q, car_count, barrier, id):
        threading.Thread.__init__(self)
        self.full = full
        self.empty = empty
        self.q = q
        self.car_count = car_count
        self.barrier = barrier
        self.id = id
        pass

    def run(self):
        # TODO produce the cars
        for i in range(self.car_count):
            #empty--
            self.empty.acquire()
            self.q.put(Car())
            #full++
            self.full.release()
            # Sleep a little - don't change
            #time.sleep(random.random() / (SLEEP_REDUCE_FACTOR + 4))

        # TODO wait until all of the factories are finished producing cars
        self.barrier.wait()

        # TODO "Wake up/signal" the dealerships one more time.  Select one factory to do this
        if self.id == 0:
            #empty --
            self.empty.acquire()
            self.q.put(None)
            #full ++
            self.full.release()
        pass



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
            #full --
            self.full.acquire()
            size = self.q.qsize()
            car = self.q.get(block=False)
            #empty ++
            self.empty.release()
            if car == None:
                self.full.release()
                self.empty.acquire()
                self.q.put(None)
                return
            self.queue_stats[size-1] += 1
            self.cars_processed += 1

            # Sleep a little - don't change
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR + 0))



def run_production(factory_count, dealer_count):
    """ This function will do a production run with the number of
        factories and dealerships passed in as arguments.
    """

    # TODO Create semaphore(s)
    full = threading.Semaphore(0)
    empty = threading.Semaphore(MAX_QUEUE_SIZE)
    # TODO Create queue(s)
    q = queue.Queue()
    # TODO Create lock(s)
    # TODO Create barrier(s)
    barrier = threading.Barrier(factory_count)

    # This is used to track the number of cars receives by each dealer
    dealer_stats = list([0] * dealer_count)

    # This tracks the length of the car queue during receiving cars by the dealerships
    # It is passed to each dealership to fill out
    queue_stats = list([0] * MAX_QUEUE_SIZE)
    # This tracks the length of the car queue during receiving cars by the dealership
    # i.e., update this list each time the dealer receives a car
    queue_stats = [0] * MAX_QUEUE_SIZE

    # TODO create your factories, each factory will create CARS_TO_CREATE_PER_FACTORY
    factories = [Factory(full, empty, q, CARS_TO_CREATE_PER_FACTORY, barrier, i) for i in range(factory_count)]

    # TODO create your dealerships
    dealers = [Dealer(full, empty, q, queue_stats) for _ in range(dealer_count)]

    log.start_timer()

    # TODO Start factories and dealerships
    for dealer in dealers:
        dealer.start()
    for factory in factories:
        factory.start()

    # TODO Wait for factories and dealerships to complete
    for dealer in dealers:
        dealer.join()
    for factory in factories:
        factory.join()

    run_time = log.stop_timer(f'{sum(queue_stats)} cars have been created')

    # This function must return the following - Don't change!
    return (run_time, sum(queue_stats))


def main(log):
    """ Main function - DO NOT CHANGE! """

    xaxis = []
    times = []
    for i in [1, 2, 3, 4, 5, 10, 15, 20, 25, 30]:
        run_time, cars_produced = run_production(i, i)

        assert cars_produced == (CARS_TO_CREATE_PER_FACTORY * i)
        
        xaxis.append(i)
        times.append(run_time)

    plot = Plots()
    plot.bar(xaxis, times, title=f'Production Time VS Threads', x_label='Thread Count', y_label='Time')
#    plot.bar(xaxis, times, title=f'Production Time VS Threads', x_label='Thread Count', y_label='Time', show_plot = False, filename = "cars.png")


if __name__ == '__main__':

    log = Log(show_terminal=True)
    main(log)


