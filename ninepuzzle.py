# Nine-Puzzle
import random
import math


stateList = {}

class gameState():
    def __init__(self, state):
        self.state = state
        self.links = [None,None,None,None]
        self.shortestEstimatedDistance = None
        self.distanceFromStart = 0
        self.previousState = None
        self.getHeuristic()
        
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
            newstate = self.move("r")
            if "".join(newstate) not in stateList.keys():
                newstateobject = gameState(newstate)
                stateList["".join(newstate)] = newstateobject
            self.links[1] = stateList["".join(newstate)]
        if self.state.index("0")%3 >0:
            newstate = self.move("l")
            if "".join(newstate) not in stateList.keys():
                newstateobject = gameState(newstate)
                stateList["".join(newstate)] = newstateobject
            self.links[3] = stateList["".join(newstate)]
        if self.state.index("0") >2 :
            newstate = self.move("u")
            if "".join(newstate) not in stateList.keys():
                newstateobject = gameState(newstate)
                stateList["".join(newstate)] = newstateobject
            self.links[0] = stateList["".join(newstate)]
        if self.state.index("0") <6 :
            newstate = self.move("d")
            if "".join(newstate) not in stateList.keys():
                newstateobject = gameState(newstate)
                stateList["".join(newstate)] = newstateobject
            self.links[2] = stateList["".join(newstate)]      
        

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
        return newstate
        
    def getHeuristic(self):
        # we will count how many tiles are out of place
        goal = "876543210"
        count = 0
        for x in range(9):
            if self.state[x] != goal[x]:
                count +=1
        self.heuristic = count


    def getAlternativeHeuristic(self):
        total = 0
        goal = "876543210"
        for x in range(9):
            total += abs(self.state.index(str(x))%3 - goal.index(str(x))%3)
            total += abs(self.state.index(str(x))//3 - goal.index(str(x))//3)
        self.heuristic = total

def solve(startBoard, target, stateList):
    currentNode = startBoard
    print("Start position:")
    currentNode.printme()
    print("Thinking...")
    if "".join(currentNode.state) == target:
        print("Already solved")
        return
    visited = []
    running = True
    while running:
        visited.append(currentNode)

        currentNode.explore(stateList)
        for node in currentNode.links: # now check all the linked nodes to update distances
            if node  and node not in visited:
                if node.shortestEstimatedDistance is None or (currentNode.distanceFromStart + 1 + node.heuristic) < node.shortestEstimatedDistance:
                    # this path to this node is better than the previous one, if any
                    node.distanceFromStart = currentNode.distanceFromStart + 1
                    node.shortestEstimatedDistance = node.distanceFromStart + node.heuristic
                    node.previousState = currentNode
        # now find the unvisited node with the closest estimated distance
        shortestDistance = None
        nextNode  = None
        for state in stateList.values():
            if state not in visited and (shortestDistance == None or state.shortestEstimatedDistance <  shortestDistance):
                shortestDistance = state.shortestEstimatedDistance
                nextNode = state # this is the node with the shortest estimated distance
        currentNode = nextNode
        if "".join(currentNode.state) == target: # The current node is the solution
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
        if move == 2 and zero<2:
            state[zero] = state[zero+3]
            state[zero+3] = "0"
        if move == 3 and zero%3>0:
            state[zero] = state[zero-1]
            state[zero-1] = "0"            
    return state
            

completedArrangement = ["8","7","6","5","4","3","2","1","0"]
startArrangement = shuffle(completedArrangement)
start = gameState(startArrangement)

stateList["".join(start.state)] = start
start.shortestEstimatedDistance = start.heuristic
start.explore(stateList)

solve(start, "876543210", stateList)