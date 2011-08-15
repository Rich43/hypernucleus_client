import sys
from subprocess import Popen, call

class GameManager:
    """
    Manages Game Processes
    """
    gamelist = {}
    
    def __init__(self):
        self.apppath = sys.argv[0]
        
    def run_game(self, game_name):
        """
        Run the game
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
        for key, value in self.gamelist.items():
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