from abc import abstractmethod, ABC
import json
import re
import os
from typing import List, Union, Optional
from dataclasses import dataclass
from collections import defaultdict


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
        serialized_bytes_like = serialized.encode(encoding='utf-8')

        # Write data to edit file
        fd = os.open(self.edit_filename, os.O_WRONLY | os.O_CREAT, 0o644)
        try:
            writed_bytes = os.write(fd, serialized_bytes_like)
            if writed_bytes == 0 and serialized != '':
                raise IOError(f'0 bytes were written to the file {self.edit_filename}')
            elif writed_bytes != len(serialized_bytes_like):
                raise IOError(f'Instead of the expected {len(serialized_bytes_like)} bytes, {writed_bytes} bytes were written to the file {self.edit_filename}')
            os.fsync(fd)

        finally:
            os.close(fd)

        # Replace original file with edit file
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


@dataclass
class _INIFieldItem:
    name: str
    value: Union[str, int, float, None]
    label: Optional[str] = None
    hint: Optional[str] = None
    
    def to_ini_str(self, export_comments: bool) -> str:
        result_str = ''
        if export_comments:
            if self.label:
                result_str += f'; {self.label}\n'
            if self.hint:
                result_str += f'; hint: {self.hint}\n'
        
        result_str += f'{self.name} = {self.value if self.value is not None else None}\n'
        return result_str


@dataclass
class _INISectionItem:
    name: str
    items: List[_INIFieldItem]
    label: Optional[str] = None
    hint: Optional[str] = None
    
    def to_ini_str(self, export_comments: bool) -> str:
        result_str = ''
        if export_comments:
            if self.label:
                result_str += f'; {self.label}\n'
            if self.hint:
                result_str += f'; hint: {self.hint}\n'
            
        result_str += f'[{self.name}]\n'
        for item in self.items:
            result_str += item.to_ini_str(export_comments)
        
        return result_str


class INIFileConfigIO(FileConfigIOInterface):
    def __init__(self, filename: str, *, export_comments: bool = True) -> None:
        super().__init__(filename)
        self.export_comments = export_comments
    
    def __make_section__(self, fieldset: '_FieldRW', ini_sections: list, fields: dict, section_path: list):
        section_field = fieldset.__get_field__(section_path[-1])
        
        in_section_items: List[_INIFieldItem] = list()
        ini_sections.append(
            _INISectionItem(
                name=".".join(section_path),
                items=in_section_items,
                label=section_field.__label__ or None,
                hint=section_field.__hint__ or None
            )
        )
        
        section_fieldset = section_field.__get__(fieldset, fieldset.__class__)
        for key, value in fields.items():
            if isinstance(value, dict):
                self.__make_section__(section_fieldset, ini_sections, value, section_path=[*section_path, key])
            else:
                field = section_fieldset.__get_field__(key)
                in_section_items.append(_INIFieldItem(
                    name=key,
                    value=value,
                    label=field.__label__ or None,
                    hint=field.__hint__ or None
                ))
        
    def serialize(self, dataset: dict) -> str:
        default_list_items: List[_INIFieldItem] = list()
        section_list: List[_INISectionItem] = list()
        section_list.append(_INISectionItem(name='', items=default_list_items))
        for field_name, fields in dataset.items():
            if isinstance(fields, dict):
                self.__make_section__(self.parent, section_list, fields, [field_name])
            else:
                field = self.parent.__get_field__(field_name)
                default_list_items.append(
                    _INIFieldItem(
                        name=field_name,
                        value=fields,
                        label=field.__label__,
                        hint=field.__hint__
                    )
                )

        result_str = ''
        for section in section_list:
            if section.name == '' and len(section.items) == 0:
                continue
            result_str += section.to_ini_str(self.export_comments) + '\n'

        return result_str[:-2]
    
    def __get_current_lvl__(self, dataset: dict, path: list):
        result = dataset
        for lvl in path:
            result = result[lvl]
        
        return result
    
    def parse(self, data):
        def defaultdict_fabric():
            return defaultdict(defaultdict_fabric)
        
        result = defaultdict(defaultdict_fabric)
        
        current_section = result
        for line in data.split('\n'):
            line = line.strip()
            if line == '' or line[0] == ';':
                continue
            elif line == '[]':
                current_section = result
            elif line[0] == '[':
                current_section = self.__get_current_lvl__(result, line[1:-1].split('.'))
            elif '=' not in line:
                current_section[line] = ''
            else:
                key, value = line.split('=', maxsplit=1)
                key = key.strip()
                value = value.strip()
                current_section[key] = value

        return result


class VirtualINIFileConfigIO(INIFileConfigIO, VirtualFile):
    pass


from .abc.fieldset import ABCMetaconfig
from .abc.fieldset import _FieldRW
