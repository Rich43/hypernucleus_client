from . import GAME, DEP
from urllib.error import URLError, HTTPError
from urllib.request import urlopen
from json import loads

class InvalidGameDepType(Exception):
    pass

class ModuleNameNotFound(Exception):
    pass

class RevisionNotFound(Exception):
    pass

class InvalidURL(Exception):
    pass

class JsonModel:
    """
    An JSON data model
    """
    
    def __init__(self, url):
        try:
            self.file = urlopen(url).read()
        except HTTPError as e:
            raise InvalidURL(e)
        except URLError as e:
            raise InvalidURL(e)
        except ValueError as e:
            raise InvalidURL(e)
        
        try:
            self.jtree = loads(self.file.decode())
        except ValueError as e:
            raise InvalidURL(e)

        if not type(self.jtree) == type({}):
            raise InvalidURL("Invalid Type")
        if not "architectures" in self.jtree:
            raise InvalidURL("No Architectures")
        if not "operatingsystems" in self.jtree:
            raise InvalidURL("No Operating Systems")
        if not "gamedep" in self.jtree:
            raise InvalidURL("No gamedep")

    def valid_type(self, module_type, none_allowed=True):
        if not none_allowed and module_type == None:
            raise InvalidGameDepType
        if not module_type in [GAME, DEP, None]:
            raise InvalidGameDepType
    
    def list_module_names(self, module_type):
        self.valid_type(module_type, False)
        if not self.jtree['gamedep']:
            return
        for item in self.jtree['gamedep']:
            if module_type in item:
                yield(item[module_type])
    
    def get_module_name(self, name, module_type):
        self.valid_type(module_type, False)
        for item in self.list_module_names(module_type):
            if item['name'] == name:
                return item
        raise ModuleNameNotFound("%s of type %s" % (name, module_type))
    
    def get_display_name(self, module_name, module_type):
        item = self.get_module_name(module_name, module_type)
        return item["display_name"]

    def get_description(self, module_name, module_type):
        item = self.get_module_name(module_name, module_type)
        return item["description"]

    def get_created(self, module_name, module_type):
        item = self.get_module_name(module_name, module_type)
        return item["created"]
    
    def get_pictures(self, module_name, module_type):
        return []
    
    def list_dependencies(self, module_name, module_type):
        item = self.get_module_name(module_name, module_type)
        result = []
        if "dependencies" in item:
            for obj in item["dependencies"]:
                result.append((obj["dependency"], obj["version"]))
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
        return sorted(item['revisions'], key=lambda k: k['version'])
    
    def get_revision(self, module_name, module_type, revision):
        revision = str(revision)
        for itemtwo in self.list_revisions(module_name, module_type):
            if itemtwo['version'] == revision:
                return itemtwo
        raise RevisionNotFound

    def get_revision_source(self, module_name, module_type, revision, 
                            return_url=False):
        item = self.get_revision(module_name, module_type, revision)
        if return_url:
            return item["source"]
        return urlopen(item["source"])

    def get_revision_created(self, module_name, module_type, revision):
        item = self.get_revision(module_name, module_type, revision)
        return item["created"]

    def get_revision_module_type(self, module_name, module_type, revision):
        item = self.get_revision(module_name, module_type, revision)
        return item["moduletype"]
    
    def list_revision_binaries(self, module_name, module_type, revision):
        item = self.get_revision(module_name, module_type, revision)
        itemtwo = item.findall("binary")
        result = []
        for binary in itemtwo:
            result.append((binary.find("binary").text,
                           binary.find("operating_system").text,
                           binary.find("architecture").text))
        return result
    
    def get_operating_system_display_name(self, operating_system):
        for item in self.list_operating_systems():
            if item['name'] == operating_system:
                return item.find("display_name").text
            return None
    
    def get_architecture_display_name(self, architecture):
        for item in self.list_architectures():
            if item['name'] == architecture:
                return item.find("display_name").text
            return None
    
    def list_operating_systems(self):
        return self.jtree["operatingsystems"]

    def list_architectures(self):
        return self.jtree["architectures"]
    