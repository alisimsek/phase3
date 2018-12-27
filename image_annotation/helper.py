from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import math

def insideRectangle(x,y,rect):
    if (x >= rect[1] and x <= rect[3]) or (x <= rect[1] and x >= rect[3]):
        if (y >= rect[2] and y <= rect[4]) or (y <= rect[2] and y >= rect[4]):
            return True

    return False

def insideCircle(x,y,circ):
    center_x = circ[1]
    center_y = circ[2]
    radius = circ[3]
    if math.sqrt((x - center_x)**2 + (y - center_y)**2) <= radius:
        return True
    else:
        return False


def insidePolyline(x,y,polyline):
    points = polyline[1]
    polygon = Polygon(points)
    point = Point(x,y)
    return polygon.contains(point)

def matchGroup(user,rule):
    u = UserGroup()
    userGroups = u.getGroups(user)
    for group in userGroups:
        if re.fullmatch(rule[0],group):
            return True

    return False
