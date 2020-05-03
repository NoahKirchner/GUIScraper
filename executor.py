import connections
import handling
from threading import Thread
from queue import *
import requests
from time import sleep, perf_counter
import numpy as np



# Executor class is basically just the class you use to multithread the connections
# from connections.py. I mean I probably could've put connections.py in here but
# compartmentalizing makes my monkey brain feel nice so here we are.
class Executor:

    # Initialization, sets up variables that will be used throughout the class
    # based on number of threads/sessions to create & protocol (http, https, socks4, socks5)
    # @Todo logging & delete this ugly extra comment line
    def __init__(self, number:int, timeout:int = 5, delay:int = 1):
        self.number = number
        self.timeout = timeout
        self.delay = delay
        self.sessions = []
        self.workers = dict()
        self.queue = Queue()
        for proxy, agent in zip(connections.genproxy(number),
                                connections.genuser(number)):
            session = requests.Session()
            session.proxies.update({(proxy.host, proxy.port)})
            session.headers.update({'User-Agent': agent})
            self.sessions.append(session)
    # For loop outputs a list of session objects that all have unique proxy
    # and header information.

    # Calls the connect function from connect.py on a range of URLs instead of just one.
    # Requires a numerical range (generated in run from the list of URLs) and the
    # list of URLs itself, as well as a session to assign to the thread and the
    # output queue. @Todo logging
    def rangeconnect(self, inputlist:list, rangelist:list, session: requests.Session(), guiqueue:Queue):
        for i in rangelist:
            try:
                result = connections.connect(session, inputlist[i], self.timeout)
                guiqueue.put(result)
                self.queue.put(result)
            except:
                pass
    # It outputs the result of of the connection function by appending it to the queue
    # that was passed to it.

    # The method to call to actually make the connections. It only takes an input list.
    # This method creates a number of threads equal to the number of sessions/arg passed
    # when the class was created. On each of those threads, it then calls the above
    # function but with a unique session (proxy and user-agent data) that is generated
    # upon class initialization. @Todo logging
    def run(self, inputlist:list, guiqueue:Queue):
        ranges = np.arange(len(inputlist))
        ranges = np.array_split(ranges,self.number)
        start = perf_counter()
        threadlist = []
        for i in range(0, self.number):
            thread = Thread(target=self.rangeconnect,args=(inputlist,ranges[i],self.sessions[i], guiqueue))
            thread.start()
            threadlist.append(thread)
            sleep(self.delay)
        for thread in threadlist:
            thread.join()
        end = perf_counter()
        print('Scraping Complete \nURLs Processed: {}\n'
              'Total Time: {} Seconds'.format(self.queue.qsize(), round(end-start)))
        return self.queue
    # This method returns a queue object which should contain tuples returned by the connect
    # function.


