"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
import time
import inflect
from collections import defaultdict

from django.conf import settings

from evennia.typeclasses.models import TypeclassBase
from evennia.typeclasses.attributes import NickHandler
from evennia.objects.manager import ObjectManager
from evennia.objects.models import ObjectDB
from evennia.scripts.scripthandler import ScriptHandler
from evennia.commands import cmdset, command
from evennia.commands.cmdsethandler import CmdSetHandler
from evennia.utils import create
from evennia.utils import search
from evennia.utils import logger
from evennia.utils import ansi
from evennia.utils.utils import (
    class_from_module,
    variable_from_module,
    lazy_property,
    make_iter,
    is_iter,
    list_to_string,
    to_str,
)
from django.utils.translation import gettext as _


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    def at_object_creation(self):
        self.locks.add("edit:perm(Builder)")

    def return_appearance(self, looker, **kwargs):
        """
        This formats a description. It is the hook a 'look' command
        should call.
        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        if not looker:
            return ""
        # get and identify all objects
        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
        exits, users, things = [], [], defaultdict(list)
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(key)
            elif con.has_account:
                users.append("|c%s|n" % key)
            else:
                # things can be pluralized
                things[key].append(con)
        # get description, build string
        string = "\n   |c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc
        if desc:
            string += "|x%s|n\n" % desc
        if exits:
            string += "\n|wExits:|n " + list_to_string(exits)
        if users or things:
            # handle pluralization of things (never pluralize users)
            thing_strings = []
            for key, itemlist in sorted(things.items()):
                nitem = len(itemlist)
                if nitem == 1:
                    key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
                else:
                    key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][
                        0
                    ]
                thing_strings.append(key)

            string += "\n|wYou see:|n " + list_to_string(users + thing_strings)

        return string
