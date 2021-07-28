from abc import abstractmethod, ABC
import json

class ConfigIOInterface(ABC):

    def __init__(self, ) -> None:
        super().__init__()
    
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
        

class JsonFileConfigIO(ConfigIOInterface):
    def __init__(self, filename: str) -> None:
        self.__filename = filename
        

    def read(self) -> dict:
        with open(self.__filename, 'r') as f:
            data = f.read()
            f.close()
        
        return self.parse(data)

    def write(self, dataset: dict):
        with open(self.__filename, 'w+') as f:
            f.write(self.serialize(dataset))
            f.close()

    def serialize(self, dataset: dict) -> str:
        return json.dumps(dataset, indent=2, ensure_ascii=False)

    def parse(self, data: str) -> dict:
        return json.loads(data)

        



