import threading
from threading import Thread
import queue
from queue import Empty, Queue
import time
import tkinter as tk
from tkinter import ttk
import random
import math

import callbackData
import names

class Game(Thread):
      FPS = 60

      isRunning = True
      startSheepNum = 10

      sheepList = []
      sheepPath = {}

      foodStashX = 1.0
      foodStashY = 0.0
      foodStashRadius = 0.1

      def __init__(self, gui):
            super().__init__(daemon=True)

            self.gui = gui
            self.texts = gui.texts
            self.tick = 0
            self.eventQueue = Queue()

            heartImageList = [
                  "img\\serce_0.png",
                  "img\\serce_1.png",
                  "img\\serce_2.png",
                  "img\\serce_3.png"
            ]
            self.heartImage = Image(self.gui, heartImageList)

      def addSheep(self, args, kwargs):
            sheep = args[0]
            sheep.setGame(self)

            self.newAttitudes(sheep)           
            self.sheepList.append(sheep)

      def newSheep(self, sheep):
            self.gui.guiUpdateCall(self.gui.addSheep, sheep)

      def newAttitudes(self, newSheep):
            if len(self.sheepList) == 0:
                  return
            
            for sheep in self.sheepList:
                  sheep.newAttitude(newSheep)
                  newSheep.newAttitude(sheep)


      def deleteSheep(self, args, kwargs):
            imageId = args[0]
            toRemove = None

            for sheep in self.sheepList:
                  if sheep.imageId == imageId:
                        toRemove = sheep

            self.sheepList.remove(toRemove)
            print(imageId)

      def deleteSheep(self, delSheep):
            toRemove = None

            for sheep in self.sheepList:
                  if sheep == delSheep:
                        toRemove = sheep

            self.sheepList.remove(toRemove)

      def updateLog(self, message):
            self.gui.guiUpdateCall(self.gui.updateLog, message)
      
      def addCallback(self, func, *args, **kwargs):
            data = callbackData.event_callbackdata(func, args, kwargs)
            self.eventQueue.put(data)
      
      def handleEventQueue(self):
            result = []
            while not self.eventQueue.empty():
                  data = self.eventQueue.get_nowait()
                  result.append(data.func(data.args, data.kwargs))

            return result

      def run(self):
            for i in range(0, self.startSheepNum):
                  self.newSheep(Sheep())

            while self.isRunning:
                  points = []

                  self.handleEventQueue()

                  for sheep in self.sheepList:
                        sheep.handleCreature()

                        points.append((sheep.imageId, sheep.x, sheep.y))

                  self.gui.guiUpdateCall(self.gui.placeImage, points)

                  self.tick = (self.tick + 1) % 500
                  time.sleep(1 / Game.FPS)

      def distance(x0, y0, x1, y1):
            return math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)


class Creature:
      moveSpeed = 0.005
      maxPathDistance = 0.4
      minPathDistance = 0.1
      lastNameIndex = 0
      chanceToWander = 0.004

      maxPoint = 0.85
      minPoint = 0.15
      scaleFactor = maxPoint - minPoint

      IDLE = 1
      WANDERING = 2
      WALKING = 3
      GETTING_FOOD = 4
      FIGHTING = 5
      IN_FIGHT = 6
      BREEDING = 7
      BEING_BRED = 8

      ALIVE = 1
      DEAD = 2
      
      def __init__(self):
            self.x = 0.5
            self.y = 0.5
            self.width = 100
            self.height = 100

            self.pathingPoint = [0, 0]
            self.pathingPointDist = [0, 0]
            self.oldDistance = 0
            self.timeSpentStanding = 0
            self.firstMoveIteration = True

            self.status = Creature.ALIVE
            self.action = Creature.IDLE
            
      def doAction(self):
            if self.action == Creature.WANDERING:
                  self.doWanderingAction()

      def handleCreature(self):
            self.doAction()
                  
      def move(self, x, y):
            self.x = x
            self.y = y

      def getCoords(self):
            scaledX = self.x * Creature.scaleFactor + Creature.minPoint
            scaledY = self.y * Creature.scaleFactor + Creature.minPoint
            return (x, y)

      def getX(self):
            return self.x * Creature.scaleFactor + Creature.minPoint

      def getY(self):
            return self.y * Creature.scaleFactor + Creature.minPoint

      def moveTowardsPathingPoint(self):
            # distX = math.fabs(self.x - self.pathingPoint[0]) 
            # distY = math.fabs(self.y - self.pathingPoint[1]) 
            travelDistX = self.pathingPointDist[0]
            travelDistY = self.pathingPointDist[1]
            distX = self.pathingPoint[0] - self.x
            distY = self.pathingPoint[1] - self.y

            newDistance = math.sqrt(distX ** 2 + distY ** 2)

            if self.firstMoveIteration or self.oldDistance > newDistance: # 0.5 0.4    0.0 0.1
                  self.firstMoveIteration = False

                  self.oldDistance = newDistance
                  deltaX = travelDistX * Sheep.moveSpeed
                  deltaY = travelDistY * Sheep.moveSpeed

                  self.move(self.x - deltaX, self.y - deltaY)
                  return False
            else:
                  return True

      def newPathingPoint(self, x, y):
            self.firstMoveIteration = True

            self.pathingPoint[0] = x
            self.pathingPoint[1] = y
            self.pathingPointDist[0] = self.x - x
            self.pathingPointDist[1] = self.y - y

      def newRandomPathingPoint(self):
            self.firstMoveIteration = True

            distance = random.random() * (Sheep.maxPathDistance - Sheep.minPathDistance) + Sheep.minPathDistance
            direction = random.random() * (2 * math.pi)

            x = self.x + math.cos(direction) * distance
            y = self.y + math.sin(direction) * distance
            if x > 1.0 or x < 0:
                  x -= 2 * math.cos(direction) * distance
            if y > 1.0 or y < 0:
                  y -= 2 * math.sin(direction) * distance

            self.pathingPoint[0] = x
            self.pathingPoint[1] = y
            self.pathingPointDist[0] = self.x - x
            self.pathingPointDist[1] = self.y - y

            return self.pathingPoint

      def setGame(self, game):
            self.game = game
            
      def __str__(self):
            return str(self.x) + " " + str(self.y) + " " + str(self.pathingPoint) + " " + str(self.pathingPointDist) + " " + str(self.action) + "\n" + str(self.nearbySheep)

class Sheep(Creature):
      timeToSpendEating = 120
      timeToSpendFighting = 360
      timeToSpendDying = 1200
      timeToSpendBreeding = 360
      nearbyDistance = 0.25
      fightingRadius = 0.05
      BreedingRadius = 0.05
      chanceToFight = 0.00003
      chanceToBreed = 0.00003
      # chanceToBreed = 0.01
      fightCooldown = 2400
      breedingCooldown = 2400
      # chanceToFight = 0.0003

      minAfterFightHealth = 0.5
      maxAfterFightHealth = 1.5

      namesNum = len(names.names)
      availableNames = [i for i in range(0, namesNum)]
      
      def __init__(self):
            super().__init__()

            self.name = Sheep.newName()
            self.happiness = 0.5
            self.health = 1.0
            self.metabolism = Sheep.newRandomMetabolism()
            self.hunger = 0.4
            self.animationFrame = 0
            self.timeSpentNotFighting = 0
            self.timeSpentNotBreeding = 0
            self.timeSpentDead = 0
            self.readyToFight = True
            self.readyToBreed = True

            self.attitudes = {}
            self.nearbySheep = []

            # super().__init__(master=gui.canvas, width=self.width, height=self.height)
            # self.create_image((50, 50), image=Sheep.image)
            # super().__init__(master=gui.viewFrame, image=Sheep.image, fg_color="transparent")
            # self.config(command=self.deleteSheep)
            # self.imageId = gui.canvas.create_image((50, 50), image=Sheep.image)
            # gui.canvas.tag_bind(self.imageId, "<Button-1>", func=lambda e: gui.selectSheep(self))
            self.startWandering()

      # propably should be called on tkinter thread
      def initGui(self, gui):
            """Function initializing sheep on tkinter's canvas
            This function is meant to be run on tkinter's thread

            Args:
                  gui (main.Window): Window object storing the canvas
            """
            self.gui = gui
            self.imageId = gui.canvas.create_image((50, 50), image=Sheep.image)
            gui.canvas.tag_bind(self.imageId, "<Button-1>", func=lambda e: gui.selectSheep(self))

      def init():
            Sheep.image = tk.PhotoImage(file="img\\owca2.png")
            Sheep.image_fight0 = tk.PhotoImage(file="img\\fight_0.png")
            Sheep.image_fight1 = tk.PhotoImage(file="img\\fight_1.png")
            Sheep.image_dead = tk.PhotoImage(file="img\\zdechla2.png")
            Sheep.image_blank = tk.PhotoImage()
            # image = Image.open("img\\owca2.png")
            Sheep.image = Sheep.image.zoom(2, 2)
            Sheep.image_fight0 = Sheep.image_fight0.zoom(2, 2)
            Sheep.image_fight1 = Sheep.image_fight1.zoom(2, 2)
            Sheep.image_dead = Sheep.image_dead.zoom(2, 2)
            # print(dir(tk.Canvas))

      # override
      def doAction(self):
            sheepToFight = self.wantsToFight()
            sheepToBreed = self.wantsToBreed()

            if self.action == Creature.IN_FIGHT:
                  self.doInFightAction()
            elif self.action == Creature.FIGHTING:
                  self.doFightingAction()
            elif self.action == Creature.GETTING_FOOD:
                  self.doGettingFoodAction()
            elif self.action == Creature.BEING_BRED:
                  self.doBeingBredAction()
            elif self.action == Creature.BREEDING:
                  self.doBreedingAction()
            elif self.hunger < 0.3:
                  self.startGettingFood()
            elif sheepToFight != None:
                  # print(self.name + " wants to fight: " + sheepToFight.name)
                  self.game.updateLog(self.name + self.game.texts["fightingMessage"] + sheepToFight.name)
                  self.startFighting(sheepToFight)
                  sheepToFight.joinFight(self)
            elif sheepToBreed != None:
                  # print(self.name + " wants to breed with: " + sheepToBreed.name)
                  self.game.updateLog(self.name + self.game.texts["breedingMessage"] + sheepToBreed.name)
                  self.startBreeding(sheepToBreed)
            elif self.action == Creature.WANDERING:
                  self.doWanderingAction()
            elif self.action == Creature.IDLE:
                  self.doIdlingAction()
                  

      # override
      def handleCreature(self):
            if self.status == Creature.ALIVE:
                  self.lowerHunger()
                  self.checkCooldowns()
                  self.checkNearbySheep()
                  self.doAction()
            elif self.status == Creature.DEAD:
                  self.doDeathAction()

      def checkNearbySheep(self):
            newList = []
            for sheep in self.game.sheepList:
                  if sheep.status == Creature.ALIVE:
                        distance = Game.distance(self.x, self.y, sheep.x, sheep.y)
                  
                        if distance < Sheep.nearbyDistance:
                              newList.append(sheep)

            self.nearbySheep = newList
      
      def checkCooldowns(self):
            if not self.readyToFight:
                  self.timeSpentNotFighting += 1
                  if self.timeSpentNotFighting >= Sheep.fightCooldown:
                        self.readyToFight = True
                        self.timeSpentNotFighting = 0

            if not self.readyToBreed:
                  self.timeSpentNotBreeding += 1
                  if self.timeSpentNotBreeding >= Sheep.breedingCooldown:
                        self.readyToBreed = True
                        self.timeSpentNotBreeding = 0


      def wantsToFight(self):
            if not self.readyToFight:
                  return None

            sheepToFight = None
            i = 0

            while i < len(self.nearbySheep) and sheepToFight == None:
                  sheep = self.nearbySheep[i]
                  if sheep != self:
                        attitude = self.attitudes[sheep]

                        if attitude < 0.3:
                              rand = random.random()

                              if rand < Sheep.chanceToFight * (2 - attitude):
                                    sheepToFight = sheep
                        
                  i += 1
                              
            return sheepToFight    
             
      def wantsToBreed(self):
            if not self.readyToBreed:
                  return None

            sheepToBreed = None
            i = 0

            while i < len(self.nearbySheep) and sheepToBreed == None:
                  sheep = self.nearbySheep[i]
                  if sheep != self:
                        if sheep.action != Creature.BREEDING:
                              attitude = self.attitudes[sheep]

                              if attitude > 0.7:
                                    rand = random.random()

                                    if rand < Sheep.chanceToBreed * (1 + attitude):
                                          sheepToBreed = sheep
                        
                  i += 1
                              
            return sheepToBreed

      def changeImage(self, image):
            self.gui.guiUpdateCall(self.gui.changeImage, imageId=self.imageId, image=image)
            
      def startIdling(self):
            self.action = Creature.IDLE

      def doIdlingAction(self):
            rand = random.random()
            if rand < Creature.chanceToWander:
                  self.startWandering()

      def startWandering(self):
            if self.action == Creature.IDLE:
                  self.action = Creature.WANDERING
                  self.newRandomPathingPoint()

      def doWanderingAction(self):
            destinationReached = self.moveTowardsPathingPoint()

            if destinationReached:
                  self.startIdling()

      def startFighting(self, sheep):
            self.timeSpentStanding = 0
            self.animationFrame = 0

            self.attackedSheep = sheep
            self.readyToFight = False
            self.action = Creature.FIGHTING
            self.newPathingPoint(sheep.x, sheep.y)

      def doFightingAction(self):
            distance = Game.distance(self.x, self.y, self.pathingPoint[0], self.pathingPoint[1])
            
            if distance > Sheep.fightingRadius:
                  self.moveTowardsPathingPoint()
            elif self.timeSpentStanding < Sheep.timeToSpendFighting:
                  if self.timeSpentStanding == 0:
                        self.attackedSheep.startJoinedFight()
                        
                  if self.timeSpentStanding % 30 == 0:
                        if self.animationFrame == 0:
                              self.changeImage(Sheep.image_fight0)
                        else:
                              self.changeImage(Sheep.image_fight1) 
                        self.animationFrame = (self.animationFrame + 1) % 2
                  self.timeSpentStanding += 1
            else:
                  self.startIdling()
                  self.changeImage(Sheep.image)
                  self.lowerHealthAfterFight()

      def startJoinedFight(self):
            self.isJoinedFightStarted = True

      def joinFight(self, sheep):
            self.timeSpentStanding = 0

            self.isJoinedFightStarted = False
            self.readyToFight = False
            self.action = Creature.IN_FIGHT
            self.newPathingPoint(sheep.x, sheep.y)

      def doInFightAction(self):
            if self.isJoinedFightStarted and self.timeSpentStanding < Sheep.timeToSpendFighting:
                  if self.timeSpentStanding == 0:
                        self.changeImage(Sheep.image_blank)
                  self.timeSpentStanding += 1

            if self.timeSpentStanding == Sheep.timeToSpendFighting:
                  self.startIdling()
                  self.changeImage(Sheep.image)
                  self.lowerHealthAfterFight()

      def lowerHealthAfterFight(self):
            amount = Sheep.minAfterFightHealth + random.random() * (Sheep.maxAfterFightHealth - Sheep.minAfterFightHealth)
            self.setHealth(self.health - amount)

      def setHealth(self, amount):
            self.health = amount
            if self.health <= 0.0:
                  self.markDead()
      
      def markDead(self):
            self.changeImage(Sheep.image_dead)
            self.status = Creature.DEAD
            # print(self.name + " has died")
            self.game.updateLog(self.game.texts["sheep"] + ": " + self.name + self.game.texts["deathMessage"])


      def doDeathAction(self):
            if self.timeSpentDead >= Sheep.timeToSpendDying:
                  self.deleteSheep()

            self.timeSpentDead += 1

      def startBreeding(self, sheep):
            self.timeSpentStanding = 0
            self.animationFrame = 0

            self.action = Creature.BREEDING
            self.readyToBreed = False
            self.newPathingPoint(sheep.x, sheep.y)
            self.sheepBeingBred = sheep
            sheep.joinBredding()

      def joinBredding(self):
            self.timeSpentStanding = 0
            self.action = Creature.BEING_BRED
            self.isBeingBredStarted = False
            self.readyToBreed = False
      
      def startBeingBred(self):
            self.isBeingBredStarted = True

      def doBreedingAction(self):
            distance = Game.distance(self.x, self.y, self.pathingPoint[0], self.pathingPoint[1])
            
            if distance > Sheep.BreedingRadius:
                  self.moveTowardsPathingPoint()
            elif self.timeSpentStanding < Sheep.timeToSpendBreeding:
                  if self.timeSpentStanding == 0:
                        self.sheepBeingBred.startBeingBred()
                        self.heartImageId = self.game.heartImage.paint(0, self.x, self.y)

                  if self.timeSpentStanding % 10 == 0:
                        if self.animationFrame <= 3:
                              self.game.heartImage.change(self.heartImageId, self.animationFrame)
                        else:
                              self.game.heartImage.change(self.heartImageId, 7 - self.animationFrame)

                        self.animationFrame = (self.animationFrame + 1) % 8

                  self.timeSpentStanding += 1
            else:
                  self.game.heartImage.remove(self.heartImageId)
                  newSheep = Sheep()
                  newSheep.x = self.x
                  newSheep.y = self.y
                  newSheep.readyToBreed = False
                  newSheep.readyToFight = False

                  self.game.updateLog(self.game.texts["sheep"] + ": " + newSheep.name + self.game.texts["birthMessage"])
                  self.game.newSheep(newSheep)
                  self.startIdling()

      def doBeingBredAction(self):
            if self.isBeingBredStarted and self.timeSpentStanding < Sheep.timeToSpendFighting:
                  self.timeSpentStanding += 1

            if self.timeSpentStanding == Sheep.timeToSpendFighting:
                  self.startIdling()

      def startGettingFood(self):   
            self.timeSpentStanding = 0
            self.action = Creature.GETTING_FOOD
            self.newPathingPoint(self.game.foodStashX, self.game.foodStashY)

      def doGettingFoodAction(self):
            deltaX = self.x - self.game.foodStashX
            deltaY = self.y - self.game.foodStashY
            distance = math.sqrt(deltaX ** 2 + deltaY ** 2)

            if distance > self.game.foodStashRadius:
                  self.moveTowardsPathingPoint()
            elif self.timeSpentStanding < Sheep.timeToSpendEating:
                  self.timeSpentStanding += 1
            else:
                  self.hunger = 1.0
                  self.startIdling()
      
      def newRandomMetabolism():
            return random.random() / 10000
            
      def lowerHunger(self):
            self.hunger -= self.metabolism
      
      def newName():
            if len(Sheep.availableNames) == 0:
                  Sheep.availableNames = [i for i in range(0, Sheep.namesNum)]

            index = int(time.time()) % len(Sheep.availableNames)
            name = names.names[Sheep.availableNames[index]]
            del Sheep.availableNames[index]

            return name

      def newAttitude(self, sheep):
            number = hash(self.name) + hash(sheep.name)
            attitude = (number % 1001) / 1000
            # attitude = 0.8
            self.attitudes[sheep] = attitude

            return attitude

      def deleteSheep(self):
            self.gui.guiUpdateCall(self.gui.removeFromCanvas, self.imageId)
            self.game.deleteSheep(self)
            for sheep in self.game.sheepList:
                  del sheep.attitudes[self]
            
      def print(self):
            print(self)

class Image:
      def __init__(self, gui, images):
            self.gui = gui
            self.imageIds = []

            self.images = []

            for img in images:
                  newImage = tk.PhotoImage(file=img)
                  newImage = newImage.zoom(2, 2)
                  self.images.append(newImage)

            self.image = images[0]
      
      def paint(self, index, x, y):
            imageId = self.gui.guiUpdateCall(self.gui.createImage, self.images[index], x, y)
            self.imageIds.append(imageId)
            return imageId
      
      def change(self, id, index):
            self.gui.guiUpdateCall(self.gui.changeImage, imageId=id, image=self.images[index])

      def remove(self, id):
            self.gui.guiUpdateCall(self.gui.removeFromCanvas, id)


