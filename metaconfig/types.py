from .io import JsonFileConfigIO

class MetaFieldClass:
    def __init__(self, *, label, default, hint=''):
        self._label = label
        self._default = self.normalize(default)
        self._hint = hint
        self._value = None
        self._set(self._default)
        # self._value = self._default

    def validate(self, value):
        pass

    def normalize(self, value):
        if value is None:
            return self._default

        self.validate(value)
        return value

    def _set(self, value):
        if not value is None:
            self._value = self.normalize(value)

    def _get(self):
        return self._value

    def as_metadata(self):
        return {
            'type': self.__class__.__name__,
            'default': self._default,
            'label': self._label,
            'hint': self._hint
        }

    def as_dataset(self):
        return self._value

    
class IntField(MetaFieldClass):
    def validate(self, value):
        if not type(value) in (int, str):
            raise ValueError(f'Value of type {type(value).__name__} is not compatible with IntField')
        
    def normalize(self, value):
        return int(super().normalize(value))


class StrField(MetaFieldClass):
    def validate(self, value):
        if not type(value) in (int, str, float, bool):
            raise ValueError(f'Value of type {type(value).__name__} is not compatible with StrField')
        
    def normalize(self, value):
        return str(super().normalize(value))


class FloatField(MetaFieldClass):
    def validate(self, value):
        if not type(value) in (int, str, float):
            raise ValueError(f'Value of type {type(value).__name__} is not compatible with FloatField')
    
    def normalize(self, value):
        return float(super().normalize(value))


class BoolField(MetaFieldClass):
    def normalize(self, value):   
        if type(value) is int:
            return value != 0
        elif type(value) is str:
            if value.strip().lower() == 'true':
                return True
            elif value.strip().lower() == 'false':
                return False
            else:
                raise ValueError(f'Value "{value}" is not compatible with BoolField')
        elif type(value) == bool:
            return value
        else:
            raise ValueError(f'Value of type {type(value).__name__} is not compatible with BoolField')
        


class ListField(MetaFieldClass):
    def __init__(self, member_type:MetaFieldClass, *, label, default:list, hint=''):
        if not issubclass(type(member_type), MetaFieldClass):
            raise ValueError('handled type of ListField must be a object of MetaFieldClass')

        self._member_type = member_type

        super().__init__(label=label, default=default, hint=hint)

    def validate(self, value):
        if not type(value) is list:
            raise ValueError('ListField value must be a list')

        return super().validate(value)

    def normalize(self, value:list):
        if value is None:
            return self._default

        self.validate(value)

        result = list()
        for data in value:
            result.append(self._member_type.normalize(data))

        
        
        return result

    def _set(self, value):
        self._value = self.normalize(value)

        self._datalist = list()
        for data in self._value:
            self._datalist.append(
                type(self._member_type)(

                    label=self._member_type._label,
                    hint=self._member_type._hint,
                    default=data
                )
            )
        

    def _get(self):
        return [data._get() for data in self._datalist]

    def as_metadata(self):
        return {
            **super().as_metadata(),
            'member_type': self._member_type.as_metadata()
        }

    def as_dataset(self):
        return [item.as_dataset() for item in self._datalist]


class Fieldset(MetaFieldClass):
    def __init__(self, *, label, default={}, hint=''):
        self.__metafields = list()
        for field in dir(self):
            if field.startswith('_'):
                continue

            metafield = getattr(self, f'@{field}')
            if issubclass(type(metafield), MetaFieldClass):
                self.__metafields.append(field)
                if isinstance(metafield, ListField):
                    setattr(self, field, type(metafield)(metafield._member_type, label=metafield._label, default=metafield._default, hint=metafield._hint))    
                else:
                    setattr(self, field, type(metafield)(label=metafield._label, default=metafield._default, hint=metafield._hint))
        
        super().__init__(label=label, default=default, hint=hint)

    def validate(self, value:dict):
        if not type(value) is dict:
            raise ValueError(f'Value of type {type(value)} is not compatible with Fieldset')

    def normalize(self, value:dict):
        if value is None:
            return self._default

        self.validate(value)
        dataset = dict()
        
        for metafield_name in self.__metafields:
            metafield = getattr(self, f'@{metafield_name}')
            try:
                dataset[metafield_name] = metafield.normalize(value.get(metafield_name, metafield._value))
            except ValueError as e:
                e.args = (f'{self.__class__.__name__}.{metafield_name}: '+str(e),)
                raise e

        return dataset

    def _set(self, value):
        self._value = self.normalize(value)
        for key, val in self._value.items():
            getattr(self, f'@{key}')._set(val)
            
    def _get(self):
        return self

    def __getattribute__(self, name: str):
        if name.startswith('@'):
            return super().__getattribute__(name[1:])

        content = super().__getattribute__(name)

        if name.startswith('_'):
            return content

        if issubclass(type(content), MetaFieldClass):
            return content._get()
        else:
            return content

    def as_metadata(self):
        return {
            **super().as_metadata(),
            **dict((f'@{member_name}', getattr(self, f'@{member_name}').as_metadata()) for member_name in self.__metafields)
        }

    def as_dataset(self):
        return dict((key, getattr(self, f'@{key}').as_dataset()) for key in self.__metafields)


        
class ConfigRoot(Fieldset):

    def __init__(self):
        ...

    def _initialize(self):
        if not hasattr(self, '__io_class__'):
            self.__io_class__ = JsonFileConfigIO('settings.json')

        super().__init__(label='', hint='')

        self._load_config()

    @classmethod
    def as_metadata(class_):
        result = dict()

        for metafield in dir(class_):
            if metafield.startswith('_'):
                continue

            if issubclass(type(getattr(class_, metafield)), MetaFieldClass):
                result[metafield] = getattr(class_, metafield).as_metadata()
        
        return result

    def _load_config(self):
        try:
            self._set(self.__io_class__.read())
        except FileNotFoundError:
            self.update({})

    def update(self, dataset: dict):
        self._set(dataset)
        self.__io_class__.write(self.normalize(dataset))
        

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        
        return cls._instance




    