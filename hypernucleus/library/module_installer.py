from urllib.parse import urlparse
from hypernucleus.library.paths import Paths
import urllib.request, urllib.error
import os
from os.path import join, basename, exists
import tarfile
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
    
    def __init__(self, moduledata, moduletype):
        self.moduledata = moduledata
        self.moduletype = moduletype
        if self.moduletype is 'dependency':
            self.extract_path = self.path.dependencies
        elif self.moduletype is 'game':
            self.extract_path = self.path.games
        else:
            raise ModuleTypeError()

        self._get_file_info()
    
    def _get_file_info(self):
        """
        Retrieves the name and the size of the file to download
        """
        # Get the filename of the file that we will download
        self.filename = basename(urlparse(self.moduledata['archiveurl']).path)
        
        # Get content length header
        req = HeadRequest(self.moduledata['archiveurl'])
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
        # Remove existing file if it exists
        try:
            os.remove(join(self.path.archives, self.filename))
        except OSError:
            pass
        print(self.filename, self.extract_path)
        # Open the file so we can write to it.
        archivefile = open(join(self.path.archives, self.filename), "a+b")
        
        # Open a normal urllib2 object
        archive = urllib.request.urlopen(self.moduledata['archiveurl'])
        
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
            tar = tarfile.open(join(self.path.archives, self.filename))
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

    def uninstall_module(self, modulename, moduletype):
        """
        Uninstall a module removing its files
        """
        
        if moduletype is 'dependency':
            extract_path = self.path.dependencies
        elif moduletype is 'game':
            extract_path = self.path.games
        else:
            raise ModuleTypeError()
    
        path_to_module = join(extract_path, modulename)
        shutil.rmtree(path_to_module, ignore_errors=True)

    def is_game_installed(self, modulename):
        """
        Check if game is installed
        """
        if exists(join(self.path.games, modulename)):
            return True
        else:
            return False

    def is_dependency_installed(self, modulename):
        """
        Check if dependency is installed
        """
        if exists(join(self.path.dependencies, modulename)):
            return True
        else:
            return False