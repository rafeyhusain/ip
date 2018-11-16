################################################
# 8.0
# 3
# 1     SQLCHAR   0     8000     ","         4   ColC        ""
# 2     SQLCHAR   0     8000     ","         0   NotUsed     ""
# 3     SQLCHAR   0     8000     "\r\n"      2   ColA        ""
# ----- ------- ------ ------ ------------ ----- -------- ---------
# File   Data   Prefix  Data  End Of Field Table  Table   Collation
# Order  Type   Length Length   Delimiter  Col # Col Name   Name
################################################


import sys, os, os.path, pandas
from datetime import datetime


class FmtGenerator:
    generator_args = None
    csvx_file = None
    df_csvx = None


    dict_sql_types = {
        'int':'SQLINT',
        'date':'SQLDATE',
        'varchar':'SQLCHAR',
        'nvarchar':'SQLNCHAR',
        'char':'SQLCHAR',
        'time': 'SQLTIME',
        'decimal':'SQLDECIMAL',
        'datetime':'SQLDATETIME'
    }


    dict_fmt_types = {
        'int':'1',
        'date':'1',
        'nvarchar':'2',
        'varchar':'2',
        'char':'2',
        'time': '1',
        'decimal':'1',
        'datetime':'1'
    }


    def __init__(self, generator_args, csvx_file, df_csvx):
        self.generator_args = generator_args
        self.csvx_file = csvx_file
        self.df_csvx = df_csvx


    @property
    def args(self):
        return self.generator_args.args


    @property
    def fmt_path(self):
        head = os.path.splitext(self.csvx_file)[0]
        file_name = os.path.basename(head)
        path = os.path.join(self.args.dir_fmt, file_name + ".fmt")

        return path


    def generate(self):
        print >> sys.stderr, '# [INFO]: Generating FMT [%s], %s' % (self.fmt_path, datetime.now().time().isoformat())

        with open(self.fmt_path, 'w') as fmt_file:
            fmt_file.write("13.0\n")
            fmt_file.write("%s\n" % (len(self.df_csvx.columns)))
            for column in self.df_csvx:
                fmt_file.write(self.get_row(column))


    def get_row(self, column):
        col_index = self.df_csvx.columns.get_loc(column)

        column_type = self.df_csvx.iloc[0, col_index].lower()
        column_size = self.df_csvx.iloc[1, col_index]

        c1_csv_index = self.df_csvx.columns.get_loc(column) +1
        c2_sql_type = self.dict_sql_types[column_type]
        c3_fmt_type = self.dict_fmt_types[column_type]
        c4_sql_size =  self.get_size(column_type, column_size)
        c5_sql_default = '""'
        c6_sql_index = c1_csv_index
        c7_sql_column = column.replace(":", "_")
        c8_sql_collation = ("SQL_Latin1_General_CP1_CI_AS" if c3_fmt_type == "2" else '""')

        return ("%-10s%-20s%-10s%-10s%-10s%-10s%-50s%s\n" % (
             c1_csv_index
            ,c2_sql_type
            ,c3_fmt_type
            ,c4_sql_size
            ,c5_sql_default
            ,c6_sql_index
            ,c7_sql_column
            ,c8_sql_collation
        ))


    def get_size(self, column_type, column_size):
        if column_size is pandas.np.nan:
            return ''

        if column_type in self.generator_args.unicode_types:
            column_size = int(column_size) * 2

        elif column_type == 'decimal':
            column_size = 19 # TODO: Specify based on (p,s) column_size.replace('.', ',')

        return column_size
