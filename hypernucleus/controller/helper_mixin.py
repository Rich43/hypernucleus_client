from hypernucleus.library.module_installer import ModuleInstaller
from hypernucleus.model import GAME, DEP
#from hypernucleus.controller.main import MainWindow
from PyQt4 import QtCore

class InvalidVersion(Exception):
    pass

class BinaryNotFound(Exception):
    pass

class HelperMixin:
    """
    A series of helper functions to make working with PyQt4 easier!
    """
    
    def quick_connect(self, action_name, method_name):
        """
        'Quick Connect'
        Use connect with less code :)
        """
        self.connect(getattr(self.ui, action_name), 
                     QtCore.SIGNAL('triggered()'), 
                     self, QtCore.SLOT(method_name + '()'))
    
    def expand(self, tree_view, tree_item):
        """
        Easy helper to expand a node.
        """
        indexes = [0, 1]
        for i in indexes:
            index = tree_view.model().createIndex(i, 0, tree_item)
            tree_view.expand(index)
        
    def get_selected_item(self, treeview=None):
        """
        Get currently selected item in treeview
        """
        if treeview:
            ci = treeview.currentIndex()
        else:
            ci = self.sender().currentIndex()
        if ci.parent().row() > -1:
            return ci.internalPointer()
        else:
            return None
    
    def get_binary_source_url(self, module_name, revision):
        """
        Get the source url from a dependency revision
        """
        # Set some needed variables
        os = self.ini_mgr.get_operating_system()
        arch = self.ini_mgr.get_architecture()
        binaries = self.m.list_revision_binaries(module_name, DEP, 
                                                 revision)
        display_name = self.m.get_display_name(module_name, DEP)
        os_display_name = self.m.get_operating_system_display_name(os)
        arch_display_name = self.m.get_architecture_display_name(arch)
        source_url = None
        
        # Find the source_url
        for binary in binaries:
            if (os == binary[1] and arch == binary[2] or 
                binary[1] == "pi" and binary[2] == "pi"):
                source_url = binary[0]
                return source_url
        
        # If not found, raise an exception.
        raise BinaryNotFound({"display_name": display_name, 
                              "name": module_name, 
                              "revision": revision, 
                              "os": os_display_name, 
                              "arch": arch_display_name})
        
    def run_game_dep(self, module_name, revision, module_type, game_mgr):
        """
        Run/Install a Game/Dependency
        """
        # Get dependencies from model
        dependencies = list(self.m.list_dependencies_recursive(module_name, 
                                                               module_type))
        
        # Add myself to dependencies if i am one.
        if module_type == DEP:
            dependencies.append((module_name, module_type))
            
        # Get some data from INI File
        installed_ver = self.ini_mgr.get_installed_version(module_name)
        chunk_size = self.ini_mgr.get_chunk_size()
        
        # Install dependencies
        for dep_name, dep_ver in dependencies:
            # Get revision's source url.
            source_url = self.get_binary_source_url(dep_name, dep_ver)
            
            # Figure if module is installed
            installer = ModuleInstaller(source_url, DEP)
            is_installed = installer.is_module_installed(dep_name, 
                                                         module_type)
            
            # If it isn't installed, install it.
            if not is_installed:
                for cur, length in installer.install(chunk_size):
                    yield (dep_name, dep_ver, cur, length)
                self.ini_mgr.set_installed_version(dep_name, dep_ver)
            
            # If the version does not match with the installed version,
            # Remove the current version and install new one.
            if is_installed and installed_ver != revision:
                self.uninstall_game_dep(dep_name, module_type)
                for cur, length in installer.install(chunk_size):
                    yield (dep_name, dep_ver, cur, length)
        
        # Install/run game
        if module_type == GAME:
            source_url = self.m.get_revision_source(module_name, 
                                                    module_type, 
                                                    revision, True)
            installer = ModuleInstaller(source_url, module_type)
            is_installed = installer.is_module_installed(module_name, 
                                                         module_type)
            if is_installed:
                game_mgr.run_game(module_name)
            else:
                for cur, length in installer.install(chunk_size):
                    yield (module_name, revision, cur, length)
                self.ini_mgr.set_installed_version(module_name, revision)
                game_mgr.run_game(module_name)
                
    def uninstall_game_dep(self, module_name, module_type):
        """
        Uninstall a Game/Dependency
        """
        installer = ModuleInstaller(None, module_type)
        is_installed = installer.is_module_installed(module_name, 
                                                     module_type)
        if is_installed:
            installer.uninstall_module(module_name, module_type)
            self.ini_mgr.delete_installed_version(module_name)
            self.reset_models()