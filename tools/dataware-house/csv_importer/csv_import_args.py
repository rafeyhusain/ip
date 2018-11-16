import argparse, re, os, os.path


class CsvImportArgs:
    args = None
    argv = None
    args_parser = None


    def __init__(self, argv):
        self.argv = argv

        self.args_parser = argparse.ArgumentParser(add_help=False)
        self.args_parser.add_argument('query_filter', type=str, help='Filter for rows to select from csv).')
        self.args_parser.add_argument('table', type=str, help='Table to import csv).')
        self.args_parser.add_argument('input_csv', type=str, help='Input csv file path).')
        self.args_parser.add_argument('error_log', type=str, help='Error log file path).')
        self.args_parser.add_argument('--db_server', type=str, help='Db server).', default='tcp:iprice-bi.database.windows.net')
        self.args_parser.add_argument('--db_name', type=str, help='Db name).', default='test')
        self.args_parser.add_argument('--user_name', type=str, help='Db user name).', default='ipg')
        self.args_parser.add_argument('--password', type=str, help='Db password).', default='test12!@')

        self.args = self.args_parser.parse_args()


    @property
    def errors_log_bcp(self):
        return "%s/errors_bcp_%s.log" % (self.dir_errors_log, self.clean_table_name)


    @property
    def dir_errors_log(self):
        return os.path.dirname(self.args.error_log)


    @property
    def clean_table_name(self):
        return self.clean(self.args.table)


    @property
    def input_csv_name(self):
        head = os.path.splitext(self.args.input_csv)[0]
        return os.path.basename(head)


    @property
    def input_csv_dir(self):
        head = os.path.dirname(self.args.input_csv)
        return head


    def clean(self, s):
        # Remove invalid characters
        s = re.sub('[^0-9a-zA-Z_]', '', s)

        # Remove leading characters until we find a letter or underscore
        s = re.sub('^[^a-zA-Z_]+', '', s)

        return s
