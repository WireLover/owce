import tkinter as tk
from tkinter import ttk
import queue
from queue import Empty, Queue
import threading
from threading import Event, Thread
import time

import callbackData
import game
import text

class Window(tk.Tk):
      winWidth = 1000
      winHeight = 790
      viewFrameWidth = winWidth
      viewFrameHeight = 625
      canvasWidth = winWidth
      canvasHeight = 625

      def __init__(self):
            super().__init__()

            self.texts = text.getTexts("pl")
            
            self.title(self.texts["title"])
            self.geometry(str(Window.winWidth) + "x" + str(Window.winHeight))
            self.game = game.Game(self)
            self.log = []

            self.eventQueue = Queue()
            self.bind("<<guiUpdate>>", self.guiUpdateHandler)

            self.reversedSorting = False
            self.recentlySelectedSheep = None

            self.createView()
            self.createFooter()
            
      def guiUpdateCall(self, func, *args, **kwargs):
            # print("guiCall: " + str(args))
            # print("guiCall: " + str(kwargs))
            data = callbackData.event_callbackdata(func, args, kwargs)
            self.eventQueue.put(data)
            self.event_generate("<<guiUpdate>>")

            data.event.wait()

            return data.result

      def guiUpdateHandler(self, event):
            # data = self.eventQueue.get_nowait()
            # data.result = data.func(data.args, data.kwargs)
            
            # data.event.set()
            while not self.eventQueue.empty():
                  data = self.eventQueue.get_nowait()
                  data.result = data.func(data.args, data.kwargs)
                  data.event.set()

      def placeImage(self, args, kwargs):
            list = args[0]
                        
            # print("placeSheep: " + str(args))
            # print("placeSheep: " + str(kwargs))
            # print("placeSheep: " + str(sheep))
            for data in list:
                  scaledX = data[1] * Window.canvasWidth
                  scaledY = data[2] * Window.canvasHeight
                  self.canvas.coords(data[0], scaledX, scaledY)

      def createImage(self, args, kwargs):
            image = args[0]
            scaledX = args[1] * Window.canvasWidth
            scaledY = args[2] * Window.canvasHeight
            return self.canvas.create_image((scaledX, scaledY), image=image)

      def changeImage(self, args, kwargs):
            id = kwargs["imageId"]
            image = kwargs["image"]
            self.canvas.itemconfigure(id, image=image)

      def removeFromCanvas(self, args, kwargs):
            self.canvas.delete(args[0])

      def getActionText(self, action):
            if action == game.Creature.IDLE:
                  return self.texts["idleAction"]
            elif action == game.Creature.WANDERING:
                  return self.texts["wanderingAction"]
            elif action == game.Creature.GETTING_FOOD:
                  return self.texts["gettingFoodAction"]
            elif action == game.Creature.BEING_BRED or action == game.Creature.BREEDING:
                  return self.texts["breedingAction"]
            elif action == game.Creature.FIGHTING or action == game.Creature.IN_FIGHT:
                  return self.texts["fightingAction"]
            else:
                  return "bla"
            
      def getValueColor(self, value):
            color = "#"
            redValue = hex(int((2.0 - value * 2) * 0xff))
            if value <= 0.5:
                  redValue = hex(0xff)
                  
            greenValue = hex(0xff)
            if value <= 0.5:
                  greenValue = hex(int((value * 2) * 0xff))

            if len(redValue) <= 3:
                  color += "0"
            color += redValue[2:]

            if len(greenValue) <= 3:
                  color += "0"
            color += greenValue[2:]
            color += "00"
            # print(color)
            return color

      def selectSheep(self, sheep):
            self.recentlySelectedSheep = sheep

            self.sheepViewDeleteButton.config(
                  command=lambda: self.game.addCallback(self.game.markSheepDead, sheep)
            )

            # self.sheepViewNameVariable.set(self.texts["sheepNameLabel"] + str(sheep.name))
            self.sheepViewNameVariable.set(str(sheep.name))
            # self.sheepViewActionVariable.set(self.texts["sheepActionLabel"] + str(sheep.action))
            self.sheepViewActionVariable.set(self.getActionText(sheep.action))
            # self.sheepViewHealthVariable.set(self.texts["sheepHealthLabel"] + str(sheep.health))
            self.sheepViewHealthValue.config(background=self.getValueColor(sheep.health))
            # self.sheepViewHappinessVariable.set(self.texts["sheepHappinessLabel"] + str(sheep.happiness))
            self.sheepViewHappinessValue.config(background=self.getValueColor(sheep.happiness))
            # self.sheepViewHungerVariable.set(self.texts["sheepHungerLabel"] + str(sheep.hunger))
            self.sheepViewHungerValue.config(background=self.getValueColor(sheep.hunger))

            attitudesList = [str(k.name) + ": " + str(v) for k, v in sheep.attitudes.items()]
            attitudesList = sorted(
                  attitudesList, 
                  key=lambda s: float(s.split(": ")[1]),
                  reverse=self.reversedSorting
            )
            self.sheepViewAttitudesVariable.set(attitudesList)

            # print(sheep)
            # self.canvas.itemconfigure(sheep.imageId, image=tk.PhotoImage())

      def updateLog(self, args, kwargs):
            message = args[0]
            self.log.append(message)
            if len(self.log) > 100:
                  del self.log[0]

            self.logVariable.set(self.log)
            self.logList.yview_moveto(len(self.log) - 1)

      def setSortingOrder(self):
            self.reversedSorting = not self.reversedSorting
            self.selectSheep(self.recentlySelectedSheep)

      def newSheep(self, args, kwargs):
            sheep = game.Sheep()
            sheep.initGui(self)
            self.game.addCallback(self.game.addSheep, sheep)

      def addSheep(self, args, kwargs):
            sheep = args[0]
            sheep.initGui(self)
            self.game.addCallback(self.game.addSheep, sheep)

      def deleteSheep(self, imageId):
            self.sheepViewDeleteButton.config(
                  command=lambda: 1
            )
            self.game.addCallback(self.game.deleteSheep, imageId)

      def createView(self):
            self.viewFrame = ttk.Frame(self)
            self.viewFrame.config(width=Window.viewFrameWidth)
            self.viewFrame.config(height=Window.viewFrameHeight)
            self.viewFrame.config(borderwidth=0)
            
            self.canvas = tk.Canvas(self.viewFrame)
            self.canvas.config(width=Window.canvasWidth)
            self.canvas.config(height=Window.canvasHeight)
            self.canvas.config(background="green")
            self.canvas.config(borderwidth=0)
            self.canvas.config(highlightthickness=0)
            
            self.canvas.pack()
            
            game.Sheep.init()

            self.viewFrame.pack()
            self.game.start()


      def createFooter(self):
            self.footerFrame = ttk.Frame(self)
            self.footerFrame.columnconfigure(0, weight=3)
            self.footerFrame.columnconfigure(1, weight=5)
            self.footerFrame.columnconfigure(2, weight=5)
            
            self.createSheepView()
            self.createFooterMenu()
            self.createLog()

            self.sheepViewFrame.grid(column=0, row=0)
            self.footerMenuFrame.grid(column=1, row=0)
            self.logFrame.grid(column=2, row=0)

            self.footerFrame.pack()

      def createSheepView(self):
            self.sheepViewFrame = ttk.Frame(self.footerFrame)

            self.createDescriptionFrame()
            self.createAttitudesFrame()
            
            self.sheepViewDescriptionFrame.grid(column=0, row=0)
            self.sheepViewAttitudesFrame.grid(column=1, row=0)

      def createDescriptionFrame(self):
            self.sheepViewDescriptionFrame = ttk.Frame(self.sheepViewFrame)

            self.sheepViewNameVariable = tk.StringVar(self.sheepViewDescriptionFrame, value="")
            self.sheepViewNameLabel = ttk.Label(
                  self.sheepViewDescriptionFrame,
                  text=self.texts["sheepNameLabel"]
            )
            self.sheepViewNameLabel.grid(column=0, row=0, sticky=tk.W)
            # self.sheepViewNameLabel.pack()

            self.sheepViewNameValue = ttk.Label(
                  self.sheepViewDescriptionFrame,
                  width=20,
                  textvariable=self.sheepViewNameVariable
            )
            self.sheepViewNameValue.grid(column=1, row=0, sticky=tk.W)
            
            self.sheepViewActionVariable = tk.StringVar(self.sheepViewDescriptionFrame, value="")
            self.sheepViewActionLabel = ttk.Label(
                  self.sheepViewDescriptionFrame,
                  text=self.texts["sheepActionLabel"]
            )
            self.sheepViewActionLabel.grid(column=0, row=1, sticky=tk.W)
            # self.sheepViewActionLabel.pack()

            self.sheepViewActionValue = ttk.Label(
                  self.sheepViewDescriptionFrame,
                  width=20,
                  textvariable=self.sheepViewActionVariable
            )
            self.sheepViewActionValue.grid(column=1, row=1, sticky=tk.W)
            
            # self.sheepViewHealthVariable = tk.StringVar(self.sheepViewDescriptionFrame, value=self.texts["sheepHealthLabel"])
            self.sheepViewHealthLabel = ttk.Label(
                  self.sheepViewDescriptionFrame,
                  # textvariable=self.sheepViewHealthVariable
                  text=self.texts["sheepHealthLabel"]
            )
            # self.sheepViewHealthLabel.pack()
            self.sheepViewHealthLabel.grid(column=0, row=2, sticky=tk.W)

            self.sheepViewHealthValue = ttk.Label(
                  self.sheepViewDescriptionFrame,
                  width=2
            )
            self.sheepViewHealthValue.grid(column=1, row=2, padx=1, pady=1, sticky=tk.W)

            # self.sheepViewHappinessVariable = tk.StringVar(self.sheepViewDescriptionFrame, value=self.texts["sheepHappinessLabel"])
            self.sheepViewHappinessLabel = ttk.Label(
                  self.sheepViewDescriptionFrame,
                  # textvariable=self.sheepViewHappinessVariable
                  text=self.texts["sheepHappinessLabel"]
            )
            # self.sheepViewHappinessLabel.pack()
            self.sheepViewHappinessLabel.grid(column=0, row=3, sticky=tk.W)

            self.sheepViewHappinessValue = ttk.Label(
                  self.sheepViewDescriptionFrame,
                  width=2
            )
            self.sheepViewHappinessValue.grid(column=1, row=3, padx=1, pady=1, sticky=tk.W)

            # self.sheepViewHungerVariable = tk.StringVar(self.sheepViewDescriptionFrame, value=self.texts["sheepHungerLabel"])
            self.sheepViewHungerLabel = ttk.Label(
                  self.sheepViewDescriptionFrame,
                  # textvariable=self.sheepViewHungerVariable
                  text=self.texts["sheepHungerLabel"]
            )
            # self.sheepViewHungerLabel.pack()
            self.sheepViewHungerLabel.grid(column=0, row=4, sticky=tk.W)

            self.sheepViewHungerValue = ttk.Label(
                  self.sheepViewDescriptionFrame,
                  width=2
            )
            self.sheepViewHungerValue.grid(column=1, row=4, padx=1, pady=1, sticky=tk.W)

            self.sheepViewDeleteButton = ttk.Button(
                  self.sheepViewDescriptionFrame,
                  text=self.texts["deleteButton"]
            )
            # self.sheepViewDeleteButton.pack()
            self.sheepViewDeleteButton.grid(column=0, row=5, sticky=tk.W)

      def createAttitudesFrame(self):
            self.sheepViewAttitudesFrame = ttk.Frame(self.sheepViewFrame)

            self.sheepViewAttitudesLabel = ttk.Label(
                  self.sheepViewAttitudesFrame,
                  text=self.texts["attitudesLabel"],
            )
            self.sheepViewAttitudesLabel.pack()

            self.sheepViewAttitudesVariable = tk.StringVar(self.sheepViewAttitudesFrame)
            self.sheepViewAttitudesList = tk.Listbox(
                  self.sheepViewAttitudesFrame,
                  listvariable=self.sheepViewAttitudesVariable,
                  height = 6
            )
            self.sheepViewAttitudesList.pack()
            
            self.sheepViewReversedSortingButton = ttk.Button(
                  self.sheepViewAttitudesFrame,
                  text=self.texts["reversedSortingButton"],
                  command=self.setSortingOrder
            )
            self.sheepViewReversedSortingButton.pack()

      def createFooterMenu(self):
            self.footerMenuFrame = ttk.Frame(self.footerFrame)

            self.footerMenulabel = ttk.Label(
                  self.footerMenuFrame, 
                  text=self.texts["footerLabel"],
                  width=20,
                  anchor="center"
            )
            self.footerMenulabel.pack()

            self.footerMenuAddSheepButton = ttk.Button(
                  self.footerMenuFrame, 
                  text=self.texts["addButton"], 
                  command=lambda: self.newSheep((), {})
            )
            self.footerMenuAddSheepButton.pack()

      def createLog(self):
            self.logFrame = ttk.Frame(self.footerFrame)

            self.logLabel = ttk.Label(
                  self.logFrame,
                  text=self.texts["logLabel"],
            )
            self.logLabel.pack(side=tk.TOP, fill=tk.NONE, expand=False)

            self.logVariable = tk.StringVar(self.logFrame)
            self.logList = tk.Listbox(
                  self.logFrame,
                  listvariable=self.logVariable,
                  width=50,
                  height=6,
            )
            self.logList.pack(side=tk.TOP, fill=tk.NONE, expand=False)

if __name__ == "__main__":
      window = Window()
      window.mainloop()
