#hypernucleus, A database of games made in python with automatic installation.
#Copyright (C) 2008  Richie Ward + Contributors.

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from hypernucleus.library.paths import Paths
from os.path import exists
from os import makedirs
from configparser import ConfigParser
PROJNAME = "hypernucleus"

class INIManager:
    """
    Manages hypernucleus's INI File
    """
    defaulturl = "http://hypernucleus.pynguins.com/outputs/xml"
    conf_file = None
    inipath = None
    
    def __init__(self):
        # Make config directory
        p = Paths()
        
        if not exists(p.games):
            makedirs(p.games)
            
        if not exists(p.dependencys):
            makedirs(p.dependencys)
        
        if not exists(p.pictures):
            makedirs(p.pictures)
            
        if not exists(p.archives):
            makedirs(p.archives)
            
        # Set variables
        self.conf_file = ConfigParser()
        
        # Make config file
        if exists(p.inipath):
            self.conf_file.read(p.inipath)
        else:
            self.conf_file.add_section(PROJNAME)
            self.conf_file.set(PROJNAME, "xmlurl", self.defaulturl)
            self.save()
            
    def save(self):
        """
        Write settings to file
        """
        p = Paths()
        self.conf_file.write(open(p.inipath, "wb"))
        
    def get_xmlurl(self):
        """
        Get Data File XML URL
        """
        return self.conf_file.get(PROJNAME, "xmlurl")
        
    def set_xmlurl(self, url):
        """
        Set Data File XML URL
        """
        self.conf_file.set(PROJNAME, "xmlurl", url)
        self.save()