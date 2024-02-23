
import csv
import math
import pandas as pd
import socket
from struct import unpack_from
import signal
import sys
import time
import threading
import queue
'''
test suite below
'''
import csv
def grabit():
    with open('thread1.csv', 'r') as read_obj:
        # Return a reader object which will
        # iterate over lines in the given csvfile
        csv_reader = csv.reader(read_obj)
        # convert string to list
        list_of_csv = list(csv_reader)
        return(list_of_csv)


def alternatewrite_to_file(f_name, lst_stream):
    #show_status('writing %s ...'%f_name)
    tempdf = pd.DataFrame
    finaldf = pd.DataFrame
    '''
    Need to split list into list of lists
        Need 16 intervals between timestamp2 and timestamp1
    '''
    for i in range(len(lst_stream)):
        #need to grab each row
        #below code will not work for final row, will need extrapolation
        currentTime = lst_stream[i][0]
        nextTime = lst_stream[i+1][0]
        tempdf = pd.DataFrame(lst_stream[i])
        tempdf = tempdf.iloc[1:,[0,1]]
        print(tempdf)

lst_stream = grabit()
alternatewrite_to_file("hello", lst_stream)