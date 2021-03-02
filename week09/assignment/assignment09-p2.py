"""
Course: CSE 251 
Lesson Week: 09
File: assignment09-p2.py 
Author: <Add name here>

Purpose: Part 2 of assignment 09, finding the end position in the maze

Instructions:
- Do not create classes for this assignment, just functions
- Do not use any other Python modules other than the ones included
- Each thread requires a different color by calling get_color()


This code is not interested in finding a path to the end position,
However, once you have completed this program, describe how you could 
change the program to display the found path to the end position.

What would be your strategy?  

When the thread reaches a fork, Use a thread pool to get the values returned from each extended path
like in part 1. Of the values returned, if there is a non-empty list, extend the current value
list to it and return the current value list. Otherwise return the empty list.


Why would it work?

This is exactly the approach I took in part 1, except instead of using recursion it uses threads.
This approach will probably be slower because it explores every square the algorithm can reach and
creates many threads, but it will return a direct path.

"""
import math
import threading 
from screen import Screen
from maze import Maze

import cv2

# Include cse 251 common Python files - Dont change
import os, sys
sys.path.append('../../code')
from cse251 import *

SCREEN_SIZE = 800
COLOR = (0, 0, 255)
COLORS = (
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (255,255,0),
    (0,255,255),
    (255,0,255),
    (128,0,0),
    (128,128,0),
    (0,128,0),
    (128,0,128),
    (0,128,128),
    (0,0,128),
    (72,61,139),
    (143,143,188),
    (226,138,43),
    (128,114,250)
)

# Globals
current_color_index = 0
thread_count = 0
stop = False

def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color

def maze_can_move(lock, maze, row, col):
    with lock:
        return maze.can_move_here(row, col)

def solve_path(maze, start, color, path_found, lock):
    """Find a path to the next dead end.
    When a fork is reached, spawn a new thread for every path except 1,
    and go down the remaining path.
    Push all created threads to threads.
    When a dead end is reached or path_found is True, die.
    When the end is reached, set path_found to True."""
    threads = []
    (row, col) = start
    while True:
        if path_found[0] or not maze_can_move(lock, maze, row, col):
            [thread.join() for thread in threads]
            return
        with lock:
            maze.move(row, col, color)
        moves = maze.get_possible_moves(row, col)
        if len(moves) == 0:
            if maze.at_end(row, col):
                path_found[0] = True
            [thread.join() for thread in threads]
            return
        elif len(moves) > 1:
            new_threads = [threading.Thread(target = solve_path, args =
                (maze, moves[i], get_color(), path_found, lock)) for i in range(len(moves) - 1)]
            threads.extend(new_threads)
            [thread.start() for thread in new_threads]
            (row, col) = moves[-1]
        else:
            (row, col) = moves[0]



def solve_find_end(maze):
    """ finds the end position using threads.  Nothing is returned """
    # A bool copies its value to the next thread, but a list carries its values to all threads.
    path_found = [False]
    start_pos = maze.get_start_pos()
    color = get_color()
    lock = threading.Lock()
    threads = []
    start_thread = threading.Thread(target = solve_path,
        args = (maze, start_pos, color, path_found, lock))
    threads.append(start_thread)
    start_thread.start()
    start_thread.join()

def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

    done = False
    speed = 1
    while not done:
        if screen.play_commands(speed): 
            key = cv2.waitKey(0)
            if key == ord('+'):
                speed = max(0, speed - 1)
            elif key == ord('-'):
                speed += 1
            elif key != ord('p'):
                done = True
        else:
            done = True



def find_ends(log):
    """ Do not change this function """

    files = (
        ('verysmall.bmp', True),
        ('verysmall-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False)
    )

    log.write('*' * 40)
    log.write('Part 2')
    for filename, delay in files:
        log.write()
        log.write(f'File: {filename}')
        find_end(log, filename, delay)
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)



if __name__ == "__main__":
    main()