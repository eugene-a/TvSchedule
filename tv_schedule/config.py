from configparser import ConfigParser
from importlib import import_module
from os.path import join
from yaml import load, add_constructor


def _open(name, mode='r'):
    return open(name, mode, encoding='utf-8')


class _Config:
    def __init__(self, config_file):

        config = ConfigParser()
        config.read_file(open(config_file, encoding='utf-8'))

        modified = False

        if not config.has_section('Input'):
            config.add_section('Input')
            config.set('Input', 'dir', join('..', 'input'))
            config.set('Input', 'channels',
                       join('%(dir)s', 'channels.txt'))
            modified = True

        if not config.has_section('Output'):
            config.add_section('Output')
            config.set('Output', 'dir', join('..', 'output'))
            config.set('Output', 'schedule',
                       join('%(dir)s', 'schedule.txt'))
            config.set('Output', 'summaries',
                       join('%(dir)s', 'summaries.txt'))
            config.set('Output', 'missing',
                       join('%(dir)s', 'missing.txt'))
            modified = True

        if modified:
            with _open(config_file, 'w') as cfile:
                config.write(cfile)

        self.config = config

    def input_dir(self):
        return self.config.get('Input', 'dir')

    def channels(self):
        return self.config.get('Input', 'channels')

    def output_dir(self):
        return self.config.get('Output', 'dir')

    def schedule(self):
        return self.config.get('Output', 'schedule')

    def summaries(self):
        return self.config.get('Output', 'summaries')

    def missing(self):
        return self.config.get('Output', 'missing')


_config = _Config('tv_schedule.conf')

_input_dir = _config.input_dir()
_channels = _config.channels()
_output_dir = _config.output_dir()
_schedule = _config.schedule()
_summaries = _config.summaries()
_missing = _config.missing()

del _config


def input_dir():
    return _input_dir


def channels():
    return _channels


def output_dir():
    return _output_dir


def schedule():
    return _schedule


def summaries():
    return _summaries


def missing():
    return _missing


# YAML !src node handling
# import source module, load and set channel code dictionary if required,
# return 'get_schedule' method of the imported module
def _get_source(loader, node):
    source = loader.construct_scalar(node)
    module = import_module('source.' + source)
    if(module.need_channel_code()):
        with _open(join(_input_dir, source + '.yaml')) as fp:
            module.channel_code = load(fp)
    return module.get_schedule

add_constructor('!src', _get_source)


def get_sources():
    class Sources:
        def __init__(self, dct):
            self.default = dct['default']
            self.special = dct['special']

    with _open(join(_input_dir, 'sources.yaml')) as fp:
        return Sources(load(fp))
