from evennia import default_cmds, CmdSet, utils

class CmdWear(default_cmds.MuxCommand):
    """
    Wear an object.
    syntax: Wear <object>
    syntax: Wear <object> <style>

    e.g. >> wear t-shirt tucked into her pants
        others see: <character> is wearing:
                    A t-shirt tucked into her pants.
    """

    key = "wear"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement command"""

        caller = self.caller
        if not self.args:
            caller.msg("What would you like to wear?")
            return

        # Because the WEAR command by definition looks for items
        # in inventory, call the search function using location = caller
        clothing = caller.search(
            self.arglist[0],
            location=caller,
            nofound_string="You aren't carrying %s." % self.args,
            multimatch_string="You carry more than one %s:" % self.args,
        )
        wearstyle = True
        if not clothing.is_typeclass("objects.Wearable", exact=False):
            self.caller.msg("You cannot wear that.")
            return

        if not clothing:
            return

        if len(self.arglist) > 1:  # If wearstyle arguments given
            wearstyle_list = self.arglist  # Split arguments into a list of words
            del wearstyle_list[0]  # Leave first argument (the clothing item) out of the wearstyle
            wearstring = " ".join(
                str(e) for e in wearstyle_list
            )  # Join list of args back into one string
            wearstyle = wearstring

        clothing.wear(caller, wearstyle)
        caller.msg("You wear %s." % (clothing.name,))
        caller.location.msg_contents("%s wears %s." % (caller.name, clothing.name), exclude=caller)
            # Call the object script's at_drop() method.

class CmdRemove(default_cmds.MuxCommand):
    """
    Takes off an item of clothing.
    Usage:
       remove <obj>
    Removes an item of clothing you are wearing. You can't remove
    clothes that are covered up by something else - you must take
    off the covering item first.
    """

    key = "remove"
    help_category = "clothing"
    arg_regex = r"\s.+"

    def func(self):
        """
        This performs the actual command.
        """
        clothing = self.caller.search(self.args, candidates=self.caller.contents)
        if not clothing:
            self.caller.msg("Thing to remove must be carried or worn.")
            return
        if not clothing.db.worn:
            self.caller.msg("You're not wearing that!")
            return
        clothing.remove(self.caller)        
        self.caller.msg("You remove %s." % (clothing.name))


class CmdTailor(default_cmds.MuxCommand):
    """
    Starts an easy-to-use dialogue for creating an item of clothing.
    Syntax: tailor
    """
    key = "tailor"
    help_category = "clothing"
    #arg_regex = r"\s.+"
    new_obj_lockstring = "control:id({id}) or perm(Admin);delete:id({id}) or perm(Admin)"


    def func(self):

        caller = self.caller
        caller.msg("You begin creating a new item of clothing.")

        while True:
            name = yield("What will it be called? (This is what others will see when they look at you, and when you pick it up, drop it, wear it, or remove it.)")
            caller.msg(name)
            answer = yield("Are you happy with this name? y/n")
            if answer.lower() == "y" or answer.lower() == "yes":
                break
            else:
                continue

        while True:
            desc = yield("What does it look like? (This is what you will see when you look at it, and what others will see if you show it off to them.)")
            caller.msg(name)
            caller.msg("\""+desc+"\"")
            answer = yield("Are you happy with this look? y/n")
            if answer.lower() == "y" or answer.lower()=="yes":
                break
            else:
                continue

        caller.msg("You carefully create " + name + ".")
        #generate lockstring with the creator's ID
        lockstring = self.new_obj_lockstring.format(id=caller.id)
        utils.create.create_object(
                typeclass="typeclasses.objects.Wearable",
                key=name,
                location=caller,
                home=caller,
                permissions=None,
                locks=lockstring,
                aliases=None,
                tags=None,
                attributes=[
                    ("provenance",caller),
                    ("desc", desc)
                    ]
                ) 

class CmdShowoff(default_cmds.MuxCommand):
    """
    Show off your clothes to everyone in the room.

    Usage : showoff <item of clothing>
    """
    key = "showoff"
    aliases = ["display", "model"]
    
    def func(self):
        caller = self.caller
        item = caller.search(self.args, location = caller)
        if not item:
            caller.msg("You don't have that.")
        else: 
            caller.location.msg_contents("{} shows off |y{}|n:".format(caller.name, item.name))
            caller.location.msg_contents(item.db.desc)



class ClothingCmdSet(CmdSet):
    key = "ClothingCmdSet"
    def at_cmdset_creation(self):
        self.add(CmdWear())
        self.add(CmdRemove())
        self.add(CmdTailor())
        self.add(CmdShowoff())
