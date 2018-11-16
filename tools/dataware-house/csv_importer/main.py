import sys
from csv_import_args import CsvImportArgs
from csv_importer import CsvImporter
from csv_extractor import CsvExtractor


def main(argv):
    args = CsvImportArgs(argv)

    extractor = CsvExtractor(args)
    extracted_csv_path = extractor.extract_csv()

    importer = CsvImporter(args, extracted_csv_path)
    importer.import_csv()


if __name__ == '__main__':
    main(sys.argv)
