
import gtk
import time
import threading

guilock = threading.RLock()
go = True

def shutdown():
    global go
    go = False

def main(onexit=None):
    try:
        while go:
            guilock.acquire()
            gtk.main_iteration_do(False)
            skipsleep = gtk.events_pending()
            guilock.release()
            if not skipsleep:
                time.sleep(0.01)
    finally:
        if onexit != None:
            onexit()

