from os.path import exists
from configparser import ConfigParser
from os.path import join
from json import loads


class Config:
    def __init__(self, config_file):

        config = ConfigParser()
        config.read_file(open(config_file, encoding='utf-8'))
        
        modified = False
        
        if not config.has_section('Input'):
            config.add_section('Input')
            config.set('Input', 'dir', join('..', 'input'))
            config.set('Input', 'channels',
                       join('%(dir)s', 'tv_channels.txt'))
            modified = True

        if not config.has_section('Output'):
            config.add_section('Output')
            config.set('Output', 'dir',  join('..', 'output'))
            config.set('Output', 'schedule',
                       join('%(dir)s', 'tv_schedule.txt'))
            config.set('Output', 'summaries',
                       join('%(dir)s', 'tv_summaries.txt'))
            config.set('Output', 'missing',
                       join('%(dir)s', 'tv_missing.txt'))
            modified = True
            
        if modified:
            with open(config_file, 'w') as cfile:
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

    def default_source(self):
        return loads(self.config.get('Sources', 'default'))

    def sources(self):
        return loads(self.config.get('Sources', 'sources'))
