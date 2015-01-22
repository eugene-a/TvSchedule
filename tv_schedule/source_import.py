from importlib import import_module
from yaml import load, add_constructor

from tv_schedule.config import source_package,  open_source

_CFG = 'sources'
_OPTION_DEFAULT = 'default'
_OPTION_SPECIAL = 'special'
_YAML_SRC_TAG = '!src'


# YAML !src node handling
# import source module, load and set channel code dictionary if required,
# return 'get_schedule' method of the imported module
def _import_source(loader, node):
    source = loader.construct_scalar(node)
    module = import_module(source_package() + '.' + source)
    if(module.need_channel_code()):
        with open_source(source) as f:
            module.channel_code = load(f)
    return module.get_schedule

add_constructor(_YAML_SRC_TAG, _import_source)


def import_sources():
    class Sources:
        def __init__(self, dct):
            self.default = dct[_OPTION_DEFAULT]
            self.special = dct[_OPTION_SPECIAL]

    with open_source(_CFG) as f:
        return Sources(load(f))
