from evennia import CmdSet
from evennia import default_cmds


class CmdMakeAction(default_cmds.MuxCommand):

    key = "makeaction"

    def func(self):
        obj = self.caller.location.search(self.args)
        trig = yield("trigger?")
        answer = yield("answer?")

class FeatureCmdSet(CmdSet):
    key = "FeatureCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdMakeAction())

