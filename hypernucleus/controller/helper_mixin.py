from hypernucleus.model.xml_model import XmlModel as Model
from hypernucleus.library.module_installer import ModuleInstaller
from hypernucleus.model import GAME, DEP
from PyQt4 import QtCore

class InvalidVersion(Exception):
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
        parent_row = ci.parent().row()
        if parent_row > -1:
            item = ci.model().rootItem.child(parent_row).childItems[ci.row()]
            return item
        else:
            return None
    
    def run_game_dep(self, module_name, revision, module_type):
        """
        Run/Install a Game/Dependency
        """
        if module_type == GAME:
            m = Model(module_type, self.ini_mgr.get_xml_url())
            revisions = m.list_revisions(module_name)
            try:
                rev_index = revisions.index(revision)
            except ValueError:
                raise InvalidVersion
            source_url = m.get_revision_source(module_name, 
                                               revisions[rev_index], True)
            installer = ModuleInstaller(source_url, module_type)
            is_installed = installer.is_module_installed(module_name, 
                                                         module_type)
            if is_installed:
                print("TODO: Run code")
            else:
                installer.install()
                self.reset_models()
        elif module_type == DEP:
            print("dep", module_name, revision)
            
    def uninstall_game_dep(self, module_name, module_type):
        """
        Uninstall a Game/Dependency
        """
        installer = ModuleInstaller(None, module_type)
        is_installed = installer.is_module_installed(module_name, 
                                                     module_type)
        if is_installed:
            installer.uninstall_module(module_name, module_type)
            self.reset_models()