import os.path
import yaml
import pkg_resources
import codecs
import functools

_UTF_8 = 'utf-8'
_YAML_EXT = '.yaml'
_SOURCE_PACKAGE = 'source'
_CFG = 'tv_schedule' + _YAML_EXT
_OPTION_CHANNELS = 'channels'
_DEFAULT_CHANNELS = 'channels.txt'
_OPTION_SOURCE_CHANNELS = 'source_channels'
_DEFAULT_SOURCE_CHANNELS = 'channels'
_OPTION_OUTPUT = 'output'
_DEFAULT_OUTPUT = 'output'

_home = os.path.expanduser('~')
_data_path = os.path.join(_home, 'TvSchedule')


def _open_data_file(name):
    return open(os.path.join(_home, name), 'rb')


def _open_source(name):
    name = os.path.join(_DEFAULT_SOURCE_CHANNELS, name)
    return pkg_resources.resource_stream(source_package(), name)


# an optional configuration file may specify alternative
# locations  for input and/or output data
class _Config:
    def __init__(self, config_file):
        partial = functools.partial

        self.open_channels = partial(pkg_resources.resource_stream, __name__)
        self.open_source = _open_source

        self._channels = _DEFAULT_CHANNELS
        self._source_channels = os.path.join(
            _SOURCE_PACKAGE, _DEFAULT_SOURCE_CHANNELS)
        self._output = os.path.join(_data_path, _DEFAULT_OUTPUT)

        try:
            with open(config_file, 'r', encoding=_UTF_8) as f:
                conf = yaml.load(f)

                try:
                    self._channels = conf[_OPTION_CHANNELS]
                    self.open_channels = _open_data_file
                except KeyError:
                    pass

                try:
                    self._source_channels = conf[_OPTION_SOURCE_CHANNELS]
                    self._open_source = _open_data_file
                except KeyError:
                    pass

                try:
                    self._output = os.path.join(_home, conf[_OPTION_OUTPUT])
                except KeyError:
                    pass

        except FileNotFoundError:
            pass

        self .open_channels = partial(self.open_channels, self._channels)

    def source_channel_dir(self):
        return self._source_channels

    def output_dir(self):
        return self._output

_config = _Config(os.path.join(_data_path, _CFG))


def source_package():
    package_dot = __name__[: __name__.rindex('.') + 1]
    return package_dot + _SOURCE_PACKAGE


def open_source(name):
    return _config.open_source(name + _YAML_EXT)


def output_dir():
    return _config.output_dir()


def channels():
    with _config.open_channels() as f:
        return codecs.getreader(_UTF_8)(f).readlines()
