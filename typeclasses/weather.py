# for example in mygame/typeclasses/scripts.py
# Script class is defined at the top of this module

from  typeclasses.scripts import Script
import random

class Weather(Script):
    """
    A timer script that displays weather info. Meant to
    be attached to a room.

    """
    def at_script_creation(self):
        self.key = "weather_script"
        self.desc = "Gives random weather messages."
        self.interval = 45 
        self.persistent = True  # willos survive reload
        self.db.messagelist = []
        self.tags.add("weatherscript")

    def at_repeat(self):
        "called every self.interval seconds."
        sizeoflist=len(self.db.messagelist)
        if sizeoflist > 0:
            rand = random.randrange(0,len(self.db.messagelist))
            weather = self.db.messagelist[rand]
        # send this message to everyone inside the object this
        # script is attached to (likely a room)
            self.obj.msg_contents(weather)

    def add_message(self, newmessage):
        self.db.messagelist.append(newmessage)

    def remove_message(self, messagetoremove):
        self.db.messagelist.remove(messagetoremove)
    
    def remove_by_index(self, indexofmessagetoremove):
        self.db.messagelist.pop(indexofmessagetoremove)

    def set_interval(self, newinterval):
        self.restart(interval=newinterval)
