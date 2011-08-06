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
        
    def get_module_name(self, name):
        name = quoteattr(name)
        item = self.etree.findall(self.type + "[name=%s]" % name)
        if not len(item):
            raise ModuleNameNotFound
        else:
            return item[0]
    
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
print(x.get_pictures("ball"))
"""