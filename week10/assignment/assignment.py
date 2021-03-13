"""
Course: CSE 251
Lesson Week: 10
File: assignment.py
Author: <your name>

Purpose: assignment for week 10 - reader writer problem

Instructions:

- Review TODO comments

- writer: a process that will "write"/send numbers to the reader.  
  To keep things simple, send random values from 0 to 255 to the reader.

- reader: a process that receive numbers sent by the writer.

- You don't need any sleep() statements for either process.

- You are able to use lock(s) and semaphores(s).  When using locks, you can't
  use the arguments "block=False" or "timeout".

- You must use ShareableList between the two processes.  
  You are only allowed to use BUFFER_SIZE number of positions
  in this ShareableList for tranfering data from the writer to
  the reader.  However, you can use other parts of the ShareableList
  for other purposes if you want by increasing the size of the ShareableList.
  This buffer area will act like a queue - First In First Out.

- Not allowed to use Queue(), Pipe(), List() or any other data structure.

- Not allowed to use Value() or Array() or any other shared data type from 
  the multiprocessing package.

Add any comments for me:



"""
import random
from multiprocessing.managers import SharedMemoryManager
import multiprocessing as mp

#buffer
#Space used by both processes
# w writer, r reader
# Semaphores
BUFFER_SIZE = 10

# Everything is put in the front
# rw writer, r reader
# LOCK
FRONT_POINTER = BUFFER_SIZE + 0

# Everything is taken from the back
# rw reader
# No lock necessary
BACK_POINTER = BUFFER_SIZE + 1

# False unless the process is finished.
# w writer, r reader
# LOCK
PROCESS_FINISHED_POINTER = BUFFER_SIZE + 2

# address w writer, r main
# no lock necessary
TOTAL_SENT_COUNT_POINTER = BUFFER_SIZE + 3

# address w reader, r main
# no lock necessary
TOTAL_RECVD_COUNT_POINTER = BUFFER_SIZE + 4

TOTAL_BUFFER_SIZE = BUFFER_SIZE + 5
def send_byte(buf, send_sem, recv_sem, front_lock, byte):
    """
    send a byte to the shared memory queue
    """
    send_sem.acquire()
    buf[send_addr(buf, front_lock)] = byte
    rotate_send_addr(buf, front_lock)
    recv_sem.release()
    pass

def send_addr(buf):
    """
    return the index in the buffer of the next call to send
    """
    return buf[FRONT_POINTER]

def rotate_send_addr(buf):
    """
    increment the next index where the send will be sent
    """
    buf[FRONT_POINTER] = buf[FRONT_POINTER] + 1 % BUFFER_SIZE

def recv_byte(mem, send_sem, recv_sem):
    """
    Receive a byte from the shared memory queue
    """
    #wait until there is something to receive
    recv_sem.acquire()
    x = mem[recv_addr(mem)]
    rotate_recv_addr(mem)
    #Signal there is space to send.
    send_sem.release()
    return x

def rotate_recv_addr(buf):
    """
    increase the address in shared memory to receive from
    """
    
    buf[BACK_POINTER] = buf[BACK_POINTER] + 1 % BUFFER_SIZE
    pass

def recv_addr(buf):
    return buf[BACK_POINTER]

def main():

    # This is the number of values that the writer will send to the reader
    items_to_send = random.randint(100000, 1000000)

    smm = SharedMemoryManager()
    smm.start()

    # TODO - Create a ShareableList to be used between the processes

    # TODO - Create any lock(s) or semaphore(s) that you feel you need

    # TODO - create reader and writer processes

    # TODO - Start the processes and wait for them to finish

    print(f'{items_to_send} sent by the writer')

    # TODO - Display the number of numbers/items received by the reader.

    smm.shutdown()


if __name__ == '__main__':
    main()
