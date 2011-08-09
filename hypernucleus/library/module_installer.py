from urllib.parse import urlparse
from hypernucleus.library.paths import Paths
from hypernucleus.model import GAME, DEP
import urllib.request, urllib.error
import os
from os.path import join, basename, exists
import zipfile
import shutil

class ModuleTypeError(Exception):
    pass

class DownloadError(Exception):
    def __init__(self, message):
        self.message = message

class HeadRequest(urllib.request.Request):
    """
    A request class which performs a HEAD request
    Useful for getting the size of a file on the internet.
    """

    def get_method(self):
        return 'HEAD'

class ModuleInstaller(object):
    path = Paths()
    
    def __init__(self, url, module_type):
        self.url = url
        self.module_type = module_type
        if self.module_type is DEP:
            self.extract_path = self.path.dependencies
        elif self.module_type is GAME:
            self.extract_path = self.path.games
        else:
            raise ModuleTypeError
    
    def _get_file_info(self):
        """
        Retrieves the name and the size of the file to download
        """
        # Get the filename of the file that we will download
        self.filename = basename(urlparse(self.url).path)
        
        # Get content length header
        req = HeadRequest(self.url)
#        header_archive = urllib2.urlopen(req)
        try:
            header_archive = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            message = 'Error downloading %s.\n%s' % (self.filename, str(e))
            raise DownloadError(message)
        headers = dict(header_archive.headers)
        # TODO: what to do if 'content-length' is not specified?
        self.filesize = headers.get('content-length', -1)
        header_archive.close()
        
    def install(self):
        """
        Download the module archive and extract it to the
        corresponding path
        """
        # Moved from __init__
        self._get_file_info()
        
        # Remove existing file if it exists
        try:
            os.remove(join(self.path.archives, self.filename))
        except OSError:
            pass
        
        # Open the file so we can write to it.
        archivefile = open(join(self.path.archives, self.filename), "a+b")
        
        # Open a normal urllib2 object
        archive = urllib.request.urlopen(self.url)
        
        # Download file
        keep_going = True
        current_pos = 0
        while keep_going:
            chunk = archive.read(1024)
            chunk_size = len(chunk)
            if chunk_size == 0:
                break
            current_pos += chunk_size
            archivefile.write(chunk)
            # TODO: Add QT4 progress bar
        # Clean up.
        archivefile.close()
        archive.close()
        
        if keep_going:
            # Extract archive
            tar = zipfile.ZipFile(
                    open(join(self.path.archives, self.filename), "rb"))
            tar.extractall(self.extract_path)
            tar.close()
        #else:
        #    # Kill dialog if Cancel Pressed
        #    progress_dlg.Destroy()
        
        # Remove archive to save disk space.
        try:
            os.remove(join(self.path.archives, self.filename))
        except OSError:
            pass
        
    def get_extract_path(self, module_type):
        """
        Find path to game/dep directory
        """
        if module_type is DEP:
            extract_path = self.path.dependencies
        elif module_type is GAME:
            extract_path = self.path.games
        else:
            raise ModuleTypeError
        return extract_path
    
    def uninstall_module(self, module_name, module_type):
        """
        Uninstall a module removing its files
        """
        extract_path = self.get_extract_path(module_type)
        path_to_module = join(extract_path, module_name)
        shutil.rmtree(path_to_module, ignore_errors=True)

    def is_module_installed(self, module_name, module_type):
        """
        Check if module is installed
        """
        extract_path = self.get_extract_path(module_type)
        if not module_type in [GAME, DEP]:
            raise ModuleTypeError
        if exists(join(extract_path, module_name)):
            return True
        else:
            return False