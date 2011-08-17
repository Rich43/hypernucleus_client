import sys
import glob
from cx_Freeze import setup, Executable
from os.path import join
base = None
if sys.platform == "win32":
    base = "Win32GUI"

zip_includes = glob.glob(join("hypernucleus", "view", "*.ui"))
includes = []
excludes = []
packages = []

setup(name = "Hypernucleus", 
      version = "1.0", 
      description = "Hypernucleus Client - A Python Game Database", 
      author_email='RichieS@GMail.com',
      url='http://hypernucleus.pynguins.com',
      executables = [Executable("run_hypernucleus.py", base = base)],
      options = {'build_exe': {'excludes': excludes, 'packages': packages, 
                               'zip_includes': zip_includes}})
