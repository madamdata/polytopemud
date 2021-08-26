from typeclasses.objects import Object
from typeclasses.characters import Character
from commands.command import Command
from evennia import CmdSet, syscmdkeys, utils



class FeatureCommand(Command):
    
    #key = sysacmdkeys.CMD_NOMATCH
    answer = ""

    def func(self):
        caller = self.caller
        obj = self.obj
        loc = obj.location
        #if it's a character, msg that character only
        if utils.utils.inherits_from(loc, Character):
            loc.location.msg_contents(self.answer)
        else:
            loc.msg_contents(self.answer)

                


class Feature(Object):
    """
    An object meant to be placed in a room. It is not meant to be puppeted but will have commands that are accessible to others in the room.
    """

    feature_command = FeatureCommand
    #locks = "call:canBeSeen()"

    def at_object_creation(self):
        if not self.db.actionlist:
            self.db.actionlist = {"testing" : "1 2 3 4"}
        self.db.callableWhenHidden = False
        self.locks.add("call:canBeSeen() or callableWhenHidden()")

    def create_feature_cmdset(self, **kwargs):
        actionlist = self.db.actionlist
        #create a CmdSet

        cmdset = CmdSet(None)
        cmdset.key = "FeatureCmdSet"
        cmdset.duplicates = True

        for item in actionlist:
            ans = actionlist[item]
            cmd = self.feature_command(
                    key = item.lower(),
                    answer = ans,
                    auto_help = False,
                    locks = str(self.locks)
                    )
            cmd.obj = self
            cmdset.add(cmd)
        return cmdset   

    def add_action(self, key, answer):
        self.db.actionlist[key] = answer
        self.at_cmdset_get(force_init = True)


    def at_cmdset_get(self, **kwargs):
        """
        Called just before cmdsets on this object are requested by the
        command handler. If changes need to be done on the fly to the
        cmdset before passing them on to the cmdhandler, this is the
        place to do it. This is called also if the object currently
        has no cmdsets.

        Keyword Args:
          force_init (bool): If `True`, force a re-build of the cmdset
            (for example to update aliases).

        """

        if "force_init" in kwargs or not self.cmdset.has_cmdset("FeatureCmdSet", must_be_default=True):
            # we are resetting, or no exit-cmdset was set. Create one dynamically.
            self.cmdset.add_default(self.create_feature_cmdset(), permanent=False)



