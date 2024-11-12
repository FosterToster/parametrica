from abc import abstractmethod, ABC
import json
import re
import os
import io


class ConfigIOInterface(ABC):

    def __init__(self) -> None:
        super().__init__()
        self.parent: ABCMetaconfig
    
    @abstractmethod
    def read(self) -> dict:
        ...

    @abstractmethod
    def write(self, dataset: dict):
        ...

    @abstractmethod
    def serialize(self, dataset: dict) -> str:
        ...

    @abstractmethod
    def parse(self, data: str) -> dict:
        ...


class FileConfigIOInterface(ConfigIOInterface):
    
    def __init__(self, filename: str) -> None:
        self.__filename = filename
        super().__init__()

    @property
    def filename(self):
        return self.__filename
    
    @property
    def edit_filename(self):
        return f'{self.filename}.edit'

    def read(self) -> dict:
        with open(self.__filename, 'r', encoding='utf-8') as f:
            data = f.read()
            f.close()
        
        return self.parse(data)
        
    def write(self, dataset: dict):
        serialized = self.serialize(dataset)

        with open(self.edit_filename, 'w+', encoding='utf-8') as f:
            f.write(serialized)
            f.close()

        os.replace(self.edit_filename, self.filename)
        
            

class VirtualFile(FileConfigIOInterface):

    '''For virtual configuration like dev.env or sth'''

    def read(self) -> dict:
        try:
            return super().read()
        except FileNotFoundError as e:
            # Ok. We don`t care.
            return {}
        
    def write(self, dataset: dict):
        # we need nothing to be written
        pass


class JsonFileConfigIO(FileConfigIOInterface):
    
    def serialize(self, dataset: dict) -> str:
        return json.dumps(dataset, indent=2, ensure_ascii=False)

    def parse(self, data: str) -> dict:
        return json.loads(data)


class VirtualJsonFileConfigIO(JsonFileConfigIO, VirtualFile):
    pass


class YAMLFileConfigIO(FileConfigIOInterface):
    def __init__(self, filename: str,*, export_comments: bool = True) -> None:
        super().__init__(filename)
        self.export_comments = export_comments
        from importlib import import_module
        try:
            self.yaml = import_module('yaml')
        except ModuleNotFoundError as e:
            raise ImportError('Package "pyyaml" need to be installed.') from e

    

    def make_comments(self, fieldset: '_FieldRW', dataset:dict, resultstr: str, parent_fieldset: str = '', indent:int = 0) -> str:
        for field_name in dataset.keys():
            field = fieldset.__get_field__(field_name)
                        
            if field.__label__ == '' and field.__hint__ == '':
                continue
            if parent_fieldset == '':
                search = re.compile(rf'.*?(?:\n|^)({field_name}):', re.S)
            else:
                search = re.compile(rf'.*?(?:\n|^) {{{indent-2}}}{parent_fieldset}:.*?\n {{{indent}}}({field_name}):', re.S)
            match = search.match(resultstr)
            if match:
                if len(match.regs) > 1:
                    pos = match.regs[1][0]
                    if field.__is_primitive_type__():
                        comment = ''
                        comment += field.__label__.replace("\n"," ").replace("\r", " ") + " " if field.__label__ else ''
                        comment += field.__hint__.replace("\n"," ").replace("\r", " ") + " " if field.__hint__ else ''
                        comment += f'({field.__generic_type__().__name__})'
                        # comment += f' -> {field.__rule__}' if field.__rule__ else ''
                        resultstr = resultstr[:pos]+f'# {comment}\n'+" "*indent+resultstr[pos:]
                    else:
                        comment = ''
                        comment += field.__label__.replace("\n"," ").replace("\r", " ") + " " if field.__label__ else ''
                        comment += field.__hint__.replace("\n"," ").replace("\r", " ") + " " if field.__hint__ else ''
                        resultstr = resultstr[:pos]+f'# {comment}\n'+" "*indent+resultstr[pos:]
            if not field.__is_iterable_type__() and not field.__is_primitive_type__():
                resultstr = self.make_comments(field.__get__(fieldset, fieldset.__class__), dataset.get(field_name), resultstr, field_name, indent+2)

        return resultstr
            
    def serialize(self, dataset: dict) -> str:
        resultstr = self.yaml.dump(dataset, sort_keys=False, default_flow_style=False, default_style=None, allow_unicode=True, canonical=None, Dumper=self.yaml.SafeDumper)
        return self.make_comments(self.parent, dataset, resultstr) if self.export_comments else resultstr

    def parse(self, data: str) -> dict:
        return self.yaml.load(data, Loader=self.yaml.Loader) or {}


class VirtualYAMLFileConfigIO(YAMLFileConfigIO, VirtualFile):
    pass


class INIFileConfigIO(FileConfigIOInterface):
    def __init__(self, filename: str, *, export_comments: bool = True) -> None:
        super().__init__(filename)
        self.export_comments = export_comments
        from importlib import import_module
        try:
            self.configparser = import_module('configparser')
        except ModuleNotFoundError as e:
            raise ImportError('Package "configparser" need to be installed.') from e
        
    def __add_comments__(self, section: str, config, field: 'ABCField', add_empty_str: bool = False):
        if not self.export_comments:
            return
        
        if field.__label__:
            config.set(section, f'; {field.__label__}')
        if field.__hint__:
            config.set(section, f'; hint: {field.__hint__}')
            
        if (field.__label__ or field.__hint__) and add_empty_str:
            config.set(section, '')
        
    def serialize(self, dataset: dict) -> str:
        config = self.configparser.ConfigParser(allow_no_value=True)
        for key, param in dataset.items():
            if not isinstance(param, dict):
                field = self.parent.__get_field__(key)
                self.__add_comments__('', config, field)
                config.set('', key, str(param))
            
            else:
                config.add_section(key)
                section_field = self.parent.__get_field__(key)
                # self.__add_comments__(key, config, section_field, True)
                
                for subkey, subparam in param.items():
                    if isinstance(subparam, dict):
                        raise ValueError('Maximum attachment depth is 1 for INI format')
                    fieldset = section_field.__get__(self.parent, self.parent.__class__)
                    field = fieldset.__get_field__(subkey)
                    self.__add_comments__(key, config, field)
                    config.set(key, subkey, str(subparam))
        
        string_io = io.StringIO()
        config.write(string_io)
        result_str = string_io.getvalue()[:-2]
        
        for section_name, param in dataset.items():
            if not isinstance(param, dict):
                continue

            field = self.parent.__get_field__(section_name)
            comment_str = ''
            if field.__label__:
                comment_str += f'; {field.__label__}\n'
            if field.__hint__:
                comment_str += f'; hint: {field.__hint__}\n'
            
            if comment_str:
                index = result_str.index(f'\n[{section_name}]\n') + 1
                result_str = result_str[:index] + comment_str + result_str[index:]
        
        return result_str
        
    def parse(self, data: str) -> dict:
        config = self.configparser.ConfigParser(allow_no_value=True)
        config.read_string(data)
        result = config._sections
        result.update(config.defaults())
        return result


class VirtualINIFileConfigIO(INIFileConfigIO, VirtualFile):
    pass


from .abc.fieldset import ABCMetaconfig
from .abc.fieldset import _FieldRW
from .abc.field import ABCField