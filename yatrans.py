#!/usr/bin/env python3

__author__ = 'esendjer'
__license__ = 'MIT'
__version__ = '0.1'
__email__ = 'esendjer@gmail.com'
__status__ = 'Development'

import tkinter
from subprocess import Popen, PIPE, DEVNULL
import requests
import json
import os
from images import *
import sys

# Your API key
api_key = 'YOUR_API_KEY'

# Default variables from file
rvar = {
    '_comment': 'It is JSON config for YaTrans',
    'prilng': 'en', 
    'seclng': 'ru',
    'color': 'gray80',
    'acolor': 'white',
    'timesec': 7,
    'winwidth': 350,
    'winheight': 350,
    'shiftx': 5,
    'shifty': 5,
    'font': 'DejaVu Sans',
    'size': '11',
    'style': 'bold',
    'cpclip': 'xsel',     # or xclip. Or maybe it is your a program
    'pget': '-o',         # and params for get clipboard
    'pset': '-ib'         # and params for set (add) clipboard via STDIN
}


# Path to dir with config file and path to config file
jsonfile = os.path.expanduser('~') + '/.config/yatrans/config.json'
jsonpath = os.path.expanduser('~') + '/.config/yatrans'


# Additional vars
texttr = []
messg = []
killid = []
aid, did = [], []


# Reading and adding (creating) variables from the file
os.makedirs(jsonpath, exist_ok=True)
if os.path.isfile(jsonfile):
    with open(jsonfile, 'r') as f:
        try:
            jsnvar = json.loads(f.read())
            nojsn = False
        except:
            messg.append('Config is not JSON!')
            nojsn = True

    for n in rvar.keys():
        if nojsn or None is jsnvar.get(n):
            vars()[n] = rvar.get(n)
        else:
            vars()[n] = jsnvar.get(n)

else:
    messg.append('Config file not exist! \nCreated new config file')
    with open(jsonfile, 'w') as f:
        f.write(json.dumps(rvar) + '\n')

    for n in rvar.keys():
        vars()[n] = rvar.get(n)


# Copy to clipboard selected the text and get it from STDOUT
with Popen([cpclip, pget], stdout=PIPE, stderr=PIPE) as proc:
     ff = proc.stdout.read()
     er = proc.stderr.read().decode()
     if len(er.split()) > 0:
         messg.append(er)



# Detecting lang
if len(ff.decode().strip().split()) > 3:
    textdt = ' '.join(ff.decode().strip().split()[0:3])

else:
    textdt = ff.decode()

urldt = 'https://translate.yandex.net/api/v1.5/tr.json/detect'
paramsdt = {'key': api_key,
          'text': textdt}
try:
    yadt = requests.post(urldt, params=paramsdt)

    if yadt.status_code == 200:
        prilng = yadt.json()['lang']
    elif yadt.status_code != 400:
        messg.append('Error connection: {}'.format(yadt.status_code))
except:
    messg.append('Not connected to network!')


# Translating
urltr = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
paramstr = {'key': api_key,
          'text': ff.decode().strip(),
          'format': 'plain',
           'lang': prilng + '-' + seclng}
try:
    yatr = requests.post(urltr, params=paramstr)
    if yatr.status_code == 200:
        transtext = yatr.json()['text']

        for i in range(len(transtext)):
            for n in transtext[i].split('\n'):
                texttr.append(n)

    elif yatr.status_code != 400:
        messg.append('Error connection: {}'.format(yatr.status_code))
except:
    messg.append('Not connected to network!')


# Action for Button Copy to clipboard
def cpcl(objtext: object):
    dd = objtext.get(1.0, 'end')
    if len(pset.split()) == 0:
        with Popen([cpclip], stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL) as proc:
            proc.communicate(input=dd.encode())

    else:
        with Popen([cpclip] + pset.strip().split(), stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL) as proc:
            proc.communicate(input=dd.encode())


# Actions for mouse events
def onwin(obj: object, leave: bool):
    global killid
    global aid, did
    if obj.winfo_rootx() + obj.winfo_width() > obj.winfo_pointerx() > obj.winfo_rootx() and \
            obj.winfo_rooty() + obj.winfo_height() > obj.winfo_pointery() > obj.winfo_rooty():

        while len(did) != 0:
            obj.after_cancel(did.pop())

        if len(aid) == 0:
            obj.attributes('-alpha', '0.95')
            aid.append(obj.after(80, lambda: obj.wm_attributes('-alpha', '0.95')))

        while len(killid) != 0:
            obj.after_cancel(killid.pop())

    elif leave:
        obj.update()

        while len(aid) != 0:
            obj.after_cancel(aid.pop())

        if len(did) == 0:
            obj.attributes('-alpha', '0.7')
            did.append(obj.after(80, lambda: obj.wm_attributes('-alpha', '0.7')))
        killid.append(obj.after(timesec * 1000, obj.destroy))


# The MAIN function
def main():
    global texttr, killid
    initrt = tkinter.Tk()
    initrt.attributes('-zoomed', True)  # Maximizing the window for detecting resolution of currently active monitor
    initrt.update()                     # Updating parameters

    ws = initrt.winfo_width() - winwidth - shiftx + initrt.winfo_rootx()  # Calculating position the window along the X axis
    hs = initrt.winfo_rooty() + shifty - 22                               # Calculating position the window along the Y axis
    initrt.destroy()

    root = tkinter.Tk()
    root.geometry('{}x{}+{}+{}'.format(winwidth, winheight, ws, hs))  # Applying new geometry foe the windowroot.overrideredirect(True)
    root.resizable(width=False, height=False)
    root.attributes('-type', 'splash')
    root.attributes('-topmost', '1')
    root.attributes('-alpha', '0.8')
    root.configure(bg=color)
    root.update()

    froo = tkinter.Frame(root, bg=color, relief='groove', borderwidth=1, highlightthickness=0, padx=3, pady=3)
    froo.pack(side='left', expand='yes', fill='both')

    frame = tkinter.Frame(froo, bg=color, relief='flat')
    frame.pack(side='bottom', fill='both')

    but = tkinter.Button(frame, text='Close', bg=color,
                         relief='flat', activebackground=acolor, command=lambda: root.destroy())
    but.configure(borderwidth=0, highlightthickness=0, width=1, font=(font, '10'), padx=10, pady=10)
    but.pack(side='left',fill='x', expand='yes')

    btncp = tkinter.Button(frame, text='Copy to clipboard', bg=color, relief='flat', activebackground=acolor,
                           command=lambda: cpcl(text))
    btncp.configure(borderwidth=0, highlightthickness=0, width=1, font=(font, '10'), padx=10, pady=10)
    btncp.pack(side='right',fill='x', expand='yes')

    img = tkinter.PhotoImage(data=mycat)
    imgalarm = tkinter.PhotoImage(data=alarm)

    txtfr = tkinter.Frame(froo, borderwidth=0, highlightthickness=0, width=1, relief='flat')
    txtfr.pack(side='left',fill='x', expand='yes')

    scroll = tkinter.Scrollbar(txtfr, borderwidth=0, highlightthickness=0, bg=color, activebackground=acolor)
    scroll.pack(side='right', fill='y', expand='yes')

    text = tkinter.Text(txtfr, wrap='word', highlightthickness=0, bg=color, relief='flat', padx=14, pady=10,
                               font=(font, size, style), spacing1=4, spacing2=4, spacing3=4, borderwidth=0)
    text.pack(side='left', expand='yes', fill='both')
    text.config(yscrollcommand=scroll.set)

    if len(texttr) == 0:
        texttr.append('/*Alarm*/ There is nothing to translate!!')

    if len(messg) != 0:
        texttr = ['=== /*Alarm*/ /*Alarm*/ /*Alarm*/ ==='] + messg + ['=== /*Alarm*/ /*Alarm*/ /*Alarm*/ ==='] + texttr

    for i in range(len(texttr)):
        for n in texttr[i].split():
            if n.upper() == 'ESENDJER':
                label = tkinter.Label(image=img, bg=color)
                text.window_create('insert', window=label)

            elif n == '/*Alarm*/':
                label = tkinter.Label(image=imgalarm, bg=color)
                text.window_create('insert', window=label)

            else:
                text.insert('end', '{} '.format(n))

        if i != len(texttr) - 1:
            text.insert('end', '\n')

    root.update()

    killid.append(root.after(timesec*1000, root.destroy))
    root.bind_all('<Enter>', lambda a: onwin(root, False))
    root.bind_all('<Motion>', lambda a: onwin(root, False))
    root.bind('<Leave>', lambda a: onwin(root, True))

    root.mainloop()
    quit(0)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == ('-v' or '--version'):
            print('Hello! YaTrans is the program to translate (using Yandex Translate)')
            print(' * Author:  {}'.format(__author__))
            print(' * License: {}'.format(__license__))
            print(' * Version: {}'.format(__version__))
            quit(0)
        else:
            print('''I don't understand that argument.''')
            print(' * Supported arguments: -v or --version')
            quit(2)
    else:
        main()
