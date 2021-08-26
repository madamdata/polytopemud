from typeclasses.objects import Object
from typeclasses.characters import Character
from evennia import default_cmds

class NPC(Character):
    """
    Generic NPC type
    """
    def at_object_creation(self):
        "This is called only when object is first created"
        self.cmdset.add_default(default_cmds.CharacterCmdSet)
        self.locks.add("puppet:all();call:false()")
        self.db.desc = "This is a general purpose mobile"
        self.db.dialogue ={}

    def at_heard_say(self, message, from_obj):
        """
        A simple listener and response. This makes it easy to change for
        subclasses of NPCs reacting differently to says.

        """
        # message will be on the form `<Person> says, "say_text"`
        # we want to get only say_text without the quotes and any spaces
        message = message.split('says, ')[1].strip(' "').lower()
        """

        if message in self.db.dialogue:

            #return "%s said: '%s'" % (from_obj, message)
            return self.db.dialogue[message]
        """
        for item in self.db.dialogue:
            if item in message:
                return self.db.dialogue[item]
    
    def msg(self, text=None, from_obj=None, **kwargs):
        "Custom msg() method reacting to say."

        if from_obj != self:
            # make sure to not repeat what we ourselves said or we'll create a loop
            try:
                # if text comes from a say, `text` is `('say_text', {'type': 'say'})`
                say_text, is_say = text[0], text[1]['type'] == 'say'
            except Exception:
                is_say = False
            if is_say:
                # First get the response (if any)
                response = self.at_heard_say(say_text, from_obj)
                # If there is a response
                if response != None:
                    # speak ourselves, using the return
                    self.execute_cmd("say %s" % response)   
    
        # this is needed if anyone ever puppets this NPC - without it you would never
        # get any feedback from the server (not even the results of look)
        super().msg(text=text, from_obj=from_obj, **kwargs) 

