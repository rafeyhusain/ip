import sys, os, os.path, pandas
from datetime import datetime


class SqlGenerator:
    generator_args = None
    csvx_file = None
    df_csvx = None


    sized_types = [
        'nvarchar',
        'char',
        'varchar',
        'decimal'
    ]


    unicode_types = [
        'nvarchar',
        'nchar',
    ]


    def __init__(self, generator_args, csvx_file, df_csvx):
        self.generator_args = generator_args
        self.csvx_file = csvx_file
        self.df_csvx = df_csvx


    @property
    def args(self):
        return self.generator_args.args


    @property
    def csv_name(self):
        head = os.path.splitext(self.csvx_file)[0]
        file_name = os.path.basename(head)
        return file_name


    @property
    def sql_path(self):
        path = os.path.join(self.args.dir_sql, self.csv_name + ".sql")

        return path


    @property
    def sql_template(self):
        template = ''
        path = os.path.join(self.args.dir_sqlx, 'default_template.sql')
        with open(path, 'r') as template_file:
            template = template_file.read()

        return template


    def generate(self):
        print >> sys.stderr, '# [INFO]: Generating SQL [%s], %s' % (self.sql_path, datetime.now().time().isoformat())

        columns = ''

        for column in self.df_csvx:
            columns += self.get_row(column)

        output = self.sql_template

        output = output.replace('@TABLE_NAME', self.csv_name)
        output = output.replace('@COLUMNS', columns)

        with open(self.sql_path, 'w') as sql_file:
            sql_file.write(output)


    def get_row(self, column):
        col_index = self.df_csvx.columns.get_loc(column)

        column_type = self.df_csvx.iloc[0, col_index]
        column_size = self.df_csvx.iloc[1, col_index]

        sql_column_size =  self.get_size(column_type, column_size)
        sql_column_name = column.replace(":", "_")

        print >> sys.stderr, 'SQL GEN column_type[%s], sql_column_size[%s]' % (column_type, sql_column_size)

        if sql_column_size == '':
            output = ("\t\t\t%-30s%s,\n" % (
                sql_column_name
                ,column_type
            ))

        else:
            output = ("\t\t\t%-30s%s(%s),\n" % (
                sql_column_name
                ,column_type
                ,sql_column_size
            ))

        return output


    def get_size(self, column_type, column_size):
        if column_size is pandas.np.nan:
            return ''

        if column_type in self.generator_args.unicode_types:
            column_size = int(column_size) * 2

        elif column_type == 'DECIMAL':
            column_size = column_size.replace('.', ',')

        return column_size
