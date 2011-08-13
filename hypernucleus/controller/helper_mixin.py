from hypernucleus.model.xml_model import XmlModel as Model
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
    
    def run_game_dep(self, module_name, revision, module_type):
        """
        Run/Install a Game/Dependency
        """
        source_url = None
        
        # Get needed data from model
        binaries = self.m.list_revision_binaries(module_name, module_type, 
                                            revision)
        dependencies = self.m.list_dependencies(module_name, module_type)
        
        # Get some data from INI File
        installed_ver = self.ini_mgr.get_installed_version(module_name)
        os = self.ini_mgr.get_operating_system()
        arch = self.ini_mgr.get_architecture()
        
        # Install dependencies
        for m_name, ver in dependencies:
            for mo, r, c, l in self.run_game_dep(m_name, ver, DEP):
                yield (mo, r, c, l)
        
        if module_type == GAME:
            source_url = self.m.get_revision_source(module_name, 
                                                    module_type, 
                                                    revision, True)
            installer = ModuleInstaller(source_url, module_type)
            is_installed = installer.is_module_installed(module_name, 
                                                         module_type)
            if is_installed:
                print("TODO: Run code")
            else:
                for cur, length in installer.install():
                    yield (module_name, revision, cur, length)
                self.ini_mgr.set_installed_version(module_name, revision)
                self.reset_models()
                print("TODO: Run code")
                
        elif module_type == DEP:
            # Find the source_url
            for binary in binaries:
                if (os == binary[1] and arch == binary[2] or 
                    binary[1] == "pi" and binary[2] == "pi"):
                    source_url = binary[0]
                    break
            if not source_url:
                raise BinaryNotFound
            
            # Figure if source_url module is installed
            installer = ModuleInstaller(source_url, module_type)
            is_installed = installer.is_module_installed(module_name, 
                                                         module_type)
            
            # If it isn't installed, install it.
            if not is_installed:
                for cur, length in installer.install():
                    yield (module_name, revision, cur, length)
                self.ini_mgr.set_installed_version(module_name, revision)
                self.reset_models()
                return
            
            # If the version does not match with the installed version,
            # Remove the current version and install new one.
            if is_installed and installed_ver != revision:
                self.uninstall_game_dep(module_name, module_type)
                for mo, r, c, l in self.run_game_dep(module_name, 
                                                    revision, module_type):
                    yield (mo, r, c, l)
                
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