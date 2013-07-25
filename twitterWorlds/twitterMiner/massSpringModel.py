import sys
import math
import random
import pygame
import pygame.gfxdraw
import operator

class Particle:

	def __init__(self, name, mass, position, velocity, force):

		self.name = name
		self.mass = mass
		self.position, self.velocity, self.force = position, velocity, force

	@property
	def acceleration(self):
		return self.force / self.mass

class Spring:

	def __init__(self, edgeA, edgeB, springConstant, dampingConstant, restLength):

		self.edgeA, self.edgeB = edgeA, edgeB
		self.springConstant, self.dampingConstant, self.restLength = springConstant, dampingConstant, restLength

class ParticleDerivatives:

	def __init__(self, dpdt, dvdt):

		self.dpdt, self.dvdt = dpdt, dvdt

class ParticlePhys:

	def __init__(self, gravitational, viscousdrag):

		self.gravitational, self.viscousdrag = gravitational, viscousdrag

def normaliseRelationships(keywordRelationships):

	keywordRelationships2 = []
	keywordRelationships3 = []
	keywordRelationships4 = []

	for item in keywordRelationships:

		keywordRelationships4.append((item[0], item[1], float(-1 * item[2])))

	maximum = map(max, zip(*keywordRelationships4))[2]
	minimum = map(min, zip(*keywordRelationships4))[2]

	for item in keywordRelationships4:

		keywordRelationships2.append((item[0], item[1], float(item[2] + math.sqrt(minimum*minimum))))

	maximum = map(max, zip(*keywordRelationships2))[2]
	minimum = map(min, zip(*keywordRelationships2))[2]

	NewMax = 800.0
	NewMin = 200.0

	OldRange = (maximum - minimum)
	NewRange = (NewMax - NewMin)

	for item in keywordRelationships2:

		newValue = (((item[2] - minimum) * NewRange) / OldRange) + NewMin
		keywordRelationships3.append((item[0], item[1], newValue))

	return keywordRelationships3

def normaliseFinalCoords(width, height, particleDict):

	particleCoords = {}

	for key in particleDict:
		particleCoords[key] = particleDict[key].position

	newMaxX = (width*0.9)
	newMinX = (width - (width*0.9))

	minX = min(particleCoords.iteritems(),key = lambda x: x[1][0])[1][0]
	maxX = max(particleCoords.iteritems(),key = lambda x: x[1][0])[1][0]

	OldRangeX = (maxX - minX)
	NewRangeX = (newMaxX - newMinX)

	newMaxY = (height*0.9)
	newMinY = (height - (height*0.9))

	minY = min(particleCoords.iteritems(),key = lambda x: x[1][1])[1][1]
	maxY = max(particleCoords.iteritems(),key = lambda x: x[1][1])[1][1]

	OldRangeY = (maxY - minY)
	NewRangeY = (newMaxY - newMinY)

	for key in particleCoords:

		newValueX = (((particleCoords[key][0] - minX) * NewRangeX) / OldRangeX) + newMinX
		newValueY = (((particleCoords[key][1] - minY) * NewRangeY) / OldRangeY) + newMinY


		particleDict[key].position = (newValueX, newValueY)

	return particleDict

def createParticles(keywordRelationships):

	height = 900
	width = 1200

	uniqueWordList = []

	for word in keywordRelationships:

		uniqueWordList.append(word[0])
		uniqueWordList.append(word[1])

	uniqueWordList = list(set(uniqueWordList))

	particleDict = {}

	for item in uniqueWordList:

		name = item
		mass = 1.0
		position = (float(random.randint(0 + (width/10), width - (width/10))), float(random.randint(0 + (height/10), height - (height/10))))
		velocity = (0.0, 0.0)
		force = (0.0, 0.0)

		p1 = Particle(name, mass, position, velocity, force)
		particleDict[name] = p1

	return particleDict

def createSprings(keywordRelationships):

	springList = []

	for item in keywordRelationships:

		edgeA = item[0]
		edgeB = item[1]
		springConstant = 0.1
		dampingConstant = 0.01
		restLength = item[2]

		s1 = Spring(edgeA, edgeB, springConstant, dampingConstant, restLength)
		springList.append(s1)

	return springList

def createDerivatives(particleDict):

	derivativeDict = {}

	for item in particleDict:

		dpdt = particleDict[item].velocity
		dvdt = (particleDict[item].force[0]/particleDict[item].mass, particleDict[item].force[1]/particleDict[item].mass)

		p1 = ParticleDerivatives(dpdt, dvdt)
		derivativeDict[item] = p1

	return derivativeDict

def forceCalculations(particleDict, springList, physicsProperties):

	for key in particleDict:

		forceX = 0.0
		forceY = 0.0

		#gravity (not used, although could potentially be added, with one point being set to fixed to allow the model to spread itself out more)

		#particleDict[key].force[0] += physicsProperties.gravitational * particleDict[key].mass * down[0]
		#particleDict[key].force[1] += physicsProperties.gravitational * particleDict[key].mass * down[1]

		#viscous drag

		forceX -= physicsProperties.viscousdrag * particleDict[key].velocity[0]
		forceY -= physicsProperties.viscousdrag * particleDict[key].velocity[1]

		particleDict[key].force = (forceX, forceY)

	for spring in springList:

		particle1 = particleDict[spring.edgeA]
		particle2 = particleDict[spring.edgeB]

		dx = particle1.position[0] - particle2.position[0]
		dy = particle1.position[1] - particle2.position[1]

		len = math.sqrt((dx*dx) + (dy*dy))

		forceX = 0.0
		forceY = 0.0

		forceX = spring.springConstant * (len - spring.restLength)
		forceX += spring.dampingConstant * (particle1.velocity[0] - particle2.velocity[0]) * dx/len
		forceX *= -dx/len

		forceY = spring.springConstant * (len - spring.restLength)
		forceY += spring.dampingConstant * (particle1.velocity[1] - particle2.velocity[1]) * dy/len
		forceY *= -dy/len

		forceX1 = particle1.force[0] + forceX
		forceY1 = particle1.force[1] + forceY

		particleDict[spring.edgeA].force = (forceX1, forceY1)

		forceX2 = particle2.force[0] - forceX
		forceY2 = particle2.force[1] - forceY

		particleDict[spring.edgeB].force = (forceX2, forceY2)

	return particleDict

def updateParticles(particleDict, springList, physicsProperties, dt):

	particleDict = forceCalculations(particleDict, springList, physicsProperties)
	derivativeDict = createDerivatives(particleDict)

	for item in particleDict:

		positionX = particleDict[item].position[0]
		positionY = particleDict[item].position[1]

		positionX += derivativeDict[item].dpdt[0] * dt
		positionY += derivativeDict[item].dpdt[1] * dt

		particleDict[item].position = (positionX, positionY)

		velocityX = particleDict[item].velocity[0]
		velocityY = particleDict[item].velocity[1]

		velocityX += derivativeDict[item].dvdt[0] * dt
		velocityY += derivativeDict[item].dvdt[1] * dt

		particleDict[item].velocity = (velocityX, velocityY)

	return particleDict

def massSpringModel(keywordRelationships, window, width, height):

	dt = 0.1

	keywordRelationships = normaliseRelationships(keywordRelationships)

	particleDict = createParticles(keywordRelationships)
	springList = createSprings(keywordRelationships)
	physicsProperties = ParticlePhys(0, 0.1)

	for i in range(0, 1200):
		updateParticles(particleDict, springList, physicsProperties, dt)
		window.fill((0, 0, 0))

		for item in particleDict:
			pygame.draw.line(window, (255, 255, 255), particleDict[item].position, particleDict[item].position)

		for item in springList:
			pygame.draw.line(window, (255, 255, 255), particleDict[item.edgeA].position , particleDict[item.edgeB].position)

		pygame.display.flip()

	particleDict = normaliseFinalCoords(width, height, particleDict)
	window.fill((0, 0, 0))

	for item in particleDict:
		pygame.draw.line(window, (255, 255, 255), particleDict[item].position, particleDict[item].position)

	for item in springList:
		pygame.draw.line(window, (255, 255, 255), particleDict[item.edgeA].position , particleDict[item.edgeB].position)

	pygame.display.flip()
	return particleDict


#tupleList = [(1, 2, 350), (1, 4, 400), (1, 3, 670), (3, 4, 540), (6, 2, 350), (8, 4, 400), (4, 3, 670), (9, 8, 540), (6, 5, 350), (1, 8, 400), (7, 3, 670), (7, 9, 540)]
#used for testing

