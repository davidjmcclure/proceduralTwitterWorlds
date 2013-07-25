import pygame
import sys
import voronoiCalc
import random

from math import sqrt
from collections import defaultdict
from helperFunctions import *

##Draw functions:

#randomCoordinates - Function that, given a window height and width, and the number of desired cells, will return a list of coordinates
#drawPointSet- draws the points in the current coordlist
#drawVoronoiEdges- draws all the line edges of the voronoi polygons
#drawDelauneyTriangles- draws the delauney triangles (most likely not used)
#createPolygonSet - returns a dictionary of each polygon and its vertices (vertices are in order)

def randomCoordinates(width, height, cellCount):

	cellCoordinates = []

	while len(cellCoordinates) < cellCount:

		coord = (random.randint(0, width), random.randint(0, height))
		if coord not in cellCoordinates:
			cellCoordinates.append(coord)

	return cellCoordinates

def drawPointSet(coordList, window):

	for coord in coordList:

		pygame.draw.line(window, (0, 0, 0), coord, coord)

	pygame.display.flip()

def drawVoronoiEdges(voronoiList, height, width, window, colour):

	north = (0.0, 1.0, float(height))
	east = (1.0, 0.0, float(width))
	south = (0.0, 1.0, 0.0)
	west = (1.0, 0.0, 0.0)

	for edge in range(0, len(voronoiList.edges)):

		#First if draws the edges for any lines not at the edge

		if voronoiList.edges[edge][1] != -1 and voronoiList.edges[edge][2] != -1:

			p1 = voronoiList.vertices[voronoiList.edges[edge][1]]
			p2 = voronoiList.vertices[voronoiList.edges[edge][2]]
			pygame.draw.line(window, colour, p1, p2)

		#next two if statements handle edge cases (by using the 
		#formula of the line that's given and calculating intersections)

		elif voronoiList.edges[edge][1] == -1:

			line = voronoiList.lines[voronoiList.edges[edge][0]]

			line1 = intersectionCalc(line, north)
			line2 = intersectionCalc(line, east)
			line3 = intersectionCalc(line, south)
			line4 = intersectionCalc(line, west)

			dist1 = distance(voronoiList.vertices[voronoiList.edges[edge][2]], line1)
			dist2 = distance(voronoiList.vertices[voronoiList.edges[edge][2]], line2)
			dist3 = distance(voronoiList.vertices[voronoiList.edges[edge][2]], line3)
			dist4 = distance(voronoiList.vertices[voronoiList.edges[edge][2]], line4)

			edgeCase = min([dist1, dist2, dist3, dist4])

			if edgeCase == dist1:

				pygame.draw.line(window, colour, line1, voronoiList.vertices[voronoiList.edges[edge][2]])
				voronoiList.vertices.append(line1)
				voronoiList.edges[edge] = (voronoiList.edges[edge][0], voronoiList.vertices.index(line1), voronoiList.edges[edge][2])

			elif edgeCase == dist2:

				pygame.draw.line(window, colour, line2, voronoiList.vertices[voronoiList.edges[edge][2]])
				voronoiList.vertices.append(line2)
				voronoiList.edges[edge] = (voronoiList.edges[edge][0], voronoiList.vertices.index(line2), voronoiList.edges[edge][2])

			elif edgeCase == dist3:

				pygame.draw.line(window, colour, line3, voronoiList.vertices[voronoiList.edges[edge][2]])
				voronoiList.vertices.append(line3)
				voronoiList.edges[edge] = (voronoiList.edges[edge][0], voronoiList.vertices.index(line3), voronoiList.edges[edge][2])

			elif edgeCase == dist4:

				pygame.draw.line(window, colour, line4, voronoiList.vertices[voronoiList.edges[edge][2]])
				voronoiList.vertices.append(line4)
				voronoiList.edges[edge] = (voronoiList.edges[edge][0], voronoiList.vertices.index(line4), voronoiList.edges[edge][2])

		elif voronoiList.edges[edge][2] == -1:

			line = voronoiList.lines[voronoiList.edges[edge][0]]

			line1 = intersectionCalc(line, north)
			line2 = intersectionCalc(line, east)
			line3 = intersectionCalc(line, south)
			line4 = intersectionCalc(line, west)

			dist1 = distance(voronoiList.vertices[voronoiList.edges[edge][1]], line1)
			dist2 = distance(voronoiList.vertices[voronoiList.edges[edge][1]], line2)
			dist3 = distance(voronoiList.vertices[voronoiList.edges[edge][1]], line3)
			dist4 = distance(voronoiList.vertices[voronoiList.edges[edge][1]], line4)

			edgeCase = min([dist1, dist2, dist3, dist4])

			if edgeCase == dist1:

				pygame.draw.line(window, colour, line1, voronoiList.vertices[voronoiList.edges[edge][1]])
				voronoiList.vertices.append(line1)
				voronoiList.edges[edge] = (voronoiList.edges[edge][0], voronoiList.edges[edge][1], voronoiList.vertices.index(line1))

			elif edgeCase == dist2:

				pygame.draw.line(window, colour, line2, voronoiList.vertices[voronoiList.edges[edge][1]])
				voronoiList.vertices.append(line2)
				voronoiList.edges[edge] = (voronoiList.edges[edge][0], voronoiList.edges[edge][1], voronoiList.vertices.index(line2))

			elif edgeCase == dist3:

				pygame.draw.line(window, colour, line3, voronoiList.vertices[voronoiList.edges[edge][1]])
				voronoiList.vertices.append(line3)
				voronoiList.edges[edge] = (voronoiList.edges[edge][0], voronoiList.edges[edge][1], voronoiList.vertices.index(line3))

			elif edgeCase == dist4:

				pygame.draw.line(window, colour, line4, voronoiList.vertices[voronoiList.edges[edge][1]])
				voronoiList.vertices.append(line4)
				voronoiList.edges[edge] = (voronoiList.edges[edge][0], voronoiList.edges[edge][1], voronoiList.vertices.index(line4))

	pygame.display.flip()

def drawDelauneyTriangles(coordList, window):

	for triangle in voronoiList.triangles:
		t1 = coordList[triangle[0]]
		t2 = coordList[triangle[1]]
		t3 = coordList[triangle[2]]

		pygame.draw.line(window, (255, 0, 0), t1, t2)
		pygame.draw.line(window, (255, 0, 0), t2, t3)
		pygame.draw.line(window, (255, 0, 0), t3, t1)

	pygame.display.flip()

def createPolygonSet(voronoiObject, cellCount, width, height, normalCheck):

	c = voronoiObject

	# For each point find triangles (vertices) of a cell
	point_in_triangles = defaultdict(set)
	for t_ind, ps in enumerate(c.triangles):
		for p in ps:
			point_in_triangles[p].add(t_ind)

	# Vertex connectivity graph
	vertex_graph = defaultdict(set)
	for e_ind, (_, r, l) in enumerate(c.edges):
		vertex_graph[r].add(l)
		vertex_graph[l].add(r)

	def cell(point):
		if point not in point_in_triangles:
			return None
		vertices = set(point_in_triangles[point]) # copy
		v_cell = [vertices.pop()]
		vertices.add(-1)  # Simulate infinity :-)
		while vertices:
			neighbours = vertex_graph[v_cell[-1]] & vertices
			if not neighbours:
				break
			v_cell.append(neighbours.pop())
			vertices.discard(v_cell[-1])
		return v_cell

	polygonDict = {}
	newPolySet = {}
	newNewPolySet = {}

	for p in xrange(cellCount):
		polygonList = cell(p)
		polygonDict[p] = polygonList

	for coord in polygonDict:

		coordList = []

		for edgeCoord in polygonDict[coord]:

			coordList.append(c.vertices[edgeCoord])

		newPolySet[coord] = coordList

	if normalCheck == 1:

		for poly in newPolySet:
			check = 0
			for point in range(0, len(newPolySet[poly])):
				try:
					if distance(newPolySet[poly][point], newPolySet[poly][point + 1]) > height/2:
						check = check + 1

				except IndexError:
					if distance(newPolySet[poly][point], newPolySet[poly][0]) > height/2:
						check = check + 1

			if check == 0:
				newNewPolySet[poly] = newPolySet[poly]

		return newNewPolySet

	elif normalCheck == 0:
		return newPolySet

def createAdjacencyDict(coordList, voronoiList, polySet):

	adjacencyDict = {}
	for triangle in voronoiList.triangles:
		for point in range(0, len(triangle)):
			if triangle[point] in adjacencyDict:
				if point == 0:
					adjacencyDict[triangle[point]].append(triangle[1])
					adjacencyDict[triangle[point]].append(triangle[2])

				elif point == 1:
					adjacencyDict[triangle[point]].append(triangle[0])
					adjacencyDict[triangle[point]].append(triangle[2])

				elif point == 2:
					adjacencyDict[triangle[point]].append(triangle[0])
					adjacencyDict[triangle[point]].append(triangle[1])

			elif triangle[point] not in adjacencyDict:
				adjacencyDict[triangle[point]] = []
				if point == 0:
					adjacencyDict[triangle[point]].append(triangle[1])
					adjacencyDict[triangle[point]].append(triangle[2])

				elif point == 1:
					adjacencyDict[triangle[point]].append(triangle[0])
					adjacencyDict[triangle[point]].append(triangle[2])

				elif point == 2:
					adjacencyDict[triangle[point]].append(triangle[0])
					adjacencyDict[triangle[point]].append(triangle[1])

	for adjacencyList in adjacencyDict:
		adjacencyDict[adjacencyList] = list(set(adjacencyDict[adjacencyList]))

	adjacencyDict2 = {}
	for key in adjacencyDict:
		if key in polySet:
			adjacencyDict2[key] = adjacencyDict[key]

	adjacencyDict3 = {}
	for key in adjacencyDict2:
		tempList = []
		for index in adjacencyDict2[key]:
			if index in polySet:
				tempList.append(index)
			adjacencyDict3[key] = tempList

	return adjacencyDict3

def createIndexSet(voronoiObject, polySet):

	indexSet = {}
	for poly in polySet:
		indexSet[poly] = []
		for coord in range(0, len(polySet[poly])):
			indexSet[poly].append(voronoiObject.vertices.index(polySet[poly][coord]))

	return indexSet

def createEdgePairs(polySet):

	edgeSets = []
	for poly in polySet:
		for point in range(0, len(polySet[poly])):
			try:
				edge = (polySet[poly][point], polySet[poly][point+1])

			except IndexError:
				edge = (polySet[poly][point], polySet[poly][0])

			edgeSets.append(edge)

	return edgeSets

def drawBiomes(window, biomeDict, polygonDict):

	biomeColour = {}

	for poly in biomeDict:
		if biomeDict[poly] != 'ocean':

			polygon = polygonDict[poly]

			try:
				if biomeDict[poly] == "Snow":
					biomeColour[poly] = (255, 255, 255)
#					pygame.gfxdraw.filled_polygon(window, polygonDict[poly], (255, 255, 255))

				elif biomeDict[poly] == "Tundra":
					biomeColour[poly] = (112, 138, 144)
#					pygame.gfxdraw.filled_polygon(window, polygonDict[poly], (112, 138, 144))

				elif biomeDict[poly] == "Taiga":
					biomeColour[poly] = (34, 139, 34)
#					pygame.gfxdraw.filled_polygon(window, polygonDict[poly], (34, 139, 34))

				elif biomeDict[poly] == "Temperate Rain Forest":
					biomeColour[poly] = (50, 170, 162)
#					pygame.gfxdraw.filled_polygon(window, polygonDict[poly], (50, 170, 162))

				elif biomeDict[poly] == "Tropical Rain Forest":
					biomeColour[poly] = (90, 200, 120)
#					pygame.gfxdraw.filled_polygon(window, polygonDict[poly], (90, 200, 120))

				elif biomeDict[poly] == "Temperate Seasonal Forest":
					biomeColour[poly] = (40, 180, 35)
#					pygame.gfxdraw.filled_polygon(window, polygonDict[poly], (40, 180, 35))

				elif biomeDict[poly] == "Temperate Deciduous Forest":
					biomeColour[poly] = (46, 177, 83)
#					pygame.gfxdraw.filled_polygon(window, polygonDict[poly], (46, 177, 83))

				elif biomeDict[poly] == "Grassland":
					biomeColour[poly] = (66, 197, 103)
#					pygame.gfxdraw.filled_polygon(window, polygonDict[poly], (66, 197, 103))

				elif biomeDict[poly] == "Desert":
					biomeColour[poly] = (250, 219, 7)
#					pygame.gfxdraw.filled_polygon(window, polygonDict[poly], (250, 219, 7))

			except KeyError:
				pass

	for poly in biomeColour:

		pygame.gfxdraw.filled_polygon(window, polygonDict[poly], biomeColour[poly])

