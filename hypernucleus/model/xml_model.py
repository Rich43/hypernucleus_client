from hypernucleus.model import GAME, DEP
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from xml.etree.ElementTree import ElementTree, ParseError
from xml.sax.saxutils import quoteattr

class InvalidGameDepType(Exception):
    pass

class ModuleNameNotFound(Exception):
    pass

class RevisionNotFound(Exception):
    pass

class InvalidURL(Exception):
    pass

class XmlModel:
    """
    An XML data model
    """
    
    def __init__(self, url):
        try:
            self.file = urlopen(url)
        except HTTPError as e:
            raise InvalidURL(e)
        except URLError as e:
            raise InvalidURL(e)
        except ValueError as e:
            raise InvalidURL(e)
        
        try:
            self.etree = ElementTree(file=self.file)
        except ParseError as e:
            raise InvalidURL(e)

    def valid_type(self, module_type, none_allowed=True):
        if not none_allowed and module_type == None:
            raise InvalidGameDepType
        if not module_type in [GAME, DEP, None]:
            raise InvalidGameDepType
    
    def list_module_names(self, module_type):
        self.valid_type(module_type, False)
        item = self.etree.findall(module_type)
        return [x.find("name").text for x in item]
    
    def get_module_name(self, name, module_type):
        self.valid_type(module_type, False)
        name = quoteattr(name)
        item = self.etree.find(module_type + "[name=%s]" % name)
        if item is None:
            raise ModuleNameNotFound("%s of type %s" % (name, module_type))
        else:
            return item
    
    def get_display_name(self, module_name, module_type):
        item = self.get_module_name(module_name, module_type)
        return item.find("display_name").text

    def get_description(self, module_name, module_type):
        item = self.get_module_name(module_name, module_type)
        return item.find("description").text

    def get_created(self, module_name, module_type):
        item = self.get_module_name(module_name, module_type)
        return item.find("created").text
    
    def get_pictures(self, module_name, module_type):
        item = self.get_module_name(module_name, module_type)
        result = []
        for x in item.findall("picture"):
            try:
                result.append(urlopen(x.text))
            except URLError:
                pass
        return result
    
    def list_dependencies(self, module_name, module_type):
        result = []
        item = self.get_module_name(module_name, module_type)
        itemtwo = item.findall("dependency")
        for dep in itemtwo:
            result.append((dep.find("name").text,
                           float(dep.find("version").text)))
        return result
    
    def list_dependencies_recursive(self, module_name, module_type):
        dependencies = self.list_dependencies(module_name, module_type)
        if dependencies:
            for m_name, ver in dependencies:
                yield (m_name, ver)
                for item in self.list_dependencies_recursive(m_name, DEP):
                    yield item
    
    def list_revisions(self, module_name, module_type):
        """
        Return sorted list of revisions.
        Biggest number first.
        """
        item = self.get_module_name(module_name, module_type)
        itemtwo = item.findall("revision")
        result = [float(x.find("version").text) for x in itemtwo]
        result.sort(reverse=True)
        return result
    
    def get_revision(self, module_name, module_type, revision):
        revision = str(revision)
        item = self.get_module_name(module_name, module_type)
        name = quoteattr(revision)
        itemtwo = item.find("revision[version=%s]" % name)
        if not len(itemtwo):
            raise RevisionNotFound
        else:
            return itemtwo

    def get_revision_source(self, module_name, module_type, revision, 
                            return_url=False):
        item = self.get_revision(module_name, module_type, revision)
        if return_url:
            return item.find("source").text
        return urlopen(item.find("source").text)

    def get_revision_created(self, module_name, module_type, revision):
        item = self.get_revision(module_name, module_type, revision)
        return item.find("created").text

    def get_revision_module_type(self, module_name, module_type, revision):
        item = self.get_revision(module_name, module_type, revision)
        return item.find("moduletype").text
    
    def list_revision_binaries(self, module_name, module_type, revision):
        item = self.get_revision(module_name, module_type, revision)
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
    