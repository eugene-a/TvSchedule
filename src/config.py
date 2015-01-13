from os.path import exists
from configparser import ConfigParser


class Config:
    def __init__(self, config_file):

        config = ConfigParser()

        if exists(config_file):
            config.read(config_file)
        else:
            config.add_section('Input')
            config.set('Input', 'dir', r'..\input')
            config.set('Input', 'channels', r'%(dir)s\tv_channels.txt')

            config.add_section('Output')
            config.set('Output', 'dir', r'..\output')
            config.set('Output', 'schedule', r'%(dir)s\tv_schedule.txt')
            config.set('Output', 'summaries', r'%(dir)s\tv_summaries.txt')
            config.set('Output', 'missing', r'%(dir)s\tv_missing.txt')

            with open(config_file, 'w') as cfile:
                config.write(cfile)

        self.config = config

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
