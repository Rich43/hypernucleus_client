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
from hypernucleus.library.find_path import user_data_dir
from os.path import join
import getpass

PROJNAME = "hypernucleus"

class Paths:
    """
    Contains path variables
    """
    datadir = user_data_dir(PROJNAME, owner=getpass.getuser())
    ini_path = join(datadir, "config.ini")
    games = join(datadir, "games")
    dependencies = join(datadir, "dependencies")
    pictures = join(datadir, "pictures")
    archives = join(datadir, "archives")
    