import platform
from hypernucleus.view import settings_path
from hypernucleus.model.ini_manager import INIManager
from hypernucleus.model.xml_model import XmlModel
from PyQt4.QtGui import QDialog
from PyQt4 import uic

class SettingsDialog(QDialog):
    """
    The Settings Dialog.
    """
    
    def __init__(self):
        QDialog.__init__(self)
        self.ui = uic.loadUi(settings_path, self)
        self.ini_mgr = INIManager()
        self.ui.gameRepositoryURLLineEdit.setText(
                                        self.ini_mgr.get_xml_url())
        self.ui.pictureWidthPixelsSpinBox.setValue(
                                        self.ini_mgr.get_picture_width())
        self.ui.detectedOperatingSystem.setText(platform.system())
        arch_text = "%s %s" % (platform.architecture()[0],
                                 platform.processor())
        self.ui.detectedArchitecture.setText(arch_text)
        xml_mdl = XmlModel(None, self.ini_mgr.get_xml_url())
        for os, os_disp in xml_mdl.list_operating_systems():
            if os != "pi":
                self.ui.operatingSystemComboBox.addItem(os_disp)
        for arch, arch_disp in xml_mdl.list_architectures():
            if arch != "pi":
                self.ui.architectureComboBox.addItem(arch_disp)