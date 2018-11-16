import sys
from code_generator_args import CodeGeneratorArgs
from code_generator import CodeGenerator


def main(argv):
    args = CodeGeneratorArgs(argv)

    generator = CodeGenerator(args)
    generator.generate()


if __name__ == '__main__':
    main(sys.argv)
