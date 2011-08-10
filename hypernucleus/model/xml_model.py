from hypernucleus.model import GAME, DEP
from urllib.request import urlopen
from urllib.error import URLError
from xml.etree.ElementTree import ElementTree
from xml.sax.saxutils import quoteattr

class InvalidGameDepType(Exception):
    pass

class ModuleNameNotFound(Exception):
    pass

class RevisionNotFound(Exception):
    pass

class XmlModel:
    """
    An XML data model
    """
    
    def __init__(self, game_or_dep, url):
        self.file = urlopen(url)
        self.etree = ElementTree(file=self.file)
        if game_or_dep == GAME:
            self.type = GAME
        elif game_or_dep == DEP:
            self.type = DEP
        elif game_or_dep == None:
            self.type = None
        else:
            raise InvalidGameDepType
    
    def list_module_names(self):
        if not self.type:
            raise Exception("None is intended for listing OS/Arch only.")
        item = self.etree.findall(self.type)
        return [x.find("name").text for x in item]
    
    def get_module_name(self, name):
        if not self.type:
            raise Exception("None is intended for listing OS/Arch only.")
        name = quoteattr(name)
        item = self.etree.find(self.type + "[name=%s]" % name)
        if not len(item):
            raise ModuleNameNotFound
        else:
            return item
    
    def get_display_name(self, module_name):
        item = self.get_module_name(module_name)
        return item.find("display_name").text

    def get_description(self, module_name):
        item = self.get_module_name(module_name)
        return item.find("description").text

    def get_created(self, module_name):
        item = self.get_module_name(module_name)
        return item.find("created").text
    
    def get_pictures(self, module_name):
        item = self.get_module_name(module_name)
        result = []
        for x in item.findall("picture"):
            try:
                result.append(urlopen(x.text))
            except URLError:
                pass
        return result
    
    def list_revisions(self, module_name):
        """
        Return sorted list of revisions.
        Biggest number first.
        """
        item = self.get_module_name(module_name)
        itemtwo = item.findall("revision")
        result = [float(x.find("version").text) for x in itemtwo]
        result.sort(reverse=True)
        return result
    
    def get_revision(self, module_name, revision):
        revision = str(revision)
        item = self.get_module_name(module_name)
        name = quoteattr(revision)
        itemtwo = item.find("revision[version=%s]" % name)
        if not len(itemtwo):
            raise RevisionNotFound
        else:
            return itemtwo

    def get_revision_source(self, module_name, revision, return_url=False):
        item = self.get_revision(module_name, revision)
        if return_url:
            return item.find("source").text
        return urlopen(item.find("source").text)

    def get_revision_created(self, module_name, revision):
        item = self.get_revision(module_name, revision)
        return item.find("created").text

    def get_revision_module_type(self, module_name, revision):
        item = self.get_revision(module_name, revision)
        return item.find("moduletype").text
    
    def list_revision_binaries(self, module_name, revision):
        item = self.get_revision(module_name, revision)
        itemtwo = item.findall("binary")
        result = []
        for binary in itemtwo:
            result.append((binary.find("binary").text,
                           binary.find("operating_system").text,
                           binary.find("architecture").text))
        return result
    
    def list_operating_systems(self):
        item = self.etree.findall("operatingsystem")
        result = []
        for os in item:
            result.append((os.find("name").text,
                           os.find("display_name").text))
        return result

    def list_architectures(self):
        item = self.etree.findall("architecture")
        result = []
        for arch in item:
            result.append((arch.find("name").text,
                           arch.find("display_name").text))
        return result
    
"""
x = XmlModel(GAME, "http://hypernucleus.pynguins.com/outputs/xml")
name = "anotherball"
print(x.get_revision_source(name, x.list_revisions(name)[0]))
"""