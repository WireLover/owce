import threading
from threading import Event

class event_callbackdata:

      def __init__(self, func, args, kwargs):
            # print("guiData: " + str(args))
            # print("guiData: " + str(kwargs))

            self.func = func
            self.args = args
            self.kwargs = kwargs
            self.result = None
            self.event = Event()