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

import unittest
from hypernucleus.model.ini_manager import INIManager

class UnavailableDependencyError(Exception):
    def __init__(self, module_name):
        self.message = "%s unavailable" % module_name

class UnmatchedDependencyVersionError(Exception):
    def __init__(self, module_name, required_version, available_version):
        self.message = "Version %s of %s is requred, but %s is available" % \
                       (required_version, module_name, available_version)

class OptionalParameterUnsatisfiedError(Exception):
    pass

def check_dependencies(game_deps, available_deps):
    """
    Check if dependencies are satisfied and versions match
    """
    ini_data = INIManager()
    
    for module_name, dep_data in list(game_deps.items()):
        if module_name not in list(available_deps.keys()):
            raise UnavailableDependencyError(module_name)
        required_version = dep_data['version']
        available_version = available_deps[module_name]['version']
        if required_version != available_version:
            raise UnmatchedDependencyVersionError(module_name,
                                                  required_version,
                                                  available_version)
        # Check for optional parameters
        optionals = ['operatingsystem', 'architecture']
        for param in optionals:
            ini_value = ini_data.get(param)
            if (ini_value is not None and
                param in available_deps[module_name]):
                if ini_value != available_deps[module_name][param]:
                    raise OptionalParameterUnsatisfiedError()

class TestDependencys(unittest.TestCase):
    def setUp(self):
        self.available_deps = {'foo': {'version': '1.0',
                                       'operatingsystem': 'windows'},
                               'bar': {'version': '0.6'}}
        self.ini_data = INIManager()
        self.previous_opsystem = self.ini_data.get("operatingsystem")
        self.ini_data.set("operatingsystem", "linux")

    def tearDown(self):
        self.ini_data.set("operatingsystem", self.previous_opsystem)
    
    def test_dep_unsatisfied(self):
        game_deps = {'qwe': {'module_name': 'qwe'}}
        self.assertRaises(UnavailableDependencyError, check_dependencies,
                          game_deps, self.available_deps)

    def test_dep_unsatisfied(self):
        game_deps = {'qwe': {'version': 'xx'}}
        self.assertRaises(UnavailableDependencyError, check_dependencies,
                          game_deps, self.available_deps)

    def test_versions_dont_match(self):
        game_deps = {'foo': {'version': '2.0'}}
        self.assertRaises(UnmatchedDependencyVersionError, check_dependencies,
                          game_deps, self.available_deps)

    def test_optional_parameter(self):
        game_deps = {'foo': {'version': '1.0'}}
        self.assertRaises(OptionalParameterUnsatisfiedError, check_dependencies,
                          game_deps, self.available_deps)

if __name__ == '__main__':
    unittest.main()
