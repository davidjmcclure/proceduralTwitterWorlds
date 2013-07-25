from math import sqrt
import math
import sys
import random


##Helper Functions:

# distance- calculate distance between two points
# intersectionalCalc- calculate point of intersection of two lines

def distance(p1, p2):
	dist = sqrt( (float(p2[0]) - float(p1[0]))**2 + (float(p2[1]) - float(p1[1]))**2 )
	return dist

def intersectionCalc(line1, line2):
	#a*x + b*y = c
	#d*x + e*y = f

	a = line1[0]
	b = line1[1]
	c = line1[2]

	d = line2[0]
	e = line2[1]
	f = line2[2]

	try:
		x = (c*e - b*f) / (a*e - b*d)

	except ZeroDivisionError:
		x = sys.maxint

	try:
		y = (a*f - c*d) / (a*e - b*d)

	except ZeroDivisionError:
		y = sys.maxint

	line = (x, y)
	return line

def centroidCalc(pointList):

	if len(pointList) == 1:
		centroid = (int(pointList[0][0]),int(pointList[0][1]))

	else:
		A = 0.0
		Cx = 0.0
		Cy = 0.0
		for point in range(0, len(pointList)):
			try:
				A = A + ((pointList[point][0]*pointList[point+1][1]) - (pointList[point+1][0]*pointList[point][1]))

			except IndexError:
				A = A + ((pointList[point][0]*pointList[0][1]) - (pointList[0][0]*pointList[point][1]))

		A = A*0.5
		for point in range(0, len(pointList)):
			try:
				Cx = Cx + ((pointList[point][0] + pointList[point+1][0]) * ((pointList[point][0]*pointList[point+1][1]) - (pointList[point+1][0]*pointList[point][1])))

			except IndexError:
				Cx = Cx + ((pointList[point][0] + pointList[0][0]) * ((pointList[point][0]*pointList[0][1]) - (pointList[0][0]*pointList[point][1])))

			try:
				Cy = Cy + ((pointList[point][1] + pointList[point+1][1]) * ((pointList[point][0]*pointList[point+1][1]) - (pointList[point+1][0]*pointList[point][1])))

			except IndexError:
				Cy = Cy + ((pointList[point][1] + pointList[0][1]) * ((pointList[point][0]*pointList[0][1]) - (pointList[0][0]*pointList[point][1])))

		try:
			Cx = Cx * (1.0/(6.0*A))

		except ZeroDivisionError:
			Cx = Cx * (1.0/0.1)

		try:
			Cy = Cy * (1.0/(6.0*A))

		except ZeroDivisionError:
			Cy = Cy * (1.0/0.1)

		if Cx == 0.0:
			print A
			print pointList

		centroid = (int(Cx), int(Cy))

	return centroid

def point_inside_polygon(point, poly):

	x = point[0]
	y = point[1]

	n = len(poly)
	inside =False

	p1x,p1y = poly[0]
	for i in range(n+1):
		p2x,p2y = poly[i % n]
		if y > min(p1y,p2y):
			if y <= max(p1y,p2y):
				if x <= max(p1x,p2x):
					if p1y != p2y:
						xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x

					if p1x == p2x or x <= xinters:
						inside = not inside

		p1x,p1y = p2x,p2y

	return inside

def angleBetweenTwoPoints(p1, p2):

	p3 = (p1[0], p1[1] + 2)

	a = (p1[0] - p2[0], p1[1] - p2[1])
	b = (p1[0] - p3[0], p1[1] - p3[1])

	theta = ((a[0]*b[0]) + (a[1]*b[1]))
	theta = theta / (sqrt((a[0]*a[0]) + (a[1]*a[1])) * sqrt((b[0]*b[0]) + (b[1]*b[1])))
	theta = math.acos(theta)

	return theta

TURN_LEFT, TURN_RIGHT, TURN_NONE = (1, -1, 0)

def turn(p, q, r):
	"""Returns -1, 0, 1 if p,q,r forms a right, straight, or left turn."""
	return cmp((q[0] - p[0])*(r[1] - p[1]) - (r[0] - p[0])*(q[1] - p[1]), 0)

def _dist(p, q):
	"""Returns the squared Euclidean distance between p and q."""
	dx, dy = q[0] - p[0], q[1] - p[1]
	return dx * dx + dy * dy

def _next_hull_pt(points, p):
	"""Returns the next point on the convex hull in CCW from p."""
	q = p
	for r in points:
		t = turn(p, q, r)
		if t == TURN_RIGHT or t == TURN_NONE and _dist(p, r) > _dist(p, q):
			q = r
	return q

def convex_hull(points):
	"""Returns the points on the convex hull of points in CCW order."""
	hull = [min(points)]
	for p in hull:
		q = _next_hull_pt(points, p)
		if q != hull[0]:
			hull.append(q)
	return hull

def checkForCoast(adjacencyDict, polygonBiome):

	coastalPolygons = []
	for key in polygonBiome:
		coast = 0
		if (polygonBiome[key] =='land'):
			try:
				for adjacents in adjacencyDict[key]:
					if polygonBiome[adjacents] == 'ocean':
						coast = 1
			except KeyError:
				pass
		if coast == 1:
			coastalPolygons.append(key)

	return coastalPolygons

def addCoastalNoise(adjacencyDict, polygonBiome, coastalPolygons):

	for key in coastalPolygons:
		if (random.randrange(0, 2) == 0):
			polygonBiome[key] = 'ocean'
			for adjacents in adjacencyDict[key]:
				if adjacents not in coastalPolygons:
					if (random.randrange(0, 10) < 4):
						polygonBiome[adjacents] = 'ocean'

		else:
			for adjacents in adjacencyDict[key]:
				if (random.randrange(0, 10) < 4):
					polygonBiome[adjacents] = 'land'

	return polygonBiome

def lakeGenerate(adjacencyDict, polygonBiome, polygonKey):

	oceans = 0
	for adjPoly in adjacencyDict[polygonKey]:
		if polygonBiome[adjPoly] == 'ocean':
			oceans = 1

	if oceans == 0:
		polygonBiome[polygonKey] = 'lake'

	currentList = adjacencyDict[polygonKey]
	currentOdds = 5
	nextList = []

	while(currentList):
		for poly in currentList:
			for nextPoly in adjacencyDict[poly]:
				if (random.randrange(0, 10) < currentOdds):
					oceans = 0

					for adjPoly in adjacencyDict[nextPoly]:
						if polygonBiome[adjPoly] == 'ocean':
							oceans = 1

					if oceans == 0 and polygonBiome[nextPoly] != 'lake':
						polygonBiome[nextPoly] = 'lake'
						nextList.append(nextPoly)

		currentOdds -= 1
		currentList = nextList
		nextList = []

	return polygonBiome



