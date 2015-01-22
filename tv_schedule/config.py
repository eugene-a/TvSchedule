from os.path import join, expanduser
from yaml import load
from pkg_resources import resource_stream
from codecs import getreader
from functools import partial

_UTF_8 = 'utf-8'
_YAML_EXT = '.yaml'
_CFG = 'tv_schedule' + _YAML_EXT
_OPTION_CHANNELS = 'channels'
_OPTION_SOURCES = 'source'
_OPTION_OUTPUT = 'output'
_DEFAULT_CHANNELS = 'channels.txt'
_SOURCE_DIR = _OPTION_SOURCES
_SOURCE_PACKAGE = 'source'
_SOURCE_DIR = 'sources'
_DEFAULT_OUTPUT_DIR = _OPTION_OUTPUT

_home = expanduser('~')
_data_path = join(_home, 'TvSchedule')


def _open_data_file(name):
    return open(join(_home, name), 'rb')


def _open_source(name):
    name = join(_SOURCE_DIR, name)
    return resource_stream(source_package(), name)


# an optional congfiguration file may specify alternative
# directories  for input and/or output data
class _Config:
    def __init__(self, config_file):
        self.open_channels = partial(resource_stream, __name__)
        self._open_source = _open_source

        self._channels = _DEFAULT_CHANNELS
        self._sources = join(_SOURCE_PACKAGE, _SOURCE_DIR)
        self._output = join(_data_path, _DEFAULT_OUTPUT_DIR)

        try:
            with open(config_file, 'r', encoding=_UTF_8) as f:
                conf = load(f)

                try:
                    self._channels = conf[_OPTION_CHANNELS]
                    self.open_channels = _open_data_file
                except KeyError:
                    pass

                try:
                    self._sources = conf[_OPTION_SOURCES]
                    self._open_source = _open_data_file
                except KeyError:
                    pass

                try:
                    self._output = join(_home, conf[_OPTION_OUTPUT])
                except KeyError:
                    pass

        except FileNotFoundError:
            pass

        self .open_channels = partial(self.open_channels, self._channels)

    def source_dir(self):
        return self._sources

    def output_dir(self):
        return self._output

_config = _Config(join(_data_path, _CFG))


def source_package():
    package_dot = __name__[: __name__.rindex('.') + 1]
    return package_dot + _SOURCE_PACKAGE


def open_source(name):
    return _config._open_source(name + _YAML_EXT)


def output_dir():
    return _config.output_dir()


def channels():
    with _config.open_channels() as f:
        return getreader(_UTF_8)(f).readlines()
