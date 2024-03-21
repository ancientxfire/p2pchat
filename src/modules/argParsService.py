import argparse


class Arguments():
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Arguments, cls).__new__(cls)
        return cls.instance
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-s', action='store_true')
        self.parser.add_argument('-c', action='store_true')
        version_group = self.parser.add_mutually_exclusive_group()
        version_group.add_argument('--v6', action='store_true')
        
        version_group.add_argument('--v6-only', action='store_true')
        self.args = self.parser.parse_args()
    def getArgs(self):
        return self.args
    