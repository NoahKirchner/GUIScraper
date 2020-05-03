import requests
import time as t
import shadow_useragent
import proxyscrape as ps

ps.create_collector("ProxyGen", 'http')
agentgen = shadow_useragent.ShadowUserAgent()


# Feed this a session object created via the requests module, a url and a timeout variable
# if you'd like to change it. @Todo logging
def connect(session:requests.Session(), url:str, timeout: int = 5):
    start = t.perf_counter()
    session = session
    connection = session.get(url, timeout=timeout)
    code = connection.status_code
    content = connection.content
    end = t.perf_counter()
    time = end-start
    print('S{} T{} URL: {}'.format(code,round(time,2),url))
    return (code, time, url, content)
# Returns a tuple containing the HTTP status code, the time it took the function
# to complete and then the raw output from the request itself (AKA the website content)


# Input the number of useragents to generate. @Todo logging
def genuser(number:int):
    useragent = agentgen
    useragent_list = []
    for _ in range(number):
        useragent_list.append(useragent.random_nomobile)
    return useragent_list
# Returns a list of randomly selected non-mobile useragents based on the input number.


# Feed this a number of free proxies to generate. @Todo logging, investigate why protocol not work
def genproxy(number:int):
    collector = ps.get_collector(name='ProxyGen')
    collector.refresh_proxies()
    proxy_list = []
    for _ in range(number):
        proxy = collector.get_proxy({'anonymous': True})
        proxy_list.append(proxy)
        collector.remove_proxy(proxy)
    return proxy_list
# Returns a list of named tuples (Ain't that a doozy) containing proxy information.
