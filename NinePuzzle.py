# Nine-Puzzle
import random
import tkinter as tk
from tkinter import font as tkFont
from winsound import *
from time import sleep


class Square():
    def __init__(self, text, colour, xpos, ypos):
        self.text = text
        self.colour = colour
        self.xpos = xpos
        self.ypos = ypos

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.titlefont = tkFont.Font(family="Arial", size=20, slant="italic")
        self.buttonFont = tkFont.Font(family="Arial", size=28)
        self.label = tk.Label(self, text="NinePuzzle", font=self.titlefont)
        self.label.grid(row=0, column=0, sticky="W")
        self.board = tk.Canvas(self, width=600,height = 600, bg="grey")
        self.board.grid(row = 1, column = 0, columnspan=3 )
        self.boardState = completedArrangement.copy()
        self.shufflebutton = tk.Button(self, text="Shuffle", font = self.titlefont, command = self.shuffle)
        self.shufflebutton.grid(row=0, column=1, sticky="E")
        self.solve = tk.Button(self, text="Solve it!", font=self.titlefont, command=self.autorun)
        self.solve.grid(row=0, column=2, sticky="EW")
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2, minsize = 180)
        self.moving = False
        self.gameActive = False
        self.makeBoard()
        self.mainloop()

    def shuffle(self):
        self.boardState = shuffle(self.boardState)
        self.makeBoard()

    def autorun(self):
        stateList = {}
        startArrangement = self.boardState
        start = gameState(startArrangement, completedArrangement)
        stateList["".join(start.state)] = start
        start.shortestEstimatedDistance = start.heuristic
        solution = solve(start, completedArrangement, stateList, self)
        # now do the animation
        self.animateSolution(solution, 0)

    def animateSolution(self, solution, nodeNumber):
        node = solution[nodeNumber]
        if node.previousDirection == 0:
            #up
            self.moveSquare(self.squares[node.previousTile], 0, 10, 20)
        elif node.previousDirection == 2:
            #down
            self.moveSquare(self.squares[node.previousTile], 0, -10, 20)
        elif node.previousDirection == 1:
            #right
            self.moveSquare(self.squares[node.previousTile], -10, 0, 20)
        elif node.previousDirection == 3:
            # left
            self.moveSquare(self.squares[node.previousTile], 10, 0, 20)
        self.boardState = node.state
        if nodeNumber < len(solution)-1:
            self.after(300, lambda n = nodeNumber+1: self.animateSolution(solution, n))

    def makeBoard(self):
        self.board.delete("all")
        self.squares = {}
        self.IDs = {}
        val = 0
        colours = [None,"red", "green","blue", "orange","purple","teal","yellow","white"]
        for row in range(3):
            for column in range(3):
                if self.boardState[val] != "0":
                    self.squares[self.boardState[val]] = Square(self.boardState[val], colours[int(self.boardState[val])], column*200, row*200 )
                val += 1
        size = 200
        for square in self.squares.values():
                square.id = self.board.create_rectangle(square.xpos,square.ypos,square.xpos+size, square.ypos+size,fill=square.colour)
                self.IDs[square.id] = square
                self.board.tag_bind(square.id,"<Button-1>", self.clicked)
                square.textID = self.board.create_text(square.xpos+size/2, square.ypos+size/2, text=square.text, font=self.buttonFont, fill="black")
                self.IDs[square.textID] = square
                self.board.tag_bind(square.textID, "<Button-1>", self.clicked)

    def clicked(self,e):
        if self.moving:
            return
        squareclicked = self.IDs[self.board.find_closest(e.x, e.y)[0]]
        #find appropriate movement
        pos = self.boardState.index(squareclicked.text)
        zero = self.boardState.index("0")
        valid = False
        if zero == pos-3:
                # up
                self.moving = True
                self.moveSquare(squareclicked, 0, -10, 20)
                valid = True
        if zero == pos+3:
                # down
                self.moving = True
                self.moveSquare(squareclicked, 0, 10, 20)
                valid = True
        if pos%3>0 and zero == pos-1:
                # left
                self.moving = True
                self.moveSquare(squareclicked, -10, 0, 20)
                valid = True
        if pos%3<2 and zero==pos+1 :
                # right
                self.moving = True
                self.moveSquare(squareclicked, 10, 0, 20)
                valid = True
        if valid:
            self.boardState[zero] = squareclicked.text
            self.boardState[pos] = "0"
        self.gameActive=True
        self.board.after(300, self.checkWin)

    def checkWin(self):
        if self.moving:
            self.board.after(20, self.checkWin)
        if self.gameActive:
            if self.boardState == completedArrangement:
                PlaySound("fanfare2.wav", SND_FILENAME)

    def moveSquare(self, square, xdiff, ydiff, loops):
        square.xpos += xdiff
        square.ypos += ydiff
        self.board.move(square.id, xdiff, ydiff)
        self.board.move(square.textID, xdiff, ydiff)
        loops -= 1
        self.board.update_idletasks()
        if loops > 0:
            self.board.after(5, lambda l = loops: self.moveSquare(square,xdiff,ydiff,l))
        else:
            self.moving = False


class gameState():
    def __init__(self, state, target):
        self.state = state
        self.links = [(None,None),(None,None),(None,None),(None,None)]
        self.shortestEstimatedDistance = None
        self.distanceFromStart = 0
        self.previousState = None
        self.previousDirection = None
        self.previousTile = None
        self.target = target
        self.visited = False
        self.getAlternativeHeuristic()

        
    def printme(self):
        print()
        for y in range(3):
            for x in range(3):
                if self.state[y*3+x] != "0":
                    print(self.state[y*3+x], end=" ")
                else:
                    print(" ", end=" ")
            print()
            
    def explore(self, stateList):
        if self.state.index("0")%3 <2:
            newstate, tileMoved = self.move("r")
            if "".join(newstate) not in stateList.keys():
                newstateobject = gameState(newstate, self.target)
                stateList["".join(newstate)] = newstateobject
            self.links[1] = stateList["".join(newstate)], tileMoved
        if self.state.index("0")%3 >0:
            newstate, tileMoved = self.move("l")
            if "".join(newstate) not in stateList.keys():
                newstateobject = gameState(newstate, self.target)
                stateList["".join(newstate)] = newstateobject
            self.links[3] = stateList["".join(newstate)], tileMoved
        if self.state.index("0") >2 :
            newstate, tileMoved = self.move("u")
            if "".join(newstate) not in stateList.keys():
                newstateobject = gameState(newstate, self.target)
                stateList["".join(newstate)] = newstateobject
            self.links[0] = stateList["".join(newstate)], tileMoved
        if self.state.index("0") <6 :
            newstate, tileMoved = self.move("d")
            if "".join(newstate) not in stateList.keys():
                newstateobject = gameState(newstate, self.target)
                stateList["".join(newstate)] = newstateobject
            self.links[2] = stateList["".join(newstate)], tileMoved
        

    def move(self, move):
        newstate = self.state[:]
        space = self.state.index("0")
        if move == "d":
            movetile = space+3
        if move == "u":
            movetile = space-3
        if move == "l":
            movetile = space-1
        if move == "r":
            movetile = space+1
        newstate[space] = self.state[movetile]
        newstate[movetile] = "0"
        return newstate, newstate[space] # send the new board position, and remember which tile was moved
                                         # (this is just for the benefit of the animation)
        
    def getHeuristic(self):
        # we will count how many tiles are out of place
        count = 0
        for x in range(9):
            if self.state[x] != self.target[x]:
                count +=1
        self.heuristic = count


    def getAlternativeHeuristic(self):
        total = 0
        for x in range(9):
            total += abs(self.state.index(str(x))%3 - self.target.index(str(x))%3)
            total += abs(self.state.index(str(x))//3 - self.target.index(str(x))//3)
        self.heuristic = total


def solve(startBoard, target, stateList, app):
    currentNode = startBoard
    moves = 0
    print("Start position:")
    currentNode.printme()
    print("Thinking...")
    if currentNode.state == target:
        print("Already solved")
        return
    running = True
    while running:
        moves +=1
        if moves%100 == 0:
            dots = int(moves / 100) % 3
            app.solve.config(text="Thinking " + dots*"." + (3-dots)*" ")
            app.update()
        currentNode.visited = True
        currentNode.explore(stateList)
        for direction in range(0,4):
            node, tileMoved = currentNode.links[direction]   # now check all the linked nodes to update distances
            if node and not node.visited:
                if node.shortestEstimatedDistance is None or (currentNode.distanceFromStart + 1 + node.heuristic) < node.shortestEstimatedDistance:
                    # this path to this node is better than the previous one, if any
                    node.distanceFromStart = currentNode.distanceFromStart + 1
                    node.shortestEstimatedDistance = node.distanceFromStart + node.heuristic
                    node.previousState = currentNode
                    node.previousDirection = direction
                    node.previousTile = tileMoved
        # now find the unvisited node with the closest estimated distance
        shortestDistance = None
        nextNode  = None
        for state in stateList.values():
            if not state.visited and (shortestDistance == None or state.shortestEstimatedDistance <  shortestDistance):
                shortestDistance = state.shortestEstimatedDistance
                nextNode = state # this is the node with the shortest estimated distance
        currentNode = nextNode
        if currentNode.state == target: # The current node is the solution
            running = False
    solution = []
    while True:  # we have found the solution, so backtrack from the end node to find the full path
        solution.insert(0, currentNode)
        if currentNode.previousState == None:
            break
        currentNode = currentNode.previousState
    print("Found solution:")
    for node in solution:
        node.printme()
    app.solve.config(text="Got it!")
    app.update()
    return solution



def shuffle(state):
    for x in range(5000):  # perform 5000 random moves to shuffle the board
        move = random.randint(0,3)
        zero = state.index("0")
        if move == 0 and zero>2:
            state[zero] = state[zero-3]
            state[zero-3] = "0"
        if move == 1 and zero%3<2:
            state[zero] = state[zero+1]
            state[zero+1] = "0"
        if move == 2 and zero<6:
            state[zero] = state[zero+3]
            state[zero+3] = "0"
        if move == 3 and zero%3>0:
            state[zero] = state[zero-1]
            state[zero-1] = "0"
    return state




completedArrangement = ["1","2","3","4","5","6","7","8","0"]
window = App()


