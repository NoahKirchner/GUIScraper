import handling, connections, executor, modparser
import PySimpleGUI as sg
from threading import Thread
from queue import *
from time import sleep

#Todo relative to whole project
# Add some form of .txt logging for ease of debugging when the meat and potatos are done
# There's a lot of different structures being passed around, a combination of list,
# dict and tuples. See if you can combine all of those to tuples if you can.

# You know where you are? You're in the jungle, baby! You're gonna die!

# @Todo This is incomprehensible spaghetti, add some comments PLEASE GOD -past me
# This is painful, but here we are. This function contains everything required
# To create the gui and implements all the dependencies listed above. The reason
# it's in a function is because that allows the program to be multithreaded, which
# is the only way to get the print output inside of the gui. Also prevents it from
# Not responding while a blocking activity is taking place, like when you start scraping.
def gui():
    # Variables and what they do @Todo convert everything to hump case or whatever the _ one is
    # Theme
    sg.theme('DarkAmber')
    # Reference to the active executor since it needs to be used multiple times.
    activeExecutor = None
    # URL input list.
    inputList = None
    # The queue that the executor sessions use to send data back to the GUI thread
    guiqueue = Queue()

    # Yarr, page layouts be here
    # @Todo reformat these so they're easier to look through
    # Page to construct the URL list.
    inputlayout = [
        [sg.T('Use this tab to create or input your URL list.')],
        [
            sg.Frame(element_justification='left', title='Input List Creation',
                     layout=[
                         [sg.InputText(size=(35, 1), key='csv'), sg.FileBrowse('Import CSV', size=(6, 2)),
                          sg.T('Column'),
                          sg.Spin([i for i in range(101)], initial_value=0, text_color='black',
                                  background_color='white', key='inputrow',
                                  tooltip='Which column the pertinent data is in')],
                         [sg.Radio('Extension from CSV', 'input', True, key='extension'),
                          sg.T('Base URL'),
                          sg.InputText('https://www.google.com/', key='baseurl',
                                       size=(25, 1),
                                       tooltip='The base URL to append the extensions in your csv to (with /)')
                          ],
                         [sg.Radio('Full URLs from CSV', 'input', True, size=(37, 2), key='full'),
                          sg.Button('Stage URLs', key='stageurl', size=(9, 2),
                                    tooltip='Generates the list of URLs to scrape.')],
                         [sg.Frame(element_justification='center',
                                   title='Staged URLs', layout=[
                                 [sg.Multiline(key='urloutput', do_not_clear=False, size=(54, 13))]]
                                   )]
                     ]),

        ]

    ]

    # Page to construct the executor class (# of threads, universal delay, timeout etc)
    connectionlayout = [
        [sg.T('Initialize and manage your connections here.')],
        [sg.Frame(element_justification='left',
                  title='Proxy Configuration', layout=[
                [sg.T('Select the number of sessions/threads to create.', size=(20, 2))],
                [sg.Spin([i for i in range(1,17)], initial_value=1, key='number',
                         text_color='black', background_color='white')],
                [sg.T('Universal Timeout'),
                 sg.T('Universal Delay')],
                [sg.Spin([i for i in range(121)], initial_value=5, text_color='black',
                         background_color='white', key='timeout'), sg.Text('Seconds'),
                 sg.Spin([i for i in range(121)], initial_value=5, text_color='black',
                         background_color='white', key='delay'), sg.Text('Seconds')],
                [sg.Button('Stage Executor', key='executor',
                           tooltip='Generates the proxies and browser headers'
                                   'that will be used for connections')]
            ]),
         sg.Frame(element_justification='right',
                  title='Staged Proxies', layout=[
                 [sg.Multiline(key='proxyoutput', do_not_clear=False, size=(23, 9))]]
                  )
         ],
        [sg.Frame(element_justification='center',
                  title='Staged Headers', layout=[
                [sg.Multiline(key='headeroutput', do_not_clear=False, size=(56, 11))]])]

    ]

    # Where to execute the scraping based on the constructed executor class & list of URLs.
    # Also has the ability to import pickled list data
    scrapelayout = [
        [sg.T('Scrape the data and export as a pickled python object')],
        [sg.Frame(element_justification='right',
                  title='Scraping Progress', layout=[
                [sg.Button('Scrape', key='scrape',
                           tooltip='Begins scraping!'),
                 sg.Button('Extract', key='extract',
                           tooltip='Extract and reformat the raw scraped data.')
                 ],
                [sg.Output(key='scrapeout', size=(55, 18))],
                [sg.InputText(size=(24, 1), key='pickleout'),
                sg.InputText(size=(15, 1), key='picklename'),
                 sg.FolderBrowse('Browse', target='pickleout'),
                 sg.Button('Export', key='pickleexport')]]
                  )
         ]
    ]

    # Aggregate all above layouts into one master page.
    masterlayout = [
        [sg.Button('Exit', tooltip='Bye! :)')],
        [sg.TabGroup([[sg.Tab('Input', inputlayout), sg.Tab('Connections', connectionlayout),
                       sg.Tab('Scraping', scrapelayout)]])],

    ]
    # End of page layouts

    # Initialize window
    # @Todo toggleable grab_anywhere
    window = sg.Window('Scraper GUI', masterlayout,
                       no_titlebar=True, grab_anywhere=True, keep_on_top=True)
    # Event loop
    while True:
        event, values = window.read()

        # If the stage URL button is hit, and using the input/baseURL & row # on the GUI
        # @Todo this can probably be made more concise.
        if event == 'stageurl':
            if len(values['csv']) == 0:
                window['urloutput'].print('You need to import a CSV first.')
            else:
                if values['extension']:
                    if len(values['baseurl']) == 0:
                        window['urloutput'].print('You need to fill in the base URL first.')
                    else:
                        try:
                            inputList = handling.formatcsv(values['baseurl'], values['csv'], values['inputrow'])
                            for url in inputList:
                                window['urloutput'].print(url)
                        except FileNotFoundError:
                            window['urloutput'].print('File not found.')
                else:
                    try:
                        inputList = handling.rawcsv(values['csv'], values['inputrow'])
                        for url in inputList:
                            window['urloutput'].print(url)
                    except FileNotFoundError:
                        window['urloutput'].print('File not found.')
        # Generate a list of URLs to iterate through, either by pulling that
        # information directly from a CSV or by appending page extensions
        # listed in a CSV onto a base URL.

        # If executor staging button is hit and using the inputs on the page.
        if event == 'executor':
            activeExecutor = executor.Executor(int(values['number']),
                                               values['timeout'], values['delay'])
            for session in activeExecutor.sessions:
                proxyinfo = list(session.proxies.items())[0]
                agentinfo = list(session.headers.values())[0]
                window['proxyoutput'].print('Proxy IP: {}:{}, \n'.format(proxyinfo[0],
                                                                         proxyinfo[1]))
                window['headeroutput'].print('User-Agent: {}, \n'.format(agentinfo))
        # Generate the sessions as you can see in executor.py, and also print out
        # that information so it's nice and purdy.

        # This one is a doozy. When scrape is hit, create a thread to run the executor
        # and begin scraping. This is to keep the gui window from not responding, and
        # also allows printouts.
        if event == 'scrape':
            thread = Thread(target=activeExecutor.run, args=(inputList, guiqueue), daemon=True)
            thread.start()
            try:
                message = guiqueue.get_nowait()
            except Empty:
                message = None
            if message:
                window.read()
        # Put all of the output into the guiqueue

        if event == 'extract':
            parselist = handling.extract(guiqueue)

        # When pickleimport button is hit
        if event == 'pickleimport':
            try:
                parselist = handling.unpickle(values['picklein'])
                print('Previously scraped data imported from {}, total'
                      ' number of pages imported is {}.'.format(values['picklein'], len(parselist)))
            except FileNotFoundError:
                print('No path was entered or the file could not be found.')
        # Unpickle the filepath using the handling module, turning it into a list.
        # Then set the internal parse list to that unpickled information.

        # When the pickleexport button is hit.
        if event == 'pickleexport':
            try:
                outputloc = values['pickleout']+'/'+values['picklename']
                handling.topickle(outputloc, guiqueue)
                print('Saved pickled list of parsable information to {}, total'
                      ' number of pages exported is {}.'.format(outputloc, len(inputList)))
            except PermissionError:
                print('Operation failed due to permission error. This could mean'
                      ' that you do not have access to the file you are attempting to'
                      ' export into, or that you failed to browse for a location entirely.')
        # Combine the two fields that comprise folder and file name with a '/' and
        # use handling.topickle to turn it into a list and then pickle it for later use.

        # End program when exit is hit.
        if event in (None, 'Exit'):
            break

    # To ensure it all returns to nothing (and comes tumbling down, tumbling down, tumbling down)
    window.close()
    del window


if __name__ == '__main__':
    gui()
