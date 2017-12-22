from future import standard_library
standard_library.install_aliases()
from builtins import filter
from builtins import map
from builtins import str
from builtins import range
from builtins import object
try:  # Python 3
    from tkinter import *
except:  # Python 2
    from tkinter import *

from SimPy.SimulationStep import now,Globals


import warnings
warnings.warn('This module be removed in SimPy 3.', DeprecationWarning)


# Creates and controls the GUI of the program
class GUIController(object):

    def __init__(self):
        self.root = Tk()
        self.root.withdraw()

        self.saveNextEvent()

        self.eventWin = EventWindow(self)
        self.wlist = []
        self.plist = []
        self.rlist = []

    # Adds a new Window to the GUI
    def addNewWindow(self,obj,name,hook):
        self.wlist += [GenericWindow(obj,hook,self,name)]

    # Adds a new Process to the GUI
    def addNewProcess(self,obj,name,hook):
        self.plist += [ProcessWindow(obj,hook,self,name)]

    # Adds a new Resource to the GUI
    def addNewResource(self,obj,name,hook):
        self.rlist += [ResourceWindow(obj,hook,self,name)]

    # Updates all the windows currently up
    def updateAllWindows(self):

        for w in self.wlist: w.update()
        for p in self.plist: p.update()
        for r in self.rlist: r.update()
        if self.eventWin.window: self.eventWin.update()

        self.organizeWindows()

        self.saveNextEvent()

    # removes all instances of window in lists
    def removeWindow(self, w):
        f = lambda win: win is not w
        self.wlist = list(filter(f, self.wlist))
        self.plist = list(filter(f, self.plist))
        self.rlist = list(filter(f, self.rlist))

    # save next event to be run
    def saveNextEvent(self):
        #from SimPy.SimulationTrace import _e

        tempList=[]
        tempList[:]=Globals.sim._timestamps
        tempList.sort()

        for ev in tempList:

            # return only event notices which are not cancelled
            if ev[3]: continue

            # save next event
            self.nextEvent = ev
            return

        self.nextEvent = (None,None,None,None)

    def organizeWindows(self):

        # event window
        eventWindowHeight = 0

        # only organize event window only if it exists
        if self.eventWin.window:
            eventWindowHeight = 40 + 20 * self.eventWin.table.size()
            self.eventWin.setWindowSize(500, eventWindowHeight ,20,40)

        # generic windows
        count = -1

        for win in self.wlist:
            count += 1

            (w,h,x,y) = win.getWindowSize()
            win.setWindowSize(w, h, 20, 40 + eventWindowHeight + 40 )

            eventWindowHeight += h + 40

        # process windows
        xCount = -1
        yCount = 0

        for p in self.plist:
            xCount += 1

            yCoord = 40 + 150 * xCount
            xCoord = 550 + 210 * yCount

            p.setWindowSize(200,120, xCoord, yCoord )

            if yCoord >= 600:
                xCount = -1
                yCount += 1

        # resource windows
        count = -1
        for r in self.rlist:
            count += 1

            windowHeight = 0
            windowHeight += 20 # capacity title
            windowHeight += 105 # empty table sizes

            windowHeight += (r.activeT.size() + r.waitT.size()) * 17 # add size for each row

            r.setWindowSize(200, windowHeight , 20 + 220 * count , 40 + eventWindowHeight + 40)



# Creates a basic window that shows a user made hook.
class GenericWindow(object):

    def __init__(self, obj, hook, guiCtrl, title=None):
        self.window = Toplevel()
        self.window.protocol("WM_DELETE_WINDOW", self._destroyWindow)
        self.obj = obj
        self.hook = hook
        self.guiCtrl = guiCtrl
        if not title:
            self.title = "%s%s" % (type(obj),id(obj))
        else:
            self.title = title
        self.initGUI()


    def setWindowSize(self,w,h,x,y):
        newG = "%dx%d+%d+%d" % (w,h,x,y)
        self.window.geometry(newG)

    def setWindowOrigin(self,x,y):
        (w,h,xx,yy) = self.getWindowSize()
        newG = "%dx%d+%d+%d" % (w,h,x,y)
        self.window.geometry(newG)

    def getWindowSize(self):
        g = self.window.geometry()
        return [int(i) for i in g.replace('+','x').split('x')]

    def _destroyWindow(self):
        self.window.destroy()
        self.window = None
        self.guiCtrl.removeWindow(self)

    # Creates the window
    def initGUI(self):
        self.window.title(self.title)
        txt = self.hook()
        if txt != "": txt += '\n'
        self.hookTxt = Label(self.window,text=txt,justify=LEFT)
        self.hookTxt.pack()

    # Updates the window
    def update(self):
        txt = self.hook()
        if txt != "": txt += '\n'
        self.hookTxt["text"] = txt

# Class that creates the event window for the simulation that
# displays the time and event.
class EventWindow(GenericWindow):

    def __init__(self, guiCtrl):
        self.window = Toplevel()
        self.window.protocol("WM_DELETE_WINDOW", self._destroyWindow)
        self.guiCtrl = guiCtrl
        self.initGUI()

    # Creates the initial window using a two column window with a
    # status bar on the bottom
    def initGUI(self):
        self.window.title("Event List")
        # Creates the table
        self.table = MultiListbox(self.window,(('', 1), ('Time',15),
                                   ('Process',20),('Next Line',5)))
        # Adds the status bar to display the current simulation time
        self.status = StatusBar(self.window)
        self.status.pack(side=TOP, fill=X)

        self.update()

    # Updates the window
    def update(self):
        self.updateETable()
        self.updateStatus()

    # Updates the status bar
    def updateStatus(self):
        self.status.set("  Current Time: %s",now())

    # Updates the table
    def updateETable(self):
        #from SimPy.SimulationStep import _e
        self.table.delete(0,self.table.size())

        tempList=[]
        tempList[:]=Globals.sim._timestamps
        tempList.sort()

        ev = self.guiCtrl.nextEvent

        nextLine = 0
        if( ev[2] ):
            if( ev[2]._nextpoint ):
                nextLine = ev[2]._nextpoint.gi_frame.f_lineno

        if ev[0]:
            self.table.insert(END,('  >>',
                   str(ev[0]), ev[2].name, nextLine ))

        count = -1
        for ev in tempList:

            # return only event notices which are not cancelled
            if ev[3]: continue

            count += 1

            currentEvent = ''
            #if count == 0 and now() == ev[0]:
            #	currentEvent = '  >>'

            nextLine = 0
            if( ev[2] ):
                if( ev[2]._nextpoint ):
                    nextLine = ev[2]._nextpoint.gi_frame.f_lineno

            self.table.insert(END,(currentEvent,
                       str(ev[0]), ev[2].name, nextLine ))

        self.table.pack(expand=YES,fill=BOTH)

# Creates a Process Window that shows the status, Next Event time,
# if the Process is currently interupted, and an optional user hook.
class ProcessWindow(GenericWindow):

    def __init__(self, obj, hook, guiCtrl, name):
        self.proc = obj
        if name:
            obj.name = name
        GenericWindow.__init__(self, obj, hook, guiCtrl, "Process")

    # Initializes the window
    def initGUI(self):
        Label(self.window,text="%s" % (self.proc.name)).pack()
        # Creates the table
        self.table = MultiListbox(self.window,((None,10),(None,15)))
        self.status = StatusBar(self.window)
        self.status.pack(side=BOTTOM, fill=X)

        GenericWindow.initGUI(self)
        self.setWindowSize(0,0,-1000,-1000)

        self.update()

    # Updates the window
    def update(self):

        # If the process has been terminated close the window
        if self.proc.terminated():
            self._destroyWindow()
            return

        if self.isRunning():
            self.status.label["text"] = "Running!"
            self.status.label["fg"] = "red"#"green"
        else:
            self.status.label["text"] = ""
            self.status.label["fg"] = "white"

        self.table.delete(0,self.table.size())

        if self.proc.active() == False:
            status = "Passive"
        else:
            status = "Active"

        if self.proc._nextTime:
            nextEvent = self.proc._nextTime
        else:
            nextEvent = ""

        if self.proc.interrupted() == True:
            interrupted = "True"
        else:
            interrupted = "False"

        self.table.insert(END,("  Status:", status))
        self.table.insert(END,("  Next Event:", nextEvent))
        self.table.insert(END,("  Interrupted:", interrupted ))

        self.table.pack(expand=YES,fill=BOTH)

        GenericWindow.update(self)

    def isRunning(self):
        return self.guiCtrl.nextEvent[2] is self.proc

# Creates a Resource Window that displays the capacity, waitQ,
# activeQ and an optional user hook
class ResourceWindow(GenericWindow):

    def __init__(self,obj,hook,guiCtrl,name):
        self.resource = obj
        if name:
            obj.name = name
        GenericWindow.__init__(self,obj,hook, guiCtrl,"Resource")

    # Initializes the window with the two tables for the waitQ and activeQ
    def initGUI(self):
        Label(self.window,text="%s\tCapacity: %d" % (self.resource.name,self.resource.capacity)).pack()

        self.activeT = MultiListbox(self.window,(('#',5),('ActiveQ',20)))
        self.waitT = MultiListbox(self.window,(('#',5),('WaitQ',20)))
        self.updateQTables()

        GenericWindow.initGUI(self)
        self.setWindowSize(0,0,-1000,-1000)

    # Updates the window
    def update(self):
        GenericWindow.update(self)
        self.updateQTables()

    # Updates the waitQ and activeQ tables
    def updateQTables(self):
        self.activeT.delete(0,END)
        self.waitT.delete(0,END)
        # Update the activeQ
        for i in range(len(self.resource.activeQ)):
            col1 = '%d' % (i+1)
            col2 = self.resource.activeQ[i].name
            self.activeT.insert(END,("   " + col1,col2))
        # Update the waitQ
        for i in range(len(self.resource.waitQ)):
            col1 = '%d' % (i+1)
            col2 = self.resource.waitQ[i].name
            self.waitT.insert(END,("   " + col1,col2))

        self.activeT.pack(expand=YES,fill=BOTH)
        self.waitT.pack(expand=YES,fill=BOTH)
        self.window.update()

# A class that creates a multilistbox with a scrollbar
class MultiListbox(Frame):
    def __init__(self, master, lists):
        Frame.__init__(self, master)
        self.lists = []
        for l,w in lists:
            frame = Frame(self); frame.pack(side=LEFT, expand=YES, fill=BOTH)

            if l is None:
                None
            elif l is '':
                Label(frame, text='', borderwidth=1, relief=FLAT).pack(fill=X)
            else:
                Label(frame, text=l, borderwidth=1, relief=SOLID).pack(fill=X)

            lb = Listbox(frame, width=w, height=0, borderwidth=0, selectborderwidth=0,
                 relief=FLAT, exportselection=FALSE)
            lb.pack(expand=YES, fill=BOTH)
            self.lists.append(lb)
        frame = Frame(self); frame.pack(side=LEFT, fill=Y)
        Label(frame, borderwidth=1, relief=RAISED).pack(fill=X)
        sb = Scrollbar(frame, orient=VERTICAL, command=self._scroll)
        sb.pack(expand=YES, fill=Y)
        self.lists[0]['yscrollcommand']=sb.set

    def _select(self, y):
        row = self.lists[0].nearest(y)
        self.selection_clear(0, END)
        self.selection_set(row)
        return 'break'

    def _button2(self, x, y):
        for l in self.lists: l.scan_mark(x, y)
        return 'break'

    def _b2motion(self, x, y):
        for l in self.lists: l.scan_dragto(x, y)
        return 'break'

    def _scroll(self, *args):
        for l in self.lists:
            l.yview(*args)

    def curselection(self):
        return self.lists[0].curselection()

    def delete(self, first, last=None):
        for l in self.lists:
            l.delete(first, last)

    def get(self, first, last=None):
        result = []
        for l in self.lists:
            result.append(l.get(first,last))
        if last: return list(map(*[None] + result))
        return result

    def index(self, index):
        self.lists[0].index(index)

    def insert(self, index, *elements):
        for e in elements:
            i = 0
            for l in self.lists:
                l.insert(index, e[i])
                i = i + 1

    def size(self):
        return self.lists[0].size()

    def see(self, index):
        for l in self.lists:
            l.see(index)

    def selection_anchor(self, index):
        for l in self.lists:
            l.selection_anchor(index)

    def selection_clear(self, first, last=None):
        for l in self.lists:
            l.selection_clear(first, last)

    def selection_includes(self, index):
        return self.lists[0].selection_includes(index)

    def selection_set(self, first, last=None):
        for l in self.lists:
            l.selection_set(first, last)

# Creates a statusbar
class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()
