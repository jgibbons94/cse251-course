"""
------------------------------------------------------------------------------
Course: CSE 251
Lesson Week: 03
File: assignment.py
Author: Brother Comeau

Purpose: Video Frame Processing

Instructions:

- Follow the instructions found in Canvas for this assignment
- No other packages or modules are allowed to be used in this assignment.
  Do not change any of the from and import statements.
- Only process the given MP4 files for this assignment

------------------------------------------------------------------------------
I think I earned a 100% on this assignment:
-> I followed the instructions
-> I customized it to selectively show the plot window.

My design is as follows:

The main program calls process_all_frames for every number in range of CPU_COUNT.

process_all_frames uses a pool of process_count processes to map process_frame through all the
frames in from 1 to FRAME_COUNT inclusive.

process_frame is adapted from the sample code.
"""

from matplotlib.pylab import plt  # load plot library
from PIL import Image
import numpy as np
import timeit
import multiprocessing as mp

# Include cse 251 common Python files
import os, sys
sys.path.append('../../code')
from cse251 import *

# If True, show the plot. Else, save time by not showing plot. I use a Jupyter
# server to run everything remotely on my laptop.  plot.show() waits for me to
# close the window, and I don't want to need to be near my laptop when I run
# everything.
SHOW_PLOT = len(sys.argv) > 1

# 4 more than the number of cpu's on your computer
CPU_COUNT = mp.cpu_count() + 4  

FRAME_COUNT = 300
#FRAME_COUNT = 20

RED   = 0
GREEN = 1
BLUE  = 2


def create_new_frame(image_file, green_file, process_file):

    # this print() statement is there to help see which frame is being processed
    print(f'{process_file[-7:-4]}', end=',', flush=True)

    image_img = Image.open(image_file)
    green_img = Image.open(green_file)

    # Make Numpy array
    np_img = np.array(green_img)

    # Mask pixels 
    mask = (np_img[:, :, BLUE] < 120) & (np_img[:, :, GREEN] > 120) & (np_img[:, :, RED] < 120)

    # Create mask image
    mask_img = Image.fromarray((mask*255).astype(np.uint8))

    image_new = Image.composite(image_img, green_img, mask_img)
    image_new.save(process_file)


def process_frame(image_number):
    image_file = rf'elephant/image{image_number:03d}.png'
    green_file = rf'green/image{image_number:03d}.png'
    process_file = rf'processed/image{image_number:03d}.png'
    create_new_frame(image_file, green_file, process_file)

def process_all_frames(process_count, log):
    log.write(f'process_count = {process_count}')
    start_time = timeit.default_timer()
    with mp.Pool(process_count) as p:
        p.map(process_frame, range(1, FRAME_COUNT + 1))
    time_taken = timeit.default_timer() - start_time
    print()
    log.write(f'Time To Process all images = {time_taken}')
    return time_taken


if __name__ == '__main__':
    # single_file_processing(300)
    # print('cpu_count() =', cpu_count())

    all_process_time = timeit.default_timer()
    log = Log(show_terminal=True)

    xaxis_frames = [i + 1 for i in range(CPU_COUNT)]
    yaxis_times = [process_all_frames(x, log) for x in xaxis_frames]

    log.write(f'Total Time for ALL procesing: {timeit.default_timer() - all_process_time}')

    # create plot of results and also save it to a PNG file
    plt.plot(xaxis_frames, yaxis_times, label=f'{FRAME_COUNT}')
    
    plt.title('CPU Core yaxis_times VS CPUs')
    plt.xlabel('CPU Cores')
    plt.ylabel('Seconds')
    plt.legend(loc='best')

    plt.tight_layout()
    plt.savefig(f'Plot for {FRAME_COUNT} frames.png')
    if SHOW_PLOT:
        plt.show()
