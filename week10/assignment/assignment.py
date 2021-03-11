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
BUFFER_SIZE = 10
# Everything is put in the front
FRONT_POINTER = BUFFER_SIZE + 0
# Everything is taken from the back
BACK_POINTER = BUFFER_SIZE + 1
# 0 unless the process is finished.
PROCESS_FINISHED_POINTER = BUFFER_SIZE + 2
INT_SIZE = 4
TOTAL_SENT_INT_POINTER = 0 * INT_SIZE
TOTAL_RECVD_SENT_POINTER = 1 * INT_SIZE
TOTAL_BUFFER_SIZE = min(BUFFER_SIZE + 3, INT_SIZE*2)

def send_byte(buf, sem_send, sem_recv, byte):
    """
    send a byte to the shared memory queue
    """
    sem_send.acquire()
    buf[send_addr(buf)] = byte
    rotate_send_addr(buf)
    sem_recv.release()
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

def recv_byte(mem, sem_send, sem_recv):
    """
    Receive a byte from the shared memory queue
    """
    #wait until there is something to receive
    sem_recv.acquire()
    x = mem[recv_addr(mem)]
    rotate_recv_addr(mem)
    #Signal there is space to send.
    sem_send.release()
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
