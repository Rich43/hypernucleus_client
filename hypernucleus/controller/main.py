'''
Created on 23 Jul 2011

@author: r
'''

import platform
import sys
from os import makedirs
from os.path import join, exists
from urllib.request import urlopen

from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel

from .helper_mixin import HelperMixin
from .settings import SettingsDialog
from ..library.game_manager import GameManager
from ..library.module_installer import ModuleInstaller
from ..library.paths import Paths
from ..model import GAME, DEP, INSTALLED, NOT_INSTALLED, INSTALLED_VERSION
from ..model.ini_manager import INIManager, WindowDimentions
from ..model.json_model import JsonModel as Model
from ..model.tree_model import TreeModel, TreeItem
from ..view import main_path


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
        dimensions = self.ini_mgr.get_window_dimentions()
        if dimensions:
            self.setGeometry(QtCore.QRect(dimensions.x, dimensions.y,
                                          dimensions.width, dimensions.height))

        # Fill treeview with content.
        self.reset_models()

        # Connect all signals/events
        self.ui.actionExit.triggered.connect(self.exit)
        self.ui.actionRun.triggered.connect(self.run)
        self.ui.actionRefresh.triggered.connect(self.refresh)
        self.ui.actionStop.triggered.connect(self.stop)
        self.ui.actionUninstall.triggered.connect(self.uninstall)
        self.ui.actionSettings.triggered.connect(self.settings)
        self.ui.treeGame.doubleClicked.connect(self.game)
        self.ui.treeDep.doubleClicked.connect(self.dep)
        self.ui.tabGameDep.currentChanged.connect(self.tab_changed)
        self.ui.treeGame.selectionModel().selectionChanged.connect(
            self.game_selection_changed_slot)
        self.ui.treeDep.selectionModel().selectionChanged.connect(
            self.dep_selection_changed_slot)

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
        for m_dict in self.m.list_module_names(module_type):
            m_name = m_dict['name']
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
            module_item = TreeItem([m_dict['display_name'], installed_version],
                                   tree_item)
            module_item.tag = (m_name, rev_list[0]['version'])
            for rev in rev_list:
                rev = rev['version']
                rev_item = TreeItem(str(rev), module_item)
                rev_item.tag = (m_name, rev)
                module_item.appendChild(rev_item)
            tree_item.appendChild(module_item)

        # Output the model
        return tree_model

    def selection_changed(self, module_type):
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
            # Delete pictures in dialog
            while self.ui.verticalPic.takeAt(0):
                pass
            # Add new pictures
            p = Paths()
            for picture in self.m.get_pictures(m_name, module_type):
                directory = join(p.pictures, picture['uuid'])
                file_name = join(directory, picture['thumb_name'])
                try:
                    makedirs(directory)
                except FileExistsError:
                    pass
                if not exists(file_name):
                    fl = urlopen(picture["thumb_url"])
                    open(file_name, "wb").write(fl.read())
                    fl.close()
                pixmap = QPixmap(file_name)
                lbl_1 = QLabel('')
                lbl_1.setPixmap(pixmap)
                self.ui.verticalPic.addWidget(lbl_1)
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

    @QtCore.pyqtSlot()
    def tab_changed(self):
        """
        User clicked another tab, refresh selection information.
        """
        tab_index = self.ui.tabGameDep.currentIndex()
        if tab_index == 0:
            self.selection_changed(GAME)
        elif tab_index == 1:
            self.selection_changed(DEP)

    @QtCore.pyqtSlot()
    def refresh(self):
        """
        Refresh button was pressed, reload model.
        """
        self.m = Model(self.ini_mgr.get_xml_url())
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
        tab_index = self.ui.tabGameDep.currentIndex()
        if tab_index == 0:
            item = self.get_selected_item(self.ui.treeGame)
            if item:
                if platform.system == "Windows":
                    self.game_mgr.stop_game_windows(item.tag[0])
                else:
                    self.game_mgr.stop_game_linux_mac(item.tag[0])

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

    @QtCore.pyqtSlot()
    def game_selection_changed_slot(self):
        """
        Game selection was changed
        :return: None
        """
        self.selection_changed(GAME)

    @QtCore.pyqtSlot()
    def dep_selection_changed_slot(self):
        """
        Dependency selection was changed
        :return: None
        """
        self.selection_changed(DEP)

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
