import math

def distance_2d(p1, p2):
    """Calculate 2D Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def midpoint(p1, p2):
    """Return the midpoint between two 2D points."""
    return [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]

def are_points_close(p1, p2, tolerance=0.01):
    """Check if two points are approximately equal within a tolerance."""
    return distance_2d(p1, p2) < tolerance