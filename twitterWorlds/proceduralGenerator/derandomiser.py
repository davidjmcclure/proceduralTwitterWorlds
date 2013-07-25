import pygame

from helperFunctions import *

def derandomiser(coordList, voronoiList, polyList, window, width, height):

	newPolySet = {}
	derandomCoordList = []

	for coord in polyList:
		edgeSet = []

		if len(polyList[coord]) >= 3:

			for edgeCoord in polyList[coord]:

				if edgeCoord[0] <= width and edgeCoord[0] >= 0 and edgeCoord[1] <= height and edgeCoord[1] >= 0:

					edgeSet.append(edgeCoord)

				else:

					edgeSet = []
					edgeSet.append(coordList[coord])
					break

			newPolySet[coord] = edgeSet

		elif len(polyList[coord]) <= 2:

			derandomCoordList.append(coordList[coord])

	for coord in newPolySet:

		derandomCoordList.append(centroidCalc(newPolySet[coord]))

	return derandomCoordList

def coordinateLinker(coordList, polySet):

	centreCoordDict = {}

	for coord2 in coordList:

		for coord in polySet:

			if point_inside_polygon(coord2, polySet[coord]):

				centreCoordDict[coord] = coord2
				break

		print coord

	return centreCoordDict
