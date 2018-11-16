import os.path
import sys
from datetime import datetime
from subprocess import call


class CsvImporter:
    import_args = None
    csv_path = None


    def __init__(self, import_args, extracted_csv_path):
        self.import_args = import_args
        self.csv_path = extracted_csv_path


    @property
    def args(self):
        return self.import_args.args


    @property
    def csv_exists(self):
        return self.csv_path is not None and os.path.isfile(self.csv_path)


    def import_csv(self):
        print >> sys.stderr, '# Start: CSV Import Process: %s, %s, %s' % (
            self.args.table, self.csv_path, datetime.now().time().isoformat())

        if self.csv_exists:
            return self.run_bcp()
        else:
            print >> sys.stderr, '[ERROR]: CSV file does not exist. %s' % self.csv_path

        print >> sys.stderr, '# End: CSV Import Process: %s, %s, %s' % (
            self.args.table, self.csv_path, datetime.now().time().isoformat())


    def run_bcp(self):
        bcp_cmd = "bcp %s.dbo.%s in %s -b1000 -m100000 -F2 -c -e '%s' -S '%s' -U '%s' -P '%s'" % (
            self.args.db_name,
            self.args.table,
            self.csv_path,
            self.import_args.errors_log_bcp,
            self.args.db_server,
            self.args.user_name,
            self.args.password
        )

        with open(self.args.error_log, 'a') as err_file:
            call([bcp_cmd], stdout=err_file, stderr=err_file, shell=True)
