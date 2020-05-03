import handling, connections, executor, parser
import PySimpleGUI as sg
from threading import Thread
from queue import *
from time import sleep


# You know where you are? You're in the jungle, baby! You're gonna die!




def gui():
    sg.theme('DarkAmber')
    activeExecutor = None
    inputList = None
    grabbable = False
    guiqueue = Queue()

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
                                 [sg.Multiline(key='urloutput', do_not_clear=False, size=(54, 8))]]
                                   )]
                     ]),

        ]

    ]

    connectionlayout = [
        [sg.T('Initialize and manage your connections here.')],
        [sg.Frame(element_justification='left',
                  title='Proxy Configuration', layout=[
                [sg.T('Select the number of sessions/threads to create.', size=(20, 2))],
                [sg.Slider(range=(1, 16), default_value=1, size=(20, 4), orientation='horizontal', key='number')],
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
                [sg.Multiline(key='headeroutput', do_not_clear=False, size=(56, 6))]])]

    ]
    scrapelayout = [
        [sg.T('Scrape the data. (This might stop responding, but it is still working!)')],
        [sg.Frame(element_justification='right',
                  title='Scraping Progress', layout=[
                [sg.Button('Scrape', key='scrape',
                           tooltip='Begins scraping!')],
                [sg.Output(key='scrapeout', size=(55, 17))]]
                  )
         ]
    ]
    parselayout = [
        [sg.T('Choose what information you are going to parse.')]
    ]
    outputlayout = [
        [sg.T('Select the format you would like to export your scraped information as.')]
    ]
    masterlayout = [
        [sg.Button('Exit', tooltip='Bye! :)')],
        [sg.TabGroup([[sg.Tab('Input', inputlayout), sg.Tab('Connections', connectionlayout),
                       sg.Tab('Scraping', scrapelayout),
                       sg.Tab('Parsing', parselayout), sg.Tab('Output', outputlayout)]])],

    ]

    window = sg.Window('Scraper GUI', masterlayout,
                       no_titlebar=True, grab_anywhere=grabbable, keep_on_top=True)
    while True:
        event, values = window.read()
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

        if event == 'executor':
            activeExecutor = executor.Executor(int(values['number']),
                                               values['timeout'], values['delay'])
            for session in activeExecutor.sessions:
                proxyinfo = list(session.proxies.items())[0]
                agentinfo = list(session.headers.values())[0]
                window['proxyoutput'].print('Proxy IP: {}:{}, \n'.format(proxyinfo[0],
                                                                         proxyinfo[1]))
                window['headeroutput'].print('User-Agent: {}, \n'.format(agentinfo))
        if event == 'scrape':
            thread = Thread(target=activeExecutor.run, args=(inputList, guiqueue), daemon=True)
            thread.start()
            try:
                message = guiqueue.get_nowait()
            except Empty:
                message = None
            if message:
                window.read()
        if event in (None, 'Exit'):
            break

    window.close()
    del window


if __name__ == '__main__':
    gui()
