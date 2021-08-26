from typeclasses.objects import Object
from evennia import default_cmds, CmdSet
from evennia.utils.evmenu import get_input

class CmdEmote(default_cmds.CmdPose):
    """
    Strike a pose. 

    Usage:
        pose <pose text>
        pose's <pose text>

    Example:
        pose is standing by the wall, smiling.
        -> others will see:
        Tom is standing by the wall, smiling.

    Describe an action being taken. The pose text will
    automatically begin with your name.
    """

    key = "pose"
    aliases = ["emote", ":"]

    def parse(self):
        """
        Custom parse the cases where the emote
        starts with some special letter, such
        as 's, at which we don't want to separate
        the caller's name and the emote with a
        space.
        """
        args = self.args
        if args and not args[0] in ["'", ",", ":"]:
            args = " %s" % args.strip()
        self.args = args


    def func(self):
        """Hook function"""
        caller = self.caller
        
        if self.args[0] != ":":

            #basic Emote function -- just writes the text into the room
            if not self.args:
                msg = "What do you want to do?"
                self.caller.msg(msg)
            else:
                msg = "%s%s" % (self.caller.name, self.args)
                self.caller.location.msg_contents(text=(msg, {"type": "pose"}), from_obj=self.caller)
        else:
            #preset emote function - check in caller's db for known emotes

            whichemote = self.args[1:].lower()
            if not self.caller.db.knownemotes:
                self.caller.db.knownemotes = {}
            
            emotelist = self.caller.db.knownemotes
        
            if whichemote in emotelist:
                string = emotelist[whichemote]
                if not string[0] in ["'", ","]:
                    string = " " + string
                msg = "%s%s" % (self.caller.name, string)
                self.caller.location.msg_contents(text=(msg, {"type": "pose"}), from_obj=self.caller)
            else:
                caller.msg("You don't yet know how to do that.")

class CmdCreateEmote(default_cmds.MuxCommand):
    """
    Create an emote. Typing this command will enter you into a prompt that will help you create the emote. 
    Syntax : createemote
    Aliases : act, makeemote
    """
    key = "createemote"
    aliases = ["act", "makeemote"]

    def func(self):
        caller = self.caller
        caller.msg("You begin creating a new emote")
        while True:
            emotetext = yield("What would you like others in the room to see? (What you enter will be preceded by your character name or short description)")
            caller.msg("Others in the room will see:")
            caller.msg("|c" + caller.name + " " + emotetext + "|n")
            answer = yield("Is that what you wanted them to see? y/n/cancel")
            answer = answer.lower()
            if answer == "y" or answer == "yes":
                break
            elif answer == "n" or answer == "no":
                continue
            else:
                caller.msg("You entered something other than 'yes' or 'no'. Exiting emote creation.")
                return None
        
        while True:
            keyword = yield("What keyword would you like to trigger this emote? For example, if you use 'jump' as a keyword then typing ::jump will show your new emote to everyone in the room.")
            keyword = keyword.lower()
            if not keyword in caller.db.knownemotes:
                caller.db.knownemotes[keyword] = emotetext
                break
            else:
                answer = yield("You already have an emote registered to that keyword. Would you like to |yselect|n a different keyword or |yreplace|n the existing emote? You can answer with 'select' or 'replace'")
                if answer.lower() == "select":
                    continue
                elif answer.lower() == "replace":
                    caller.db.knownemotes[keyword] = emotetext
                    break
                else:
                    caller.msg("Answer not recognized - exiting emote creation.")


            
        caller.msg("Congratulations! You have created a new emote. Typing ::" + keyword + " will now show the room:")
        caller.msg("\"" + caller.name + " " + emotetext + "\"")

class CmdEmoteList(default_cmds.MuxCommand):
    """
    Lists all of the emotes you currently know. 
    Syntax: listemotes
    Aliases: list emotes, allemotes, emotelist, el
    """

    key = "listemotes"
    aliases = ["list emotes", "allemotes", "emotelist", "el"]

    def func(self):
        caller = self.caller
        emotelist = caller.db.knownemotes
        caller.msg("You know the following emotes:")
        for item in emotelist:
            string = "::" + item + " --> " + emotelist[item]
            caller.msg(string)

class CmdRemoveEmote(default_cmds.MuxCommand):
    """
    Removes an emote from your known emotes.
    Syntax : deleteemote <keyword of emote you wish to delete>
    
    Aliases : forgetemote, deleteemote


    """
    key = "removeemote"
    aliases = ["forgetemote", "deleteemote"]

    def func(self):
        caller = self.caller
        emotelist = caller.db.knownemotes
        if not self.args:
            caller.msg("Syntax: deleteemote <keyword of emote>")
        whichemote = self.args
        if whichemote in emotelist: 
            emotelist.pop(whichemote)
            caller.msg("You have forgotten the emote \"" + whichemote + "\".")
        else:
            caller.msg("You don't know that emote.")

class CmdTeachEmote(default_cmds.MuxCommand):
    """
    Teach an emote to someone else. 
    Usage : teachemote <person> = <keyword of emote>

    """
    key = "teachemote"

    def func(self):
        if not self.args:
            self.caller.msg("Usage : teachemote <person> = <keyword of emote>")
            return None
            
        teacher = self.caller
        student = teacher.location.search(self.lhs)
        if not student:
            teacher.msg("That person doesn't seem to be here.")
            return None
        whichemote = self.rhs
        emotelist = teacher.db.knownemotes
        if not whichemote in emotelist:
            teacher.msg("You don't know that emote.")
            return None

        #callback function to execute on student's answer
        def callback(student, prompt, user_input):
            teacher = student.ndb.teacher
            whichemote = student.ndb.whichemote
            if user_input.lower() in ("y", "yes"):
                student.db.knownemotes[whichemote] = teacher.db.knownemotes[whichemote]
                student.msg("You learn how to " + whichemote + " from" + teacher.name + "!")
                teacher.msg("You teach " + student.name + " how to " + whichemote + "!")
                
            elif user_input.lower() in ("n", "no"):
                student.msg("You decline to learn from " + teacher.name + ".")
                teacher.msg(student.name + " has declined to learn from you.")
                
            else:
                student.msg("That is not a recognized answer. Please indicate 'yes' or 'no'.")
                return True

        teacher.msg("You indicate to " + student.name + " that you would like to teach them how to " + whichemote + ".")
        student.msg(teacher.name + " indicates that they wish to teach you how to |y" + whichemote + "|n.")

        # store reference to teacher and emote temporarily inside student's Character object to pass to the callback. 
        student.ndb.teacher = teacher
        student.ndb.whichemote = whichemote
        get_input(student, "Would you like to learn this? y/n", callback)  
            



class EmoteCmdSet(CmdSet):

    key = "EmoteCmdSet"

    def at_cmdset_creation(self): 
        self.add(CmdEmote())
        self.add(CmdCreateEmote())
        self.add(CmdEmoteList())
        self.add(CmdRemoveEmote())
        self.add(CmdTeachEmote())


