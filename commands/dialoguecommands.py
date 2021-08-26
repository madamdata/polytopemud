from evennia import default_cmds, CmdSet
from evennia.commands.default.building import ObjManipCommand
from commands.command import Command

class CmdDialogueCreate(ObjManipCommand):
    """
    Create a trigger string and response for an NPC.
    Syntax --- dialoguecreate <target NPC> = <trigger phrase> , <response>

    """

    help_category = "Builder"
    key = "dialoguecreate"

    def func(self):
        "This actually does things" 
        if not self.args:
            self.caller.msg("You didn't enter anything!")           
        else:
            target = self.lhs_objs[0]["name"]
            trigger = self.rhs_objs[0]["name"].lower()
            aliases = self.rhs_objs[0]["aliases"]
            response = self.rhs_objs[1]["name"]
            self.caller.search(target).db.dialogue.update({trigger:response})
            print(target)
            print(trigger)
            print(response)

class CmdDialogueDelete(ObjManipCommand):
    """
    Delete a trigger string and response for an NPC
    Usage --- dialoguedelete <target NPC> = <trigger phrase to delete>
    """

    help_category = "Builder"
    key = "dialoguedelete"

    def func(self):
        if not self.args:
            self.caller.msg("You didn't enter anything!")
        else:
            target = self.lhs_objs[0]["name"]
            trigger = self.rhs_objs[0]["name"].lower()
            self.caller.search(target).db.dialogue.pop(trigger)


class CmdDialogueClear(ObjManipCommand):
    """
    Delete all dialogue for an NPC
    """

    help_category = "Builder"
    key = "dialogueclear"

    def func(self):
        target = self.lhs_objs[0]["name"]
        self.caller.search(target).db.dialogue = {}
        self.caller.msg("Dialogue cleared for {0}.".format(target))
        
class CmdDialogueShow(ObjManipCommand):

    help_category = "Builder"
    key = "dialogueshow"

    def func(self):
        target = self.lhs_objs[0]["name"]
        dialoguelist = self.caller.search(target).db.dialogue
        self.caller.msg("Displaying dialogue for {0} :".format(target))
        for item in dialoguelist:
            self.caller.msg(item + " : " + dialoguelist[item])


class DialogueCmdSet(CmdSet):
    key = "DialogueCmdSet"
    def at_cmdset_creation(self):
        self.add(CmdDialogueCreate())
        self.add(CmdDialogueDelete())
        self.add(CmdDialogueClear())
        self.add(CmdDialogueShow())
