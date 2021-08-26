"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from evennia.utils import list_to_string
from typeclasses.objects import get_worn_clothes, Object

class Character(DefaultCharacter, Object):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """
    
    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.
        Args:
            looker (Object): Object doing the looking.
        Notes:
            The name of every clothing item carried and worn by the character
            is appended to their description. If the clothing's db.worn value
            is set to True, only the name is appended, but if the value is a
            string, the string is appended to the end of the name, to allow
            characters to specify how clothing is worn.
        """
        if not looker:
            return ""
        # get description, build string
        string = "|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc
        worn_string_list = []
        clothes_list = get_worn_clothes(self, exclude_covered=True)
        # Append worn, uncovered clothing to the description
        for garment in clothes_list:
            # If 'worn' is True, just append the name
            if garment.db.worn is True:
                worn_string_list.append(garment.name)
            # Otherwise, append the name and the string value of 'worn' which will bethe wearstyle
            elif garment.db.worn:
                worn_string_list.append("%s %s" % (garment.name, garment.db.worn))
        if desc:
            string += "%s" % desc
        # Append worn clothes.
        if worn_string_list:
            #string += "|/|/%s is wearing %s." % (self, list_to_string(worn_string_list))
            string += "|/|/%s is wearing: \n" % (self)
            for item in worn_string_list:
                string += item
                string += "\n"
        else:
            string += "|/|/%s is not wearing anything." % self
        return string


