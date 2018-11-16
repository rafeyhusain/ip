import sys, os, os.path, pandas
from datetime import datetime
from subprocess import call
from fmt_generator import FmtGenerator
from sql_generator import SqlGenerator


class CodeGenerator:
    generator_args = None


    def __init__(self, generator_args):
        self.generator_args = generator_args


    @property
    def args(self):
        return self.generator_args.args


    def generate(self):
        print >> sys.stderr, '# Start: Code Generation: %s' % (datetime.now().time().isoformat())

        if self.init():
            self.generate_files()

        print >> sys.stderr, '# End: Code Generation: %s' % (datetime.now().time().isoformat())


    def init(self):
        result = self.check_dir(self.args.dir_csvx)
        result = self.check_dir(self.args.dir_fmt)
        result = self.check_dir(self.args.dir_sql)

        return result


    def check_dir(self, dir):
        result = True

        if not os.path.isdir(dir):
            print >> sys.stderr, '[ERROR]: Directory does not exist. %s' % dir
            result = False

        return result


    def generate_files(self):
        for csvx_file in os.listdir(self.args.dir_csvx):
            if csvx_file.endswith(".csvx"):
                df_csvx = pandas.read_csv(os.path.join(self.args.dir_csvx, csvx_file), sep=',')
 
                fmt = FmtGenerator(self.generator_args, csvx_file, df_csvx)
                fmt.generate()

                sql = SqlGenerator(self.generator_args, csvx_file, df_csvx)
                sql.generate()
