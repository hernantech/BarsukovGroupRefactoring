'''
https://medium.com/@shahooda637/multi-processing-in-python-32d4b1c97354
'''

import multiprocessing
import time

import threading
import multiprocessing

class SuperVisor:
    def __init__(self, param1, param2, use_processes, number_equipment):
        self.param1 = param1
        self.param2 = param2
        self.use_processes = use_processes
        self.number_eq = number_equipment
        #self.process_init(self)

    def process_init(self):
        if self.use_processes == True:
            processes = []
            arglist = ["process1", "process2"]
            for i in range(self.number_eq):
                process = multiprocessing.Process(target=self.equipment_process, args=(arglist[i],))
                print(process)
                processes.append(process)
                process.start()
            for process in processes:
                process.join()
        else:
            print("arg not propogating")
    def equipment_process(self, arg1):
        print(arg1)

#defining our function we want to apply multiprocessing on
#01 the producer function to add elements in the queue
def producer(q):
  for item in range(5):
    q.put(item)
    print(f"Produced:  {item}")


#02 consumer function to get elements from the queue
def consumer(q):
  while True:
    item = q.get()
    if item is None:
      break
    print(f"Consumed: {item}")


if __name__ == "__main__":
  #creating a multiprocessing queue
  q = multiprocessing.Queue()

  #creating the producer and consumer processes
  producer_process = multiprocessing.Process(target=producer, args=(q,))
  consumer_process = multiprocessing.Process(target=consumer, args=(q,))

  #starting the processes
  producer_process.start()
  consumer_process.start()

  #finish the producer, signal the consumer to exit
  producer_process.join()
  q.put(None) #signaling the consumer about no more data in the queue
  consumer_process.join()