import pygame
import pygame.gfxdraw
import sys
import time
import random
import threading
import Queue

import proceduralGenerator.drawFunctions
import proceduralGenerator.voronoiCalc
import proceduralGenerator.helperFunctions
import xml.etree.cElementTree as ET

from collections import defaultdict
from proceduralGenerator.derandomiser import *
from twitterMiner.analysis import *


##Settings

mapName = "defaultMap"
width = 1200
height = 900
cellCount = 5000
query = "test"

##Main code
#Initiates the window and calls the subfunctions to draw in them

pygame.init()

window = pygame.display.set_mode((width, height))

pygame.display.set_caption('PCG')

q = Queue.Queue()
t1 = threading.Thread(target=analysis, args=(q, query, window, width, height))
t1.start()

#create random coords, performs voronoi tessellation, creates polygon dictionary

coordList = proceduralGenerator.drawFunctions.randomCoordinates(width, height, cellCount)
voronoiList = proceduralGenerator.voronoiCalc.voronoi(coordList)
polySet = proceduralGenerator.drawFunctions.createPolygonSet(voronoiList, cellCount, width, height, 0)

#reloads voronoi, then performs normalisation, recalculates voronoi and polygon dictionary 

proceduralGenerator.voronoiCalc = reload(proceduralGenerator.voronoiCalc)
coordList = derandomiser(coordList, voronoiList, polySet, window, width, height)
voronoiList = proceduralGenerator.voronoiCalc.voronoi(coordList)

#creates various dictionarys for use in creating map

"""
polySet = dictionary with centre points of polygons as keys and all surrounding points as a list for each polygon
polyIndexSet = partner dictionary to polySet, but with indices instead of actual coords (used in making the edgeset)
edgeSet = list of tuples of edge pairs
adjacencyTable = dictionary with each point as the key and all the adjacent polygon centres making up the returns (deals only in indices)
"""

polySet = proceduralGenerator.drawFunctions.createPolygonSet(voronoiList, cellCount, width, height, 1)
polyIndexSet = proceduralGenerator.drawFunctions.createIndexSet(voronoiList, polySet)
edgeSet = proceduralGenerator.drawFunctions.createEdgePairs(polyIndexSet)
adjacencyTable = proceduralGenerator.drawFunctions.createAdjacencyDict(coordList, voronoiList, polySet)

#pulls the twitter data from the other thread

twitterData = q.get()
particleDict = twitterData['particles']
keywordRelationships = twitterData['querykeywords']

t1.join()

particleCoords = {}

for particle in particleDict:

	particleCoords[particle] = particleDict[particle].position

proceduralGenerator.drawFunctions.drawVoronoiEdges(voronoiList, height, width, window, (0, 0, 255))

#Land Shape

print "Shaping the landmass..."
polygonBiome = {}
newParticleCoords = {}

for point in particleCoords:
	for poly in polySet:
		if point_inside_polygon(particleCoords[point], polySet[poly]):
			newParticleCoords[poly] = point

for poly in polySet:
	polygonBiome[poly] = 'ocean'

for poly in newParticleCoords:

	polygonBiome[poly] = 'land'

	currentList = []
	currentList.append(poly)
	currentOdds = random.randrange(7, 10)
	nextList = []
	previousList = []

	while(currentList):
		for poly in currentList:

			try:
				for nextPoly in adjacencyTable[poly]:
					if (random.randrange(0, 5) < currentOdds):
						if nextPoly not in previousList and nextPoly not in currentList:
							polygonBiome[nextPoly] = 'land'
							nextList.append(nextPoly)
			except KeyError:
				pass


		currentOdds -= 1
		previousList = currentList
		currentList = list(set(nextList))
		nextList = []

#un-comment to add some noise to the coasts (to be honest, the landmass generation does a decent enough job of it anyway)

#polygonBiome = proceduralGenerator.helperFunctions.addCoastalNoise(adjacencyTable, polygonBiome, coastalPolygons)

#creates the dictionaries that are used in working out the final elevations of the polygons

coastalPolygons = proceduralGenerator.helperFunctions.checkForCoast(adjacencyTable, polygonBiome)

vertexIndex = {}
vertexElevation = {}
polygonElevation = {}

for coord in range(0, len(voronoiList.vertices)):

	vertexIndex[voronoiList.vertices[coord]] = coord

window.fill((0, 0, 128))

#draws the outline of the landmass

for key in polygonBiome:

	try:

		if polygonBiome[key] == 'ocean':

			pygame.gfxdraw.filled_polygon(window, polySet[key], (0, 0, 128))

		elif polygonBiome[key] == 'lake':

			pygame.gfxdraw.filled_polygon(window, polySet[key], (0, 191, 255))

		elif polygonBiome[key] == 'land':

			pygame.gfxdraw.filled_polygon(window, polySet[key], (0, 255, 0))

	except KeyError:

		pass

pygame.display.flip()

#Elevation

def printPolyDict(dictToPrint):
	for poly in dictToPrint:
		try:
			pygame.gfxdraw.filled_polygon(window, polySet[poly], (255, 255, 255))
		except KeyError:
			pass
	pygame.display.flip()

print "Figuring out heights..."

def elevation():

	visited = []
	currentList = proceduralGenerator.helperFunctions.checkForCoast(adjacencyTable, polygonBiome)
	printPolyDict(currentList)
	for index in currentList:
		for coord in polySet[index]:
			vertexElevation[vertexIndex[coord]] = (random.uniform(0.3, 1.0))

	for item in currentList:
		visited.append(item)

	newList = []
	heightModifier = 1.0
	for index in currentList:
		try:
			for key in adjacencyTable[index]:
				if polygonBiome[key] != 'ocean' and key not in currentList:
					newList.append(key)

		except KeyError:
			pass

	newList = list(set(newList))
	previousList = currentList
	currentList = newList

	while(len(currentList) > 0):
		for item in currentList:
			visited.append(item)
		printPolyDict(currentList)
		newList = []
		for index in currentList:
			for key in adjacencyTable[index]:
				if key not in previousList and key not in currentList:
					try:
						if polygonBiome[key] != 'ocean':
							newList.append(key)
					except KeyError:
						pass

		for polyKey in currentList:
			try:
				for coord in polySet[polyKey]:

					vertexElevation[vertexIndex[coord]] = (heightModifier + random.uniform(0.0, 1.0))

			except KeyError:
				pass

		previousList = currentList
		currentList = list(set(newList))
		heightModifier += 1

def calculatePolygonElevations():

	for key in polySet:
		if polygonBiome[key] == 'land':
			heights = []
			for coord in polySet[key]:
				try:
					heights.append(vertexElevation[vertexIndex[coord]])

				except KeyError:
					pass

			try:
				polygonElevation[key] = sum(heights)/float(len(heights))

			except ZeroDivisionError:
				pass

def normaliseElevations():

	newMax = (1.0)
	newMin = (0.0)

	oldMin = vertexElevation[min(vertexElevation, key=vertexElevation.get)]
	oldMax = vertexElevation[max(vertexElevation, key=vertexElevation.get)]

	OldRange = (oldMax - oldMin)
	NewRange = (newMax - newMin)

	for key in vertexElevation:

		vertexElevation[key] = (((vertexElevation[key] - oldMin) * NewRange) / OldRange) + newMin

elevation()

normaliseElevations()
calculatePolygonElevations()

for poly in polygonElevation:
	try:
		pygame.gfxdraw.filled_polygon(window, polySet[poly], (0, 255, 255))
	except KeyError:
		pass
pygame.display.flip()

#Temperature

print "Working out the temperatures..."

polygonTemperature = {}

centrePoint = height/2

for polygon in polygonBiome:
	if polygonBiome[polygon] == 'land':
		x = coordList[polygon][1]
		if x > centrePoint:
			distanceFromEquator = x-centrePoint
		elif x <= centrePoint:
			distanceFromEquator = centrePoint - x

		tempRatio = float(distanceFromEquator)/float(centrePoint)
		locationTemp = 1 - (tempRatio*tempRatio)

		try:
			heightTemp = 1 - polygonElevation[polygon]
		except KeyError:
			pass
		polygonTemperature[polygon] = (locationTemp*0.4)+(heightTemp)

def normaliseTemps():

	newMax = (1.0)
	newMin = (0.0)

	oldMin = polygonTemperature[min(polygonTemperature, key=polygonTemperature.get)]
	oldMax = polygonTemperature[max(polygonTemperature, key=polygonTemperature.get)]

	OldRange = (oldMax - oldMin)
	NewRange = (newMax - newMin)

	for key in polygonTemperature:

		polygonTemperature[key] = (((polygonTemperature[key] - oldMin) * NewRange) / OldRange) + newMin

normaliseTemps()

#Moisture

print "Calculating Moisture Values..."

moistureDict = {}

def moistureCalc():

	waterAdjacentPolygons = []

	for key in polygonBiome:

		coast = 0

		if (polygonBiome[key] =='land'):
			try:
				for adjacents in adjacencyTable[key]:
					if polygonBiome[adjacents] == 'ocean' or polygonBiome[adjacents] == 'lake':
						coast = 1

			except KeyError:
				pass

		if coast == 1:
			waterAdjacentPolygons.append(key)

	visited = []
	currentList = waterAdjacentPolygons
	for index in currentList:
		moistureDict[index] = (random.uniform(40.0, 41.0))

	for item in currentList:
		visited.append(item)

	newList = []
	heightModifier = 12.0
	for index in currentList:
		try:
			for key in adjacencyTable[index]:
				if polygonBiome[key] != 'ocean' and polygonBiome[key] != 'lake' and key not in currentList:
					newList.append(key)

		except KeyError:
			pass

	newList = list(set(newList))
	previousList = currentList
	currentList = newList

	while(len(currentList) > 0):
		for item in currentList:
			visited.append(item)

		newList = []
		for index in currentList:
			try:
				for key in adjacencyTable[index]:
					if key not in previousList and key not in currentList and polygonBiome[key] != 'ocean':
						newList.append(key)

			except KeyError:
				pass

		for polyKey in currentList:
			try:

				moistureDict[polyKey] = (random.uniform(40.0, 41.0) - heightModifier)

			except KeyError:
				pass

		previousList = currentList
		currentList = list(set(newList))
		heightModifier += 1

def normaliseMoistureValues():

	newMax = (1.0)
	newMin = (0.0)

	oldMin = moistureDict[min(moistureDict, key=moistureDict.get)]
	oldMax = moistureDict[max(moistureDict, key=moistureDict.get)]

	OldRange = (oldMax - oldMin)
	NewRange = (newMax - newMin)

	for key in moistureDict:

		moistureDict[key] = (((moistureDict[key] - oldMin) * NewRange) / OldRange) + newMin

moistureCalc()
normaliseMoistureValues()

#BiomeAssignment

print "Creating Biomes..."

landPolygons = []

def biomeAssigner():

	for poly in polygonBiome:
		if polygonBiome[poly] == 'land':

			try:
				if moistureDict[poly] >= 0 and moistureDict[poly] <= 0.1:
					if polygonTemperature[poly] >= 0 and polygonTemperature[poly] <= 0.35:
						polygonBiome[poly] = 'Tundra'

					if polygonTemperature[poly] > 0.35 and polygonTemperature[poly] <= 0.7:
						polygonBiome[poly] = 'Grassland'

					if polygonTemperature[poly] > 0.7 and polygonTemperature[poly] <= 1.0:
						polygonBiome[poly] = 'Desert'

				if moistureDict[poly] > 0.1 and moistureDict[poly] <= 0.2:
					if polygonTemperature[poly] >= 0 and polygonTemperature[poly] <= 0.35:

						polygonBiome[poly] = 'Tundra'
					if polygonTemperature[poly] > 0.35 and polygonTemperature[poly] <= 0.5:

						polygonBiome[poly] = 'Grassland'
					if polygonTemperature[poly] > 0.5 and polygonTemperature[poly] <= 0.9:

						polygonBiome[poly] = 'Temperate Seasonal Forest'
					if polygonTemperature[poly] > 0.9 and polygonTemperature[poly] <= 1.0:

						polygonBiome[poly] = 'Desert'
				if moistureDict[poly] > 0.2 and moistureDict[poly] <= 0.3:

					if polygonTemperature[poly] >= 0 and polygonTemperature[poly] <= 0.5:
						polygonBiome[poly] = 'Taiga'

					if polygonTemperature[poly] > 0.5 and polygonTemperature[poly] <= 0.95:
						polygonBiome[poly] = 'Grassland'

					if polygonTemperature[poly] > 0.95 and polygonTemperature[poly] <= 1.0:
						polygonBiome[poly] = 'Desert'

				if moistureDict[poly] > 0.3 and moistureDict[poly] <= 0.5:
					if polygonTemperature[poly] >= 0 and polygonTemperature[poly] <= 0.35:

						polygonBiome[poly] = 'Taiga'
					if polygonTemperature[poly] > 0.35 and polygonTemperature[poly] <= 0.6:

						polygonBiome[poly] = 'Grassland'
					if polygonTemperature[poly] > 0.6 and polygonTemperature[poly] <= 1:

						polygonBiome[poly] = 'Temperate Seasonal Forest'
				if moistureDict[poly] > 0.5 and moistureDict[poly] <= 0.8:

					if polygonTemperature[poly] >= 0 and polygonTemperature[poly] <= 0.35:
						polygonBiome[poly] = 'Taiga'

					if polygonTemperature[poly] > 0.35 and polygonTemperature[poly] <= 0.6:
						polygonBiome[poly] = 'Temperate Deciduous Forest'

					if polygonTemperature[poly] > 0.6 and polygonTemperature[poly] <= 1.0:
						polygonBiome[poly] = 'Temperate Seasonal Forest'

				if moistureDict[poly] > 0.8 and moistureDict[poly] <= 0.85:
					if polygonTemperature[poly] >= 0 and polygonTemperature[poly] <= 0.2:

						polygonBiome[poly] = 'Snow'
					if polygonTemperature[poly] > 0.2 and polygonTemperature[poly] <= 0.35:

						polygonBiome[poly] = 'Taiga'
					if polygonTemperature[poly] > 0.35 and polygonTemperature[poly] <= 0.6:

						polygonBiome[poly] = 'Temperate Rain Forest'
					if polygonTemperature[poly] > 0.6 and polygonTemperature[poly] <= 1.0:

						polygonBiome[poly] = 'Tropical Rain Forest'
				if moistureDict[poly] > 0.85 and moistureDict[poly] <= 1.0:

					if polygonTemperature[poly] >= 0 and polygonTemperature[poly] <= 0.4:
						polygonBiome[poly] = 'Snow'

					if polygonTemperature[poly] > 0.4 and polygonTemperature[poly] <= 0.5:
						polygonBiome[poly] = 'Tundra'

					if polygonTemperature[poly] > 0.5 and polygonTemperature[poly] <= 0.6:
						polygonBiome[poly] = 'Temperate Rain Forest'

					if polygonTemperature[poly] > 0.6 and polygonTemperature[poly] <= 1.0:
						polygonBiome[poly] = 'Tropical Rain Forest'

				if moistureDict[poly] < 0 or moistureDict[poly] > 1:
					print "Moisture:"
					print moistureDict[poly]

				if polygonTemperature[poly] < 0 or polygonTemperature[poly] > 1:
					print "Temp:"
					print polygonTemperature[poly]
				landPolygons.append(poly)
			except KeyError:
				polygonBiome[poly] = 'ocean'

coastalPolygons = proceduralGenerator.helperFunctions.checkForCoast(adjacencyTable, polygonBiome)

biomeAssigner()

#Rendering

print "Drawing biomes"

for key in polygonBiome:

	try:

		if polygonBiome[key] == 'ocean':

			pygame.gfxdraw.filled_polygon(window, polySet[key], (0, 0, 128))

		elif polygonBiome[key] == 'lake':

			pygame.gfxdraw.filled_polygon(window, polySet[key], (0, 191, 255))

		elif polygonBiome[key] == 'land':

			pygame.gfxdraw.filled_polygon(window, polySet[key], (255, 0, 0))

	except KeyError:

		pass

	proceduralGenerator.drawFunctions.drawBiomes(window, polygonBiome, polySet)


for poly in coastalPolygons:

	pygame.gfxdraw.filled_polygon(window, polySet[poly], (120, 200, 140))

print "Biomes drawn"

proceduralGenerator.drawFunctions.drawVoronoiEdges(voronoiList, height, width, window, (0, 0, 0))
proceduralGenerator.drawFunctions.drawPointSet(coordList, window)

pygame.display.flip()

for poly in polySet:

	if poly not in polygonElevation:
		polygonElevation[poly] = 0.0

	if poly not in polygonTemperature:
		polygonTemperature[poly] = 0.0

	if poly not in moistureDict:
		moistureDict[poly] = 1.0

for vertex in range(0, len(voronoiList.vertices)):

	if vertex not in vertexElevation:
		vertexElevation[vertex] = 0.0


##XML Generation Code

map = ET.Element("map")

map.set("height", str(height))
map.set("width", str(width))
map.set("polygons", str(cellCount))

polygons = ET.SubElement(map, "polygons")

for poly in polySet:

	polygon  = ET.SubElement(polygons, "polygon")
	polygon.set("id", str(poly))

	polygon.set("x", str(coordList[poly][0]))
	polygon.set("y", str(coordList[poly][1]))
	polygon.set("Biome", str(polygonBiome[poly]))
	polygon.set("Elevation", str(polygonElevation[poly]))
	polygon.set("Temperature", str(polygonTemperature[poly]))
	polygon.set("Moisture", str(moistureDict[poly]))

	verticeIDs = ET.SubElement(polygon, "ids")

	for index in polyIndexSet[poly]:

		vertexID = ET.SubElement(verticeIDs, "id")
		vertexID.text = str(index)

edges = ET.SubElement(map, "edges")

for currentEdge in edgeSet:

	edge = ET.SubElement(edges, "edge")

	verticeIDs = ET.SubElement(edge, "ids")

	vertexID = ET.SubElement(verticeIDs, "id")
	vertexID.text = str(currentEdge[0])
	vertexID = ET.SubElement(verticeIDs, "id")
	vertexID.text = str(currentEdge[1])

vertices = ET.SubElement(map, "vertices")

for vertice in range(0, len(voronoiList.vertices)):

	vertex = ET.SubElement(vertices, "vertex")
	vertex.set("id", str(vertice))
	vertex.set("x", str(voronoiList.vertices[vertice][0]))
	vertex.set("y", str(voronoiList.vertices[vertice][1]))
	vertex.set("Elevation", str(vertexElevation[vertice]))

tree = ET.ElementTree(map)
tree.write(mapName + ".xml")

#event code to keep window running

def displayHeatmap():
	for poly in polygonTemperature:
		colourTemp = 255*polygonTemperature[poly]
		pygame.gfxdraw.filled_polygon(window, polySet[poly], (colourTemp, 0, 255 - colourTemp))
	pygame.display.flip()

running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_h:
				displayHeatmap()
		if event.type == pygame.QUIT:
			running = False
