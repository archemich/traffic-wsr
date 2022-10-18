import argparse

from .version import __version__

def parse_args() ->argparse.Namespace:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version',
                        action='version',
                        version=__version__)
    args = parser.parse_args()
    return args

def main():
    """
    Script entry point
    :return:
    """
    args = parse_args()

    print('hello world')


if __name__ == '__main__':
    main()
