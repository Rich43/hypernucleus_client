'''
Created on 23 Jul 2011

@author: r
'''

from hypernucleus.view import main_path
from hypernucleus.model.ini_manager import INIManager, WindowDimentions
from hypernucleus.model.tree_model import TreeModel, TreeItem
from hypernucleus.model.xml_model import XmlModel as Model
from hypernucleus.library.module_installer import (ModuleInstaller,
                                                   DownloadError)
from hypernucleus.library.game_manager import GameManager
from hypernucleus.model import (GAME, DEP, INSTALLED, NOT_INSTALLED,
                                INSTALLED_VERSION)
from hypernucleus.controller.helper_mixin import HelperMixin, BinaryNotFound
from hypernucleus.controller.settings import SettingsDialog
from PyQt4.QtGui import QMainWindow, QTreeView, QProgressDialog, QMessageBox
from PyQt4 import uic, QtCore
import sys

class MainWindow(QMainWindow, HelperMixin):
    """
    The Main Window.
    """
    
    def __init__(self, app, m):
        QMainWindow.__init__(self)
        self.app = app
        self.m = m
        self.ui = uic.loadUi(main_path, self)
        self.game_mgr = GameManager()
        
        # Set the window dimensions from config.
        self.ini_mgr = INIManager()
        dimentions = self.ini_mgr.get_window_dimentions()
        if dimentions:
            self.setGeometry(QtCore.QRect(dimentions.x, dimentions.y,
                                          dimentions.width, 
                                          dimentions.height))
        
        # Fill treeview with content.
        self.reset_models()
            
        # Connect all signals/events
        self.quick_connect("actionExit", "exit")
        self.quick_connect("actionRun", "run")
        self.quick_connect("actionStop", "stop")
        self.quick_connect("actionUninstall", "uninstall")
        self.quick_connect("actionSettings", "settings")
        self.ui.treeGame.doubleClicked.connect(self.game)
        self.ui.treeDep.doubleClicked.connect(self.dep)
        self.ui.tabGameDep.currentChanged.connect(self.tab_changed)
        self.ui.treeGame.selectionChanged = self.game_selection_changed
        self.ui.treeDep.selectionChanged = self.dep_selection_changed
        
    def reset_models(self):
        """
        Reload items in treeview
        """
        # Reset dependency model
        list_model = TreeModel(["Name", "Version"])
        self.ui.dependenciesTreeView.setModel(list_model)
        
        # Clear the root/child items
        self.root_items = {GAME: {}, DEP: {}}

        # Make new models
        self.ui.treeGame.setModel(self.configure_model(GAME))
        self.ui.treeDep.setModel(self.configure_model(DEP))
        
        # Expand relevant nodes.
        part_one = [(GAME, self.ui.treeGame), (DEP, self.ui.treeDep)]
        part_two = [INSTALLED, NOT_INSTALLED]
        for one_key, one_tv in part_one:
            for two in part_two:
                self.expand(one_tv, self.root_items[one_key][two])
        
        for dummy, one_tv in part_one:
            one_tv.resizeColumnToContents(0)
            
    def configure_model(self, module_type):
        """
        Add items to a Tree View model.
        """
        # Make the title bar.
        tree_model = TreeModel(["Name", INSTALLED_VERSION])
        root_item = tree_model.rootItem
        
        # Add Installed root item
        ins = TreeItem([INSTALLED, ''], root_item)
        self.root_items[module_type][INSTALLED] = ins
        tree_model.appendChild(ins)
        
        # Add Not Installed root item
        not_ins = TreeItem([NOT_INSTALLED, ''], root_item)
        self.root_items[module_type][NOT_INSTALLED] = not_ins
        tree_model.appendChild(not_ins)
        
        # Populate root items with data, check to see if module is installed.
        installer = ModuleInstaller(None, module_type)
        for m_name in self.m.list_module_names(module_type):
            rev_list = self.m.list_revisions(m_name, module_type)
            # Ignore this module if it has no revisions.
            if not len(rev_list):
                continue
            # Check to see if module is installed
            is_installed = installer.is_module_installed(m_name, module_type)
            # If so, put item in installed category
            # Else put in not installed
            if is_installed:
                tree_item = ins
                installed_version = str(self.ini_mgr.get_installed_version(
                                                                    m_name))
            else:
                tree_item = not_ins
                installed_version = ''
            module_item = TreeItem([self.m.get_display_name(m_name, 
                                                            module_type), 
                                    installed_version], tree_item)
            module_item.tag = (m_name, rev_list[0])
            for rev in rev_list:
                rev_item = TreeItem(str(rev), module_item)
                rev_item.tag = (m_name, rev)
                module_item.appendChild(rev_item)
            tree_item.appendChild(module_item)
        
        # Output the model
        return tree_model
        
    def selection_changed(self, old_selection, new_selection, module_type):
        """
        This is an event.
        Called when a different item was selected on the TreeView.
        """
        # Get the treeview that we are editing
        if module_type == GAME:
            tree_view = self.ui.treeGame
        elif module_type == DEP:
            tree_view = self.ui.treeDep
            
        # Get the currently selected item from model and 
        # init the module installer class
        item = self.get_selected_item(tree_view)
        installer = ModuleInstaller(None, module_type)
        
        # If we are not the parent item...
        if item:
            # Get the module name from selected item's tag
            m_name = item.tag[0]
            
            # Populate the text boxes with data
            self.ui.projectNameLineEdit.setText(
                                self.m.get_display_name(m_name, module_type))
            self.ui.pythonModuleNameLineEdit.setText(m_name)
            self.ui.projectCreationDateLineEdit.setText(
                                self.m.get_created(m_name, module_type))
            self.ui.projectDescriptionLineEdit.setText(
                                self.m.get_description(m_name, module_type))
            
            # Check to see if module is installed and
            # show the installed version if it is.
            if installer.is_module_installed(m_name, module_type):
                i_version = str(self.ini_mgr.get_installed_version(m_name))
                self.ui.installedVersionLineEdit.setText(i_version)
            else:
                self.ui.installedVersionLineEdit.setText(NOT_INSTALLED)
            
            # Load the dependencies from model and 
            # display them in the treeview.
            list_model = TreeModel(["Name", "Version"])
            root_item = list_model.rootItem
            for dep in self.m.list_dependencies_recursive(m_name, 
                                                          module_type):
                list_model.appendChild(TreeItem([dep[0], str(dep[1])], 
                                                root_item))
            self.ui.dependenciesTreeView.setModel(list_model)
            
    def dep_selection_changed(self, old_selection, new_selection):
        """
        Dependency selection changed, call above function.
        """
        self.selection_changed(old_selection, new_selection, DEP)
        return QTreeView.selectionChanged(self.ui.treeDep, 
                                                old_selection, 
                                                new_selection)
    
    def game_selection_changed(self, old_selection, new_selection):
        """
        Game selection changed, call above function.
        """
        self.selection_changed(old_selection, new_selection, GAME)
        return QTreeView.selectionChanged(self.ui.treeGame, 
                                                old_selection, 
                                                new_selection)
        
    @QtCore.pyqtSlot()
    def tab_changed(self):
        """
        User clicked another tab, refresh selection information.
        """
        tab_index = self.ui.tabGameDep.currentIndex()
        if tab_index == 0:
            self.selection_changed(tab_index, tab_index, GAME)
        elif tab_index == 1:
            self.selection_changed(tab_index, tab_index, DEP)
    
    def run_game_dep_wrapper(self, module_type, retry=False):
        """
        Short wrapper around run_game_dep
        """
        progress_dialog = {}
        label_text = "Installing %s %s, %s of %s"
        win_title = "Downloading..."
        DOWNLOAD_FAIL = "Could not download game or dependency."
        DOWNLOAD_FAIL += " Check Internet connection and try again."
        DEP_FAIL = "Could not find a dependency with "
        DEP_FAIL += "the following requirements:\n"
        DEP_FAIL += "Project Name: %(name)s\n"
        DEP_FAIL += "Python Module Name: %(display_name)s\n"
        DEP_FAIL += "Version: %(revision)s\n"
        DEP_FAIL += "Operating System: %(os)s\n"
        DEP_FAIL += "Architecture: %(arch)s\n"
        DEP_FAIL += "Ask the project maintainer(s) to upload "
        DEP_FAIL += "a binary for your operating system and architecture."
        
        if module_type == GAME:
            item = self.get_selected_item(self.ui.treeGame)
        else:
            item = self.get_selected_item(self.ui.treeDep)
            
        if item:
            try:
                for mo, r, c, l in self.run_game_dep(item.tag[0], 
                                                     item.tag[1], 
                                                     module_type,
                                                     self.game_mgr):
                    if not (mo, r) in progress_dialog and l > 2 ** 19:
                        progress_dialog[(mo, r)] = QProgressDialog(self)
                        progress_dialog[(mo, r)].setMaximum(l)
                        progress_dialog[(mo, r)].setVisible(True)
                        progress_dialog[(mo, r)].setWindowTitle(win_title)
                    if (mo, r) in progress_dialog:
                        dlg = progress_dialog[(mo, r)]
                        dlg.setValue(c)
                        dlg.setLabelText(label_text % (mo, r, c, l))
                    self.app.processEvents()
            except DownloadError:
                # If we have not been here before.
                if not retry:
                    # Reset the model and have another go.
                    self.m = Model(self.ini_mgr.get_xml_url())
                    self.reset_models()
                    self.run_game_dep_wrapper(module_type, True)
                    return
                else:
                    # Went wrong twice, show error.
                    QMessageBox.critical(self, 
                                         "Download Failed", 
                                         DOWNLOAD_FAIL)
                    return
            except BinaryNotFound as e:
                QMessageBox.critical(self, 
                                         "Cannot find dependency.", 
                                         DEP_FAIL % e.args[0])
            self.reset_models()
            
    @QtCore.pyqtSlot()
    def game(self):
        """
        Game treeview was double clicked, install/run the game.
        """
        self.run_game_dep_wrapper(GAME)
        
    @QtCore.pyqtSlot()
    def dep(self):
        """
        Dependency treeview was double clicked, 
        install the dependency.
        """
        self.run_game_dep_wrapper(DEP)

    @QtCore.pyqtSlot()
    def exit(self):
        """
        Exit button on toolbar
        """
        sys.exit()

    @QtCore.pyqtSlot()
    def run(self):
        """
        Run button on toolbar was clicked.
        Figure what tab were on, and run/install game/dep
        """
        tab_index = self.ui.tabGameDep.currentIndex()
        if tab_index == 0:
            self.run_game_dep_wrapper(GAME)
        elif tab_index == 1:
            self.run_game_dep_wrapper(DEP)
    
    @QtCore.pyqtSlot()
    def stop(self):
        """
        Kill the currently running game.
        """
        #self.game_mgr.stop_game_linux_mac(game_name)
        #self.game_mgr.stop_game_windows(game_name)
        pass
    
    @QtCore.pyqtSlot()
    def uninstall(self):
        """
        Uninstall button on toolbar was clicked.
        """
        tab_index = self.ui.tabGameDep.currentIndex()
        if tab_index == 0:
            item = self.get_selected_item(self.ui.treeGame)
            if item:
                self.uninstall_game_dep(item.tag[0], GAME)
        elif tab_index == 1:
            item = self.get_selected_item(self.ui.treeDep)
            if item:
                self.uninstall_game_dep(item.tag[0], DEP)
        
    @QtCore.pyqtSlot()
    def settings(self):
        """
        Settings button on toolbar was clicked.
        """
        settings = SettingsDialog()
        settings.show()
        
    def resizeEvent(self, event):
        """
        Window was resized, save position.
        """
        self.move_resize()
    
    def moveEvent(self, event):
        """
        Window was moved, save position.
        """
        self.move_resize()
     
    def move_resize(self):
        """
        Do the processing for a move/resize event.
        """
        ini_mgr = INIManager()
        q_rect = self.geometry()
        dimentions = WindowDimentions(q_rect.x(), q_rect.y(), 
                                      q_rect.width(), q_rect.height())
        ini_mgr.set_window_dimentions(dimentions)