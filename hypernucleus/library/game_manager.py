from .paths import Paths
from ..model import GAME, DEP
from ..model.ini_manager import INIManager
from ..model.json_model import JsonModel
from os.path import join
from subprocess import Popen, call
import os
import sys

class GameManager:
    """
    Manages Game Processes
    """
    gamelist = {}
    
    def __init__(self):
        self.apppath = sys.argv[0]
    
    def execute_game(self, game_name):
        """
        Run the game itself.
        """
        p = Paths()
        
        # Load XML File
        ini_data = INIManager()
        xml_data = JsonModel(ini_data.get_xml_url())
         
        # Change directory to the game's folder
        os.chdir(join(p.games, game_name))
        
        # Get various needed data
        game_ins_ver = ini_data.get_installed_version(game_name)
        game_module_type = xml_data.get_revision_module_type(game_name, 
                                                             GAME, game_ins_ver)
        
        # Figure out if its a file or folder module
        if game_module_type == "file":
            sys.path.append(join(p.games, game_name))
        else:
            sys.path.append(p.games)
        
        # Add dependencies to path
        for dep_name, dep_ver in \
                    xml_data.list_dependencies_recursive(game_name, GAME):
            dep_module_type = xml_data.get_revision_module_type(dep_name,
                                                                DEP, dep_ver)
            if dep_module_type == "file":
                sys.path.append(join(p.dependencies, dep_name))
            else:
                sys.path.append(p.dependencies)
            
        # Run it
        game = __import__(game_name)
        
        if hasattr(game, "main"):
            game.main()
    
    def run_game(self, game_name):
        """
        Run the game optional argument.
        """
        # Remove stopped games.
        self.cleanup()
        # Start game.
        process = Popen([self.apppath, "-r", game_name])
        # Add process to dictionary.
        self.gamelist[game_name] = process

    def cleanup(self):
        """
        Removes stopped games
        """
        for key, value in dict(self.gamelist).items():
            if value.poll() != None:
                del(self.gamelist[key])
                
    def stop_game_linux_mac(self, game_name):
        """
        Stop a game, linux/mac command.
        """
        pid = str(self.gamelist[game_name].pid)
        call(["kill", pid])
        del(self.gamelist[game_name])
        
    def stop_game_windows(self, game_name):
        """
        Stop a game, windows command.
        """
        pid = str(self.gamelist[game_name].pid)
        call(["taskkill", "/PID", pid])
        del(self.gamelist[game_name])
