import unittest
from metaconfig import Field, Fieldset, Metaconfig, MetaconfigSingletone
from metaconfig.io import VirtualYAMLFileConfigIO
   

class TestConfigRoot(unittest.TestCase):

    def setUp(self) -> None:

        class Server(Fieldset):
            host = Field[str]('127.0.0.1').label('host')
            port = Field[int](8080).label('port')
            url = Field[str]('/test').label('secret url').secret()


        class Config(Metaconfig):
            server = Field[Server]()


        class ConfigSingletone(MetaconfigSingletone):
            server = Field[Server]()


        self.CONFIG = Config
        self.CONFIG_SINGLETONE = ConfigSingletone



    
    def test_export_data(self):
        instance = self.CONFIG(VirtualYAMLFileConfigIO('test.yaml'))
        instance.export()

    def test_export_data_no_secret(self):
        instance = self.CONFIG(VirtualYAMLFileConfigIO('test.yaml'))
        dataset = instance.export()

        self.assertEqual(dataset['server'].get('url'), None)
    
    def test_export_data_secret(self):
        instance = self.CONFIG(VirtualYAMLFileConfigIO('test.yaml'))
        dataset = instance.export(export_secret=True)

        self.assertEqual(dataset['server'].get('url'), '/test')
        
    def test_export_data_secret_updated(self):
        instance = self.CONFIG(VirtualYAMLFileConfigIO('test.yaml'))
        instance.update({'server': {'url': '/test/value'}})
        dataset = instance.export()

        self.assertEqual(dataset['server'].get('url'), '/test/value')

    def test_singletone(self):
        self.assertEqual(id(self.CONFIG_SINGLETONE(VirtualYAMLFileConfigIO('test.yaml'))), id(self.CONFIG_SINGLETONE(VirtualYAMLFileConfigIO('test.yaml'))))
        
            