'''
IO communications

'''


'''
Need methods for dynamically handling online/offline multiprocess stuff


'''
from multiprocessing import Process, Manager

'''need to do in batches?'''


'''producer fills the queue with '''
def producer(queue, data_list):
    for item in data_list:
        print(f"Producing: {item}")
        queue.put(item)

    # Signal the end of data with a sentinel value
    queue.put(None)

def consumer(queue):
    while True:
        data_item = queue.get()
        if data_item is None:
            break
        print(f"Consuming: {data_item}")

if __name__ == "__main__":
    with Manager() as manager:
        # Create a managed Queue
        shared_queue = manager.Queue()

        # Example list with undefined length
        data_list = ["Packet 0", "Packet 1", "Packet 2", "Packet 3", "Packet 4"]

        # Create and start producer and consumer processes
        producer_process = Process(target=producer, args=(shared_queue, data_list))
        consumer_process = Process(target=consumer, args=(shared_queue,))

        producer_process.start()
        consumer_process.start()

        # Wait for the producer to finish producing
        producer_process.join()

        # Wait for the consumer to finish consuming
        consumer_process.join()
