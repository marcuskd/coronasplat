import sys
from os.path import abspath, dirname, join


def get_path(rel_path):

    """
    Returns the path to a data file in both development and deployed modes
    """

    base_path = getattr(sys, '_MEIPASS', dirname(abspath(__file__)))
    full_path = join(base_path, rel_path)

    return full_path
