import sys
import glob
from cx_Freeze import setup, Executable
from os import sep
from os.path import join
base = None
if sys.platform == "win32":
    base = "Win32GUI"

include_files = glob.glob(join("hypernucleus", "view", "*.ui"))
include_files = [(p, sep.join(p.split(sep)[1:])) for p in include_files]
include_files.append("pythoncom.py")
include_files.append("pywintypes.py")
includes = ["multiprocessing", "PyQt5", "requests", "pythoncom", 
            "pywintypes", "sysconfig", "distutils"]
excludes = []
packages = []

setup(name = "Hypernucleus", 
      version = "1.0", 
      description = "Hypernucleus Client - A Python Game Database", 
      author_email='RichieS@GMail.com',
      url='http://hypernucleus.pynguins.com',
      executables = [Executable("run_hypernucleus.py", base = base)],
      options = {'build_exe': {'excludes': excludes, 'packages': packages, 
                               'include_files': include_files,
                               'includes': includes}})
