import executor
from queue import *
from bs4 import *
import lxml
import csv
import pickle


# Takes a queue object (preferably from the Executor class in executor.py) as an input
def extract(queue:Queue):
    contentlist = []
    for i in range(len(list(queue.queue))):
        internal = queue.queue[i]
        if internal[3] is not None:
            contentlist.append([internal[2],internal[3]])
    return contentlist
# Checks each value to make sure that the website had content and
# then gets rid of logging information like status codes and connection time
# Outputs a list of tuples containing URL & website content.


# Takes in a base url (https://www.google.com/ <-- with slash, without extensions),
# a path to a csv file and an input row where the extensions in that csv are.
# For example, input (https://old.nasdaq.com/symbol/) with a csv that in row 3 has
# a list of all tickers you want to scrape.
def formatcsv(url:str, inputloc:str, inputrow:int = 0):
    formatlist = []
    with open(inputloc) as csv_file:
        csv_file.seek(0)
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            formatlist.append(url + row[inputrow])
    return formatlist
# Returns a list with the extension from the CSV appended to the url for all extensions
# in the CSV.


# Takes in a csv and an input row, like the above function, but the csv and row
# should correspond to a full URL saved in a csv.
def rawcsv(inputloc:str, inputrow:int = 0):
    urllist = []
    with open(inputloc) as csv_file:
        csv_file.seek(0)
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            urllist.append(row[inputrow])
        return urllist
# Returns a list of URLs based on the CSV.


# Takes in an export location and a queue object (from the executor class) to pickle.
def topickle(outputloc:str, queue:Queue):
    outfile = open(outputloc + '.pickle', 'wb')
    pickle.dump(extract(queue), outfile)
    outfile.close()
# Exports a serialized list object created from the passed queue object.


# Unpickles a serialized list object.
def unpickle(inputloc:str):
    infile = open(inputloc, 'rb')
    contentdict = pickle.load(infile)
    infile.close()
    return contentdict
# Returns a list, yo
