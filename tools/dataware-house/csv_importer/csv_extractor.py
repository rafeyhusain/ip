import sys, os, os.path, pandas
from datetime import datetime


class CsvExtractor:
    import_args = None


    def __init__(self, import_args):
        self.import_args = import_args


    @property
    def args(self):
        return self.import_args.args


    @property
    def csv_exists(self):
        return self.args.input_csv is not None and os.path.isfile(self.args.input_csv)


    def extract_csv(self):
        print >> sys.stderr, '_________________________________________________________________________________'
        print >> sys.stderr, '# Start: Extract Process: %s, %s, %s' % (
            self.args.input_csv, self.args.query_filter, datetime.now().time().isoformat())

        if self.csv_exists:
            return self.to_csv()
        else:
            print >> sys.stderr, '[ERROR]: CSV file does not exist. %s' % self.args.input_csv

        print >> sys.stderr, '# End: Extract Process: %s, %s, %s' % (
            self.args.input_csv, self.args.query_filter, datetime.now().time().isoformat())


    def to_csv(self):
        output = pandas.read_csv(self.args.input_csv, sep=',')

        # to import complete csv pass query_filter == ""
        if self.args.query_filter != '':
            output = self.safe_query(output, self.args.query_filter)

        if len(output) == 0:
            print >> sys.stderr, '# [INFO]: Nothing to import. Filter returned zero rows: %s' % (self.args.query_filter)
            return None

        output.insert(
              0
            , 'ipg:batchNo'
            , "%s_%s" % (self.import_args.input_csv_name, datetime.now().strftime("%Y%m%dT%H%M%S"))
            , False
            )

        output = output.fillna('')

        csv_path = "%s/__%s.csv" % (self.import_args.input_csv_dir, self.import_args.input_csv_name)

        with open(csv_path, 'w+') as csv_file:
            output.to_csv(csv_file,
                          header=True,
                          index=False,
                          encoding='utf-8-sig',
                          sep='\t')

        return csv_path


    # The current implementation of 'query' requires the string to be a valid python
    # expression, so column names must be valid python identifiers. 
    def safe_query(self, df, query):
        invalid_column_names = [x for x in list(df.columns.values)]

        # Make replacements in the query and keep track
        # NOTE: This method fails if the frame has columns called REPL_0 etc.
        replacements = dict()
        for column in invalid_column_names:
            r = 'REPL_' + str(invalid_column_names.index(column))
            query = query.replace(column, r)
            replacements[column] = r

        inv_replacements = {replacements[k]: k for k in replacements.keys()}

        df = df.rename(columns=replacements)  # Rename the columns

        df = df.query(query)  # Carry out query

        df = df.rename(columns=inv_replacements)

        return df
