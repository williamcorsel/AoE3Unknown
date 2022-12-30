from math import sqrt
import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller

    Args:
        relative_path (str): Relative path to resource

    Returns:
        str: Absolute path to resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def dist(p1, p2):
    """Calculate distance between two points

    Args:
        p1 (tuple): Point 1
        p2 (tuple): Point 2

    Returns:
        float: Distance between points
    """
    dy = p1[0] - p2[0]
    dx = p1[1] - p2[1]
    return sqrt( dy*dy + dx*dx )



def midpoint(p1, p2):
    """Get midpoint coordinate between two points

    Args:
        p1 (tuple): Point 1
        p2 (tuple): Point 2

    Returns:
        tuple: Midpoint coordinate
    """
    return [int((p1[0] + p2[0])/2), int((p1[1] + p2[1])/2)]