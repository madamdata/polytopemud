from evennia.utils.evmenu import EvMenu, get_input
from evennia import utils 


quit_option = {
        "key":("(A) abort", "a","abort"),
        "desc":"Exit this menu", 
        "goto":"BuildMenuExitAbort"
        }

def BuildMenuStartNode(caller, raw_string, **kwargs):
    text = "What would you like to make?"
    options = [
                {
                    #don't make the bracketed letters part of the word - this makes it hard for screen readers. 
                     "key": ("(C) clothes", "c", "cl", "clothes"),
                     "desc" : "Design clothes you can wear.",
                     "goto" : "BuildMenuClothesCentral"
                     },
                {
                    "key": ("(F) feature", "f", "feature"),
                    "desc" : "Create a feature in a room that responds to commands.",
                    "goto" : "BuildMenuFeatureCentral"
                    }, 
                {
                    "key": ("(R) room", "r", "room"),
                    "desc" : "Create a new room",
                    "goto" : "BuildMenuRoomNode"
                    }, 
                quit_option
                ]
    return text, options

def BuildMenuClothesInit(caller, raw_string, **kwargs):
    #caller.ndb._menutree.garmentName = None
    text = "What kind of clothing would you like to make? Please enter a name for the new garment."

    options = [{"key" : "_default", 
                "goto": (_set_name)},
            quit_option]
    return text, options

def BuildMenuGetField(caller, raw_string, **kwargs):
    field = kwargs.get("field")
    return_node = kwargs.get("nodeToReturn")
    prompt = kwargs.get("prompt")
    obj = caller.ndb._menutree.obj  
    text = prompt
    options = [{
        "key": "_default",
        "goto": (_setAttrHelper, {"field": field, "nodeToReturn":return_node})
        }]
    #setattr(obj, field, value)
    return text, options

def _setAttrHelper(caller, raw_string, **kwargs):
    field = kwargs.get("field")
    return_node = kwargs.get("nodeToReturn")
    caller.msg("Setting {}.".format(field))
    #store the input in the temporary menutree. The return node is responsible for saving these to the db! It's just easier this way as far as I can tell.
    menutree = caller.ndb._menutree
    setattr(menutree, field, raw_string)
    return return_node
    

def BuildMenuClothesCentral(caller, raw_string, **kwargs):

    menutree = caller.ndb._menutree
    try: 
        obj = menutree.obj
    except:
        obj = None
    if not obj:
        #create a new item of clothing first
        new_obj_lockstring = "control:id({id}) or perm(Admin);delete:id({id}) or perm(Admin)"
        lockstring = new_obj_lockstring.format(id=caller.id)
        obj = utils.create.create_object(
            "typeclasses.objects.Wearable",
            " ",
            caller,
            home=caller,
            #aliases=aliases,
            locks=lockstring,
            report_to=caller,
            ) 
        obj.db.desc = ""
        obj.db.provenance = caller
        menutree.obj = obj
    else:
        obj = menutree.obj
        try:
            obj.name = menutree.name
        except:
            pass
        try:
            obj.db.desc = menutree.desc
        except:
            pass

    name = obj.name
    desc = obj.db.desc
    text = "Garment name: {} \nDescription: {} \n".format(name, desc)

    options = [{
        "key": ("(n) name", "n"),
        "desc": "Set the name of the object.",
        "goto": ("BuildMenuGetField", 
            {
            "field" : "name", 
            "nodeToReturn":"BuildMenuClothesCentral",
            "prompt":"Please enter a name:"
            })},
                {
        "key": ("(d) desc", "d"), 
        "desc": "Set the description of the object.",
        "goto": ("BuildMenuGetField", {
            "field" : "desc", 
            "nodeToReturn":"BuildMenuClothesCentral",
            "prompt":"Please enter a description:" 
            })},
                {
        "key": ("(c) confirm", "c"), 
        "goto": "BuildMenuExitConfirm"},
                {
        "key": ("(a) abort", "a"), 
        "goto": "BuildMenuExitAbort"}
                ]
    return text, options

def BuildMenuGetTriggers(caller, raw_string, **kwargs):
    #if nothing else triggers, return to prev node
    text = "Setting trigger command and response..."
    options = [{"key":"_default", "goto":"BuildMenuFeatureCentral"}]
    try:
        trig = caller.ndb._menutree.trig
    except:
        trig = None
    try: 
        ans = caller.ndb._menutree.ans
    except:
        ans = None
    if not trig:
        text = "Please enter a trigger command:"
        options = [{
            "key":"_default",
            "goto":(_setAttrHelper, {"field":"trig", "nodeToReturn": "BuildMenuGetTriggers"}) 
            }]
    elif not ans:
        text = "Please enter a response to the trigger command:"
        options = [{
            "key":"_default",
            "goto":(_setAttrHelper, {"field":"ans", "nodeToReturn": "BuildMenuFeatureCentral"}) 
            }]

    return text, options

def BuildMenuRemoveTriggers(caller, raw_string, **kwargs):
    actionlist = caller.ndb._menutree.obj.db.actionlist
    actionlistkeylist = list(actionlist.keys())
    text = "Please specify the number of the trigger you would like to remove.\n"
    table = utils.evtable.EvTable("#", "Triggers", "Responses", table = [[], [], []])
    for index, item in enumerate(actionlistkeylist):
        table.add_row(index, item, actionlist[item])
    #print the table to the text variable for output
    for item in table.get():
        text += item + "\n"
    options = [{
        "key" : "_default",
        "goto": (_removeTrigsHelper)
        }]
    return text, options

def _removeTrigsHelper(caller, raw_string, **kwargs):
    actionlist = caller.ndb._menutree.obj.db.actionlist
    try:
        trigToRemove = int(raw_string)
        actionlist.pop(list(actionlist.keys())[trigToRemove])
        nodeToReturn = "BuildMenuFeatureCentral"
    except ValueError:
        caller.msg("You did not enter a valid number. Please try again.")
        nodeToReturn = "BuildMenuRemoveTriggers"
    return nodeToReturn


def BuildMenuFeatureCentral(caller, raw_string, **kwargs):
    menutree = caller.ndb._menutree
    try: 
        #get a stored object from the menutree
        obj = menutree.obj
    except:
        #if not on the menutree, check to see if an object was provided in the kwargs. This happpens if the "buildmenu" command is called with an argument, in order to edit an object. 
        #returns None if editObject is not a key in kwargs, so the below if statement will trigger.
        obj = kwargs.get("editObject")
        #store whatever's found on the menutree.
        if obj:
            if not (obj.access(caller, "edit") or obj.access(caller, "control")):
                caller.msg("Sorry, you may not edit this object.")
                return "", []
        menutree.obj = obj
        #set a flag if we are editing an external object. This ensures the object is not deleted on abort. 
        menutree.editMode = True
    if not obj:
        #create a new item of clothing first
        new_obj_lockstring = "control:id({id}) or perm(Admin);delete:id({id}) or perm(Admin)"
        lockstring = new_obj_lockstring.format(id=caller.id)
        obj = utils.create.create_object(
            "typeclasses.features.Feature",
            " ",
            caller,
            home=caller,
            #aliases=aliases,
            locks=lockstring,
            report_to=caller,
            ) 
        obj.db.desc = ""
        obj.db.provenance = caller
        menutree.obj = obj
        menutree.editMode = False

    #if there is temporary name or description in the menutree from the GetField node, copy it into the object.
    try:
        obj.name = menutree.name
    except:
        pass
    try:
        obj.db.desc = menutree.desc
    except:
        pass

    #if there is a temporary trigger and response from the GetTriggers node, add them to the object.
    try:
        trig, ans = (caller.ndb._menutree.trig, caller.ndb._menutree.ans)
        if trig and ans:
            obj.add_action(trig, ans)
            caller.ndb._menutree.trig = None
            caller.ndb._menutree.ans = None
    except:
        pass

    name = obj.name
    desc = obj.db.desc
    actionlist = obj.db.actionlist
    text = "Feature name: {} \nDescription: {} \n".format(name, desc)
    table = utils.evtable.EvTable("Triggers", "Responses", table = [[], []])
    for item in actionlist:
        table.add_row(item, actionlist[item])
    #print the table to the text variable for output
    for item in table.get():
        text += item + "\n"

    options = [               
            {
        "key": ("(n) name", "n"),
        "desc": "Set the name of the object.",
        "goto": ("BuildMenuGetField", 
            {
            "field" : "name", 
            "nodeToReturn":"BuildMenuFeatureCentral",
            "prompt":"Please enter a name:"
            })},
                {
        "key": ("(d) desc", "d"), 
        "desc": "Set the description of the object.",
        "goto": ("BuildMenuGetField", {
            "field" : "desc", 
            "nodeToReturn":"BuildMenuFeatureCentral",
            "prompt":"Please enter a description:" 
            })},
                {
        "key": ("(t) triggers", "t", "triggers"), 
        "desc": "Set a trigger command and a response",
        "goto": "BuildMenuGetTriggers"},
                {
        "key": ("(r) remove triggers", "r", "remove"), 
        "desc": "Set a trigger command and a response",
        "goto": "BuildMenuRemoveTriggers" 
            },
            {
        "key": ("(c) confirm", "c"), 
        "goto": "BuildMenuExitConfirm"},
            {
        "key": ("(a) abort", "a"), 
        "goto": "BuildMenuExitAbort"}
            ]
    return text, options


def BuildMenuExitAbort(caller, raw_string, **kwargs):
    text = "Aborting."
    #if in edit mode, just quit (don't delete the objct!!.
    if caller.ndb._menutree.editMode:
        return text, []

    try:
        caller.ndb._menutree.obj.delete()
    except:
        pass    
    return text, []
    
def BuildMenuExitConfirm(caller, raw_string, **kwargs):
    text = "You carefully create a {}.".format(caller.ndb._menutree.obj.name)
    return text, []
    
        
    
def BuildMenuObjectNode(caller, raw_string, **kwargs):
    text = "Sorry, that function is still in development. Stay tuned!"
    options = [quit_option]
    return text, options

def BuildMenuRoomNode(caller, raw_string, **kwargs):
    text = "Sorry, that function is still in development. Stay tuned!"
    options = [quit_option]
    return text, options
