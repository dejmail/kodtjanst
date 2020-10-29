from data_wizard import loaders
from .iter import CustomIter

class CustomIterLoader(loaders.BaseLoader):
    default_serializer = 'kodtjanst.wizard.KodverkSerializer'
    print("in custom loader")
    def load_iter(self):
        print("in custom loader iter method")
        source = self.run.content_object
        return CustomIter(some_option=source.some_option)