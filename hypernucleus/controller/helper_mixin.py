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
        m = Model(module_type, self.ini_mgr.get_xml_url())
        if module_type == GAME:
            source_url = m.get_revision_source(module_name, revision, True)
            installer = ModuleInstaller(source_url, module_type)
            is_installed = installer.is_module_installed(module_name, 
                                                         module_type)
            if is_installed:
                print("TODO: Run code")
            else:
                installer.install()
                self.ini_mgr.set_installed_version(module_name, revision)
                self.reset_models()
                print("TODO: Run code")
                
        elif module_type == DEP:
            os = self.ini_mgr.get_operating_system()
            arch = self.ini_mgr.get_architecture()
            binaries = m.list_revision_binaries(module_name, revision)
            source_url = None
            for binary in binaries:
                if (os == binary[1] and arch == binary[2] or 
                    binary[1] == "pi" and binary[2] == "pi"):
                    source_url = binary[0]
                    break
            if not source_url:
                raise BinaryNotFound
            installer = ModuleInstaller(source_url, module_type)
            is_installed = installer.is_module_installed(module_name, 
                                                         module_type)
            if not is_installed:
                installer.install()
                self.ini_mgr.set_installed_version(module_name, revision)
                self.reset_models()
                
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