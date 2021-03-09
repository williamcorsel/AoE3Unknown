from math import sqrt

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