from typeclasses.weather import Weather
from evennia import default_cmds, utils, CmdSet


def displayWeather(weatherObj, caller):
    caller.msg("These are the weather messages in this room. The interval between messages is " + str(weatherObj.interval) + " seconds.")
            
    for num, item in enumerate(weatherObj.db.messagelist):
        caller.msg(str(num) + " : " + item)

class CmdAddWeather(default_cmds.MuxCommand):
    """
    Create or add to a weather script in the current room. If there is no current weather script, one will be created; otherwise a new message will be added to the current weather object for the room.

    The messages stored in the weather script will be played into the room at every interval; the duration of each interval can be set with the command "weatherinterval"

    syntax: addweather <message> 
     
    """

    key = "addweather"
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        room = self.caller.location
        roomscripts = room.scripts.all()
        scriptlist = list(filter(lambda item: utils.inherits_from(item, "typeclasses.weather.Weather"), roomscripts))
        if len(scriptlist) > 0:
            weather = scriptlist[0]
            weather.add_message(self.args)
            caller.msg("Adding \"" + self.args + "\" " +"to weather messages.")
        else:
            caller.msg("No weather script found in this room. Making a new one...")
            room.scripts.add("weather.Weather")
                    
            weather = room.scripts.all().get(db_typeclass_path="typeclasses.weather.Weather")
            weather.add_message(self.args)
            caller.msg("Adding \"" + self.args + "\" " +"to weather messages.")

class CmdWeatherInterval(default_cmds.MuxCommand):
    """
    Change how often the weather messages in this room will display. 

    Syntax: weatherinterval <interval between messages in seconds>
    """
    key = "weatherinterval"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        room = caller.location
        weather = room.scripts.all().get(db_typeclass_path="typeclasses.weather.Weather")
        weather.set_interval(int(self.args))
        caller.msg("Setting the interval of the weather in this room to " + self.args + " seconds.")

class CmdWeatherList(default_cmds.MuxCommand):
    """
    List all the weather messages for this room.
    """
    

    key = "weatherlist"
    aliases = ["wl", "list weather"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        room = caller.location
        weather = room.scripts.all().get(db_typeclass_path="typeclasses.weather.Weather")
        if weather:
            displayWeather(weather, caller)

class CmdRemoveWeather(default_cmds.MuxCommand):
    """
    Remove a weather message from the current list of weather messages. 
    Syntax: removeweather <index number of weather message>
    Use the command "weatherlist" to get the index number of the message you want to delete. 
    """
    key = "removeweather"
    locks = "cmd:all()"
    arg_regex = r"\s.+"

    def func(self):
        caller = self.caller
        room = caller.location
        index = int(self.args)
        weather = room.scripts.all().get(db_typeclass_path="typeclasses.weather.Weather")
        caller.msg("\"" + weather.db.messagelist[index]+ "\" has been removed from the list of weather messages in this room.")
        weather.remove_by_index(index)


class WeatherCmdSet(CmdSet):
    key = "WeatherCmdSet"
    def at_cmdset_creation(self):
        self.add(CmdAddWeather())
        self.add(CmdWeatherInterval())
        self.add(CmdWeatherList())
        self.add(CmdRemoveWeather())
