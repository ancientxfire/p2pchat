import argparse


class Arguments():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        version_group = self.parser.add_mutually_exclusive_group()
        version_group.add_argument('--v6', action='store_true')
        version_group.add_argument('--v6-only', action='store_true')
        self.args = self.parser.parse_args()
    