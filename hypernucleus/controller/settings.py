import platform
from ..view import settings_path
from ..model.ini_manager import INIManager
from ..model.xml_model import XmlModel as Model, InvalidURL
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic, QtCore

INVALID_REPO_FAIL = """You failed to set the repository URL correctly. 
Hypernucleus needs this to download a list of operating systems and 
architectures. Go back to the general tab and set it correctly before coming 
to this tab.""".replace("\n", "")

INVALID_REPO_FAIL_TWO = """You failed to set the repository URL correctly. 
If you cannot get it set right, you may click Cancel to 
abort this dialog.""".replace("\n", "")

class SettingsDialog(QDialog):
    """
    The Settings Dialog.
    """
    
    def __init__(self, initial_tab=0):
        """
        Fill the dialog with some initial data.
        """
        # Initialise the dialog
        QDialog.__init__(self)
        self.ui = uic.loadUi(settings_path, self)
        
        # Set the tabs initial index and add some handy aliases.
        self.ui.tabWidget.setCurrentIndex(initial_tab)
        self.os_combo = self.ui.operatingSystemComboBox
        self.arch_combo = self.ui.architectureComboBox
        
        # Populate controls
        self.ini_mgr = INIManager()
        self.initial_url = self.ini_mgr.get_xml_url().lower()
        self.ui.gameRepositoryURLLineEdit.setText(
                                        self.ini_mgr.get_xml_url())
        self.ui.pictureWidthPixelsSpinBox.setValue(
                                        self.ini_mgr.get_picture_width())
        self.ui.downloadChunkSizeBytesSpinBox.setValue(
                                        self.ini_mgr.get_chunk_size())
        self.ui.detectedOperatingSystem.setText(platform.system())
        arch_text = "%s %s" % (platform.architecture()[0],
                                 platform.machine())
        self.ui.detectedArchitecture.setText(arch_text)
        
        # Add some code to handle an invalid URL and set a flag for
        # later use.
        self.invalid_url = False
        try:
            self.fill_combo_boxes(self.ini_mgr.get_operating_system(),
                                  self.ini_mgr.get_architecture())
            self.invalid_url = False
        except InvalidURL:
            self.invalid_url = True
            
        # Connect any needed events.
        self.ui.tabWidget.currentChanged.connect(self.tab_changed)

    @QtCore.pyqtSlot()
    def accept(self):
        """
        User pressed the OK button.
        """
        # Get data from controls
        selected_os = self.os_combo.itemData(self.os_combo.currentIndex())
        selected_arch = self.arch_combo.itemData(
                                        self.arch_combo.currentIndex())
        current_url = self.ui.gameRepositoryURLLineEdit.text()
        picture_width = self.ui.pictureWidthPixelsSpinBox.value()
        chunk_size = self.ui.downloadChunkSizeBytesSpinBox.value()
        
        # check to see if user has been a prat and entered wrong URL.
        try:
            self.fill_combo_boxes()
        except InvalidURL:
                QMessageBox.critical(self, "Invalid Repository URL", 
                                     INVALID_REPO_FAIL_TWO)
                return
        
        # Save data to INI File
        self.ini_mgr.set_operating_system(selected_os)
        self.ini_mgr.set_architecture(selected_arch)
        self.ini_mgr.set_xml_url(current_url)
        self.ini_mgr.set_picture_width(picture_width)
        self.ini_mgr.set_chunk_size(chunk_size)
        
        # Well done we made it to the end :) Return 1
        self.done(1)
        
    @QtCore.pyqtSlot()
    def tab_changed(self):
        """
        User changed the tab.
        """
        # Get data from controls
        current_url = self.ui.gameRepositoryURLLineEdit.text().lower()
        current_index = self.ui.tabWidget.currentIndex()
        
        # Find out if we need to reload the combo boxes.
        if (current_url != self.initial_url and current_index > 0 or 
            self.invalid_url and current_index > 0):
            
            try:
                self.fill_combo_boxes()
                self.invalid_url = False
            except InvalidURL:
                # User entered invalid URL in first tab, 
                # display error and go back to first tab.
                QMessageBox.critical(self, "Invalid Repository URL", 
                                     INVALID_REPO_FAIL)
                self.ui.tabWidget.setCurrentIndex(0)
                self.invalid_url = True
    
    def fill_combo_boxes(self, os_name=None, arch_name=None):
        """
        Empty the operating system and architecture combo boxes
        and fill them with new items from the Model.
        Also handy for validating the URL
        (Since this will raise an exception).
        """
        # Get data from controls and reset them
        current_url = self.ui.gameRepositoryURLLineEdit.text()
        self.ui.operatingSystemComboBox.clear()
        self.ui.architectureComboBox.clear()
        
        # Load the model
        xml_mdl = Model(current_url)
        
        # Add data to operating system combo
        for os, os_disp in xml_mdl.list_operating_systems():
            if os != "pi":
                self.os_combo.addItem(os_disp)
                self.os_combo.setItemData(self.os_combo.count() - 1, os)
                if os_name and os_name == os:
                    self.os_combo.setCurrentIndex(self.os_combo.count() - 1)
        
        # Add data to architecture combo
        for arch, arch_disp in xml_mdl.list_architectures():
            if arch != "pi":
                self.arch_combo.addItem(arch_disp)
                self.arch_combo.setItemData(
                                        self.arch_combo.count() - 1, arch)
                if arch_name and arch_name == arch:
                    self.arch_combo.setCurrentIndex(
                                        self.arch_combo.count() - 1)
