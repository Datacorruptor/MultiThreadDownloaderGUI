import PySimpleGUI as sg
print = lambda *args, **kwargs: window['-ML1-' + sg.WRITE_ONLY_KEY].print(*args, **kwargs)
from download_pool_script_pruned import AddNewLink, Info, InfoF

width = 180
font = ("Consolas", 11)
layout = [[sg.Text('INFO:')],
          [sg.MLine(key='-ML1-' + sg.WRITE_ONLY_KEY, horizontal_scroll=True, disabled= True, font= font,size=(width, 20))],
          [sg.Input('', size=(width,1),font= font, key='-IN-')],
          [sg.Button('Go',font= font,size=(50,1))]]

window = sg.Window('Window Title', layout, finalize=True,element_justification='c')

prev_info = ""
while True:  # Event Loop
    event, values = window.read(timeout=1)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event in ["Go"]:
        AddNewLink(window['-IN-'].get())

    info = Info()
    info = InfoF(width)
    if len(info)>0 and info != prev_info:
        window['-ML1-' + sg.WRITE_ONLY_KEY].update("")
        print(info)
        prev_info = info

window.close()
