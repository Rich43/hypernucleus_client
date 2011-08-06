from urllib.request import urlopen
from urllib.error import URLError
from xml.etree.ElementTree import ElementTree
from xml.sax.saxutils import quoteattr

GAME = "game"
DEP = "dependency"

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
        else:
            raise InvalidGameDepType
    
    def list_module_names(self):
        item = self.etree.findall(self.type)
        return [x.find("name").text for x in item]
    
    def get_module_name(self, name):
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

    def get_revision_source(self, module_name, revision):
        item = self.get_revision(module_name, revision)
        return urlopen(item.find("source").text)

    def get_revision_created(self, module_name, revision):
        item = self.get_revision(module_name, revision)
        return item.find("created").text

    def get_revision_module_type(self, module_name, revision):
        item = self.get_revision(module_name, revision)
        return item.find("moduletype").text
    
    """
    def load(self):
        item_id = 0
        for item in self.etree.findall("game"):
            # Put XML attributes into a dictionary
            try:
                attribs = ["name", "version", "description", "picture",
                "archiveurl", "modulename", "moduletype", "author"]
                result = {}
                for attrib in attribs:
                    result[attrib] = item.find(attrib).text
            except AttributeError:
                # Bad XML Schema
                return False
            
            # Put Dictionary in a list
            self.data[item_id] = result
            item_id += 1
        return True
    """

"""
x = XmlModel(GAME, "http://hypernucleus.pynguins.com/outputs/xml")
name = "anotherball"
print(x.get_revision_source(name, x.list_revisions(name)[0]))
"""