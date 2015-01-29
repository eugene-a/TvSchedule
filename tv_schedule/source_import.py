import importlib
import yaml

from tv_schedule import config

_CHANNEL_ASSIGNMENT = 'channel_assignment'
_OPTION_DEFAULT = 'default'
_OPTION_SPECIAL = 'special'
_YAML_SRC_TAG = '!src'


# YAML !src node handling
# import source module, load and set channel code dictionary if required,
# return 'get_schedule' method of the imported module
def _import_source(loader, node):
    source = loader.construct_scalar(node)
    module = importlib.import_module(config.source_package() + '.' + source)
    if(module.need_channel_code()):
        with config.open_source(source) as f:
            module.channel_code = yaml.load(f)
    return module.get_schedule

yaml.add_constructor(_YAML_SRC_TAG, _import_source)


def import_sources():
    class Sources:
        def __init__(self, dct):
            self.default = dct[_OPTION_DEFAULT]
            self.special = dct[_OPTION_SPECIAL]

    with config.open_source(_CHANNEL_ASSIGNMENT) as f:
        return Sources(yaml.load(f))
