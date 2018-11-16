import sys, argparse, re, os, os.path, pandas


class CodeGeneratorArgs:
    args = None
    argv = None
    args_parser = None


    unicode_types = [
        'nvarchar',
        'nchar',
    ]


    def __init__(self, argv):
        self.argv = argv

        self.args_parser = argparse.ArgumentParser(add_help=False)
        self.args_parser.add_argument('dir_csvx', type=str, help='Directory of configuration csv files).')
        self.args_parser.add_argument('dir_sqlx', type=str, help='Directory of configuration sql files).')
        self.args_parser.add_argument('dir_fmt', type=str, help='Directory to output fmt).')
        self.args_parser.add_argument('dir_sql', type=str, help='Directory to output sql).')

        self.args = self.args_parser.parse_args()


    @property
    def dir_csvx_exists(self):
        return os.path.isdir(self.args.folder_csvx)


    @property
    def dir_fmt_exists(self):
        return os.path.isdir(self.args.folder_fmt)


    @property
    def dir_sql_exists(self):
        return os.path.isdir(self.args.folder_sql)
