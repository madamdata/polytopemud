from evennia import default_cmds, utils, CmdSet
from evennia.utils.evmenu import EvMenu

class CmdRecall(default_cmds.MuxCommand):
    """

    Return yourself to the Prime Vertex.
    
    Usage : recall

    """
    key = "recall" 
    aliases = ["return", "vertex", "primevertex"]

    def func(self):
        primevertex = utils.search.search_object(True, attribute_name = "isrecall", typeclass = "typeclasses.rooms.Room")[0]
        if not self.caller.location == primevertex:
            
            self.caller.msg("|mYou close your eyes and sidestep this dimension for a split second. \nWhen you open them, space itself seems to have dissolved; you are back at the Prime Vertex.|n")
            self.caller.location.msg_contents(text="{} vanishes with a loud pop and the smell of freshly cut grass.".format(self.caller.name), exclude = self.caller)
            self.caller.location = primevertex
            self.caller.location.msg_contents(text="There is a flash of light and a soft pop of air as {} appears.".format(self.caller.name), exclude = self.caller)
        else: 
            self.caller.msg("You are already at the Prime Vertex!")
            return
    

class CmdNameSelf(default_cmds.MuxCommand):
    """
    Change your own name. Unlike the much more powerful 'name', this only works on yourself. 
    Usage : nameself <new name>
    """
    key = "nameself"
    
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage : nameself <new name>")
        caller.name = self.args
        caller.msg("You have changed your name to {}.".format(caller.name))

class CmdSetMyHome(default_cmds.MuxCommand):
    """
    Set your home location to the current room. Typing 'home' will bring you back to this room.
    """
    key = "setmyhome"
    
    def func(self):
        caller = self.caller
        answer = yield("Would you like to set your current location, {}, as your home? y/n".format(caller.location.name))
        if answer.lower() in ("y", "yes", "yep"):
            caller.home = caller.location
            caller.msg("Your home location has been set to: {}.".format(caller.home.name))
        else:
            caller.msg("You answered no. Your home is still: {}.".format(caller.home.name))

class CmdInventory(default_cmds.MuxCommand):
    """
    view inventory

    Usage:
      inventory
      inv

    Shows your inventory.
    """

    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        """check inventory"""
        items = self.caller.contents
        if not items:
            string = "You are not carrying anything."
        else:
            from evennia.utils.ansi import raw as raw_ansi
            table = self.styled_table(border="header")
            string = ""
            for item in items:
                #check if item is worn. If worn is None (not wearable) or False (not worn) just the name will be displayed. If .db.worn is True, or is a string (custom wearstyle) then "(worn)" is displayed. 
                if item.db.worn in (None, False):
                    string = f"|C{item.name}|n"
                else:
                    string = f"|c{item.name}|n (worn)"

                table.add_row(string,
                              "{}|n".format(utils.crop(raw_ansi(item.db.desc or ""), width=50) or ""))
            string = f"|wYou are carrying:\n{table}"
        self.caller.msg(string)


class CmdBuildMenu(default_cmds.MuxCommand):
    """
    Opens a menu interface for building anything in the world.

    Usage : buildmenu

    """

    key = "buildmenu"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        startnode = "BuildMenuStartNode"
        startnode_input = {}
        if self.args:
            obj = caller.search(self.args)
            if utils.utils.inherits_from(obj, "typeclasses.features.Feature"):
                startnode = "BuildMenuFeatureCentral"
                startnode_input = ("", {"editObject":obj})
        EvMenu(
                caller, 
                "commands.buildmenu",
                startnode = startnode,
                cmdset_mergetype="Replace", cmdset_priority=1,
                auto_quit=True, auto_look=True, auto_help=True,
                cmd_on_exit="look",
                persistent=False,
                startnode_input=startnode_input,
                session=None,
                debug=False,
                )

class CmdConcealObj(default_cmds.MuxCommand):
    """
    Makes an object invisible. Nobody will be able to see it unless they have discovered it first. 
    Usage : conceal <object>

    """
    
    key = "conceal"
    locks = "cmd:perm(Builder)"

    def func(self):
        caller = self.caller
        obj = caller.search(self.args)
        try:
            obj.hide_object()
            caller.msg("You conceal a {}.".format(obj.name))
        except:
            caller.msg("You cannot conceal that.")

class CmdUnconcealObj(default_cmds.MuxCommand):
    """
    Makes a concealed object visible again.  
    Usage : unconceal <object>

    """
    
    key = "unconceal"
    locks = "cmd:perm(Builder)"

    def func(self):
        caller = self.caller
        obj = caller.search(self.args)
        try:
            obj.unhide_object()
            caller.msg("You unconceal a {}.".format(obj.name))
        except:
            caller.msg("You cannot unconceal that.")

        
class PolytopeCharacterCmdSet(CmdSet):
    key = "polytopecharactercmdset"

    def at_cmdset_creation(self):
        self.add(CmdNameSelf())
        self.add(CmdRecall())
        self.add(CmdSetMyHome())
        self.add(CmdInventory())
        self.add(CmdBuildMenu())
        self.add(CmdConcealObj())
        self.add(CmdUnconcealObj())

        
