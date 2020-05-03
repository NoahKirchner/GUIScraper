import executor
from queue import *
from bs4 import *
import lxml
import csv
import pickle



# Takes a queue object (preferably from the Executor class in executor.py) as an input
# @Todo add logging
def extract(queue:Queue):
    contentdict = {}
    for i in range(len(list(queue.queue))):
        internal = queue.queue[i]
        if internal[3] is not None:
            contentdict.update({internal[2]:internal[3]})
    return contentdict
# Checks each value to make sure that the website had content and
# then gets rid of logging information like status codes and connection time
# Outputs a dictionary with the url as the key and content as value

# @Todo this needs to be expanded upon, namely pickling/unpickling queues and parsers
# @Todo ^^^ all data manipulation that is not IO bound or the modular parser go here


def formatcsv(url:str, inputloc:str, inputrow:int = 0):
    formatlist = []
    with open(inputloc) as csv_file:
        csv_file.seek(0)
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            formatlist.append(url + row[inputrow])
    return formatlist


def rawcsv(inputloc:str, inputrow:int = 0):
    urllist = []
    with open(inputloc) as csv_file:
        csv_file.seek(0)
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            urllist.append(row[inputrow])
        return urllist


def topickle(outputloc:str, queue:Queue):
    outfile = open(outputloc, 'wb')
    pickle.dump(extract(queue), outfile)
    outfile.close()


def unpickle(inputloc:str):
    infile = open(inputloc, 'rb')
    contentdict = pickle.load(infile)
    infile.close()
    return contentdict