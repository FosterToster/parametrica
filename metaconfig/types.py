class MetaFieldClass:
    def __init__(self, *, label, default, hint=''):
        self._label = label
        self._default = self.normalize(default)
        self._hint = hint
        self._value = self._default

    def validate(self, value):
        pass

    def normalize(self, value):
        self.validate(value)
        return value

    def _set(self, value):
        if not value is None:
            self._value = self.normalize(value)

    def _get(self):
        return self._value

    
class IntField(MetaFieldClass):
    def validate(self, value):
        if not type(value) in (int, str):
            raise ValueError(f'Value of type {type(value).__name__} is not compatible with IntField')
        
    def normalize(self, value):
        return int(super().normalize(value))


class ListField(MetaFieldClass):
    def __init__(self, handled_type, *, label, default:list, hint=''):
        if not issubclass(handled_type, MetaFieldClass):
            raise ValueError('handled type of ListField must be a MetaFieldClass')

        self._handled_type = handled_type

        super().__init__(label=label, default=default, hint=hint)

    def validate(self, value):
        if not type(value) is list:
            raise ValueError('ListField value must be a list')

        return super().validate(value)

    def normalize(self, value:list):
        self.validate(value)

        result = list()
        for data in value:
            if type(data) is self._handled_type:
                result.append(data)
            else: 
                result.append(self._handled_type(label='', hint='', default=data))
        
        return result

    def _get(self):
        return [data._get() for data in self._value]


class Fieldset(MetaFieldClass):
    def __init__(self, *, label, default={}, hint=''):
        self.__metafields = list()
        for field in dir(self):
            if field.startswith('_'):
                continue
            if issubclass(type(getattr(self, field)), MetaFieldClass):
                self.__metafields.append(field)

        super().__init__(label=label, default=default, hint=hint)

    def validate(self, value:dict):
        if not type(value) is dict:
            raise ValueError(f'Value of type {type(value)} is not compatible with Fieldset')
        
    def _set(self, value:dict):
        for metafield_name in self.__metafields:
            metafield = getattr(self, metafield_name)
            try:
                metafield._set(value.get(metafield_name))
            except ValueError as e:
                e.args = (f'{self.__class__.__name__}.{metafield_name}: '+str(e))
                raise e

    def _get(self):
        return self

    def __getattribute__(self, name: str):
        content = super().__getattribute__(name)
        if name.startswith('_'):
            return content

        if issubclass(type(content), MetaFieldClass):
            return content._get()
        else:
            return content

        
class ConfigRoot(Fieldset):
    def __init__(self):
        super().__init__(label='', hint='')

    