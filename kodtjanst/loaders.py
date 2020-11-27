# from data_wizard import loaders
# from .iter import CustomIter

# from itertable.loaders import NetLoader
# from itertable.mappers import TupleMapper
# from itertable.exceptions import ParseFailed
# from itertable.util import PARSERS, make_iter
# from itertable import JsonNetIter

# from pdb import set_trace

# def load_url(url, mapper=TupleMapper, options={}):
    
#     from urllib.request import urlopen
#     content_type = urlopen(url).info().get_content_type()

#     if content_type not in PARSERS:
#         raise ParseFailed(f"Could not determine parser for {content_type}")
#     parser = PARSERS[content_type]
#     loader = NetLoader
#     Iter = JsonNetIter()
#     set_trace()
#     return Iter(url=url, **options)

# class CustomJsonUrlLoader(loaders.URLLoader):

#     def get_serializer_name(self):
#         set_trace()
#         return self.default_serializer


#     def  load_iter(self):
#         """
#         docstring
#         """
#         set_trace()
#         options = self.load_iter_options()
#         return load_url(self.url, options=options)
