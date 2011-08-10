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

from hypernucleus.library.paths import Paths, PROJNAME
from os.path import exists
from os import makedirs
from configparser import ConfigParser, NoOptionError
from hypernucleus.model import INSTALLED_VERSION

class WindowDimentions:
    """
    Handy object for carting around x,y,width,height
    """
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class INIManager:
    """
    Manages hypernucleus's INI File
    """
    default_url = "http://hypernucleus.pynguins.com/outputs/xml"
    default_picture_width = 200
    default_arch = "i386"
    conf_file = None
    ini_path = None
    
    def __init__(self):
        # Make config directory
        p = Paths()
        
        if not exists(p.games):
            makedirs(p.games)
            
        if not exists(p.dependencies):
            makedirs(p.dependencies)
        
        if not exists(p.pictures):
            makedirs(p.pictures)
            
        if not exists(p.archives):
            makedirs(p.archives)
            
        # Set variables
        self.conf_file = ConfigParser()
        
        if not exists(p.ini_path):
            # Make config file
            self.conf_file.add_section(PROJNAME)
            self.conf_file.set(PROJNAME, "xmlurl", self.default_url)
            self.conf_file.add_section(INSTALLED_VERSION)
            self.save()
        
        self.conf_file.read(p.ini_path)
        
    def save(self):
        """
        Write settings to file
        """
        p = Paths()
        self.conf_file.write(open(p.ini_path, "w"))
        
    def get_xml_url(self):
        """
        Get Data File XML URL
        """
        try:
            return self.conf_file.get(PROJNAME, "xmlurl")
        except NoOptionError:
            return self.default_url
        
    def set_xml_url(self, url):
        """
        Set Data File XML URL
        """
        self.conf_file.set(PROJNAME, "xmlurl", url)
        self.save()
        
    def get_picture_width(self):
        """
        Get picture width
        """
        try:
            return self.conf_file.getint(PROJNAME, "picture_width")
        except NoOptionError:
            return self.default_picture_width
        
    def set_picture_width(self, picture_width):
        """
        Set picture width
        """
        self.conf_file.set(PROJNAME, "picture_width", str(picture_width))
        self.save()
    
    def get_architecture(self):
        """
        Get architecture
        """
        try:
            return self.conf_file.get(PROJNAME, "architecture")
        except NoOptionError:
            return self.default_arch
        
    def set_architecture(self, architecture):
        """
        Set architecture
        """
        self.conf_file.set(PROJNAME, "architecture", architecture)
        self.save()

    def get_operating_system(self):
        """
        Get operating system
        """
        try:
            return self.conf_file.get(PROJNAME, "operating_system")
        except NoOptionError:
            return None
        
    def set_operating_system(self, operating_system):
        """
        Set operating system
        """
        self.conf_file.set(PROJNAME, "operating_system", operating_system)
        self.save()
        
    def get_window_dimentions(self):
        """
        Get window dimentions
        """
        options = ["x", "y", "width", "height"]
        for option in options:
            if not self.conf_file.has_option(PROJNAME, option):
                return None
        x = self.conf_file.getint(PROJNAME, "x")
        y = self.conf_file.getint(PROJNAME, "y")
        width = self.conf_file.getint(PROJNAME, "width")
        height = self.conf_file.getint(PROJNAME, "height")
        return WindowDimentions(x, y, width, height)
        
    def set_window_dimentions(self, window_dimentions_obj):
        """
        Set window dimentions
        """
        self.conf_file.set(PROJNAME, "x", 
                           str(window_dimentions_obj.x))
        self.conf_file.set(PROJNAME, "y", 
                           str(window_dimentions_obj.y))
        self.conf_file.set(PROJNAME, "width", 
                           str(window_dimentions_obj.width))
        self.conf_file.set(PROJNAME, "height", 
                           str(window_dimentions_obj.height))
        self.save()
        
    def set_installed_version(self, module_name, version):
        self.conf_file.set(INSTALLED_VERSION, module_name, str(version))
        self.save()
        
    def get_installed_version(self, module_name):
        try:
            return self.conf_file.getfloat(INSTALLED_VERSION, module_name)
        except NoOptionError:
            return None
        
    def delete_installed_version(self, module_name):
        self.conf_file.remove_option(INSTALLED_VERSION, module_name)