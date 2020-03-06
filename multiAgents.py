# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "Features to calculate: " \
        "- avFoodDist || av new distance from all food (excluding the one that may be eaten)" \
        "+ eatBonus || fixed value for eating a food" \
        "- deathwish || fixed value for getting within 1 square of any non-scared ghost" \
        "+ dangerSense || av new distance from all non-scared ghosts" \
        "- huntingSense || av new distance from all scared ghost"
        avFoodDist = 0
        foodList = newFood.asList()
        for food in foodList:
            avFoodDist += util.manhattanDistance(food, newPos)
        avFoodDist /= max(newFood.count(), 1)
        eatBonus = 0
        if (currentGameState.getNumFood() > successorGameState.getNumFood()):
            eatBonus = 1
        deathwish = 0
        dangerSense = 0
        dangers = 0
        huntingSense = 0
        for ghost in newGhostStates:
            if ghost.scaredTimer == 0:
                dangers += 1
                temp = util.manhattanDistance(newPos, ghost.getPosition())
                dangerSense += temp
                if temp < 2:
                    deathwish += 1
            else:
                huntingSense += util.manhattanDistance(newPos, ghost.getPosition())
        dangerSense /= max(dangers, 1)
        huntingSense /= max(len(newGhostStates) - dangers, 1)

        return -avFoodDist + 100*eatBonus - 10*deathwish + 0.5*dangerSense - huntingSense

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        scaledDepthLimit = self.depth*gameState.getNumAgents()
        value = -100000000
        for action in gameState.getLegalActions(0):
            candidate = self.getValue(gameState.generateSuccessor(0, action),
                                             2, 1, scaledDepthLimit)
            if candidate > value:
                value = candidate
                move = action
        return move



    def getValue(self, gameState, currentDepth, agentIndex, scaledDepthLimit):
        """
        Current depth tells the recursive function how deep it is based on the call stack.
        For example, at the top of the minimax tree, currentDepth = 1. When this function
        is called to evaluate the agent acting directly next, currentdepth = 2.

        Scaled Depth is the maximum number of recursive calls that can be resolved in the minimax search.
        It varies based on the depth allowed and the number of agents.
        """
        if gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)
        if currentDepth > scaledDepthLimit:
            return self.evaluationFunction(gameState)
        if agentIndex == 0:
            return self.maxValue(gameState, currentDepth, agentIndex, scaledDepthLimit)
        else:
            return self.minValue(gameState, currentDepth, agentIndex, scaledDepthLimit)


    def maxValue(self, gameState, currentDepth, agentIndex, scaledDepthLimit):
        value = -100000000
        for act in gameState.getLegalActions(agentIndex):
            nextAgent = (agentIndex+1)%gameState.getNumAgents()
            value = max(value, self.getValue(gameState.generateSuccessor(agentIndex, act),
                                             currentDepth+1, nextAgent, scaledDepthLimit))
        return value

    def minValue(self, gameState, currentDepth, agentIndex, scaledDepthLimit):
        value = +100000000
        for act in gameState.getLegalActions(agentIndex):
            nextAgent = (agentIndex + 1) % gameState.getNumAgents()
            value = min(value, self.getValue(gameState.generateSuccessor(agentIndex, act),
                                             currentDepth + 1, nextAgent, scaledDepthLimit))
        return value

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        scaledDepthLimit = self.depth*gameState.getNumAgents()
        value = -100000000
        alpha = 100000000
        beta = -100000000
        for action in gameState.getLegalActions(0):
            candidate = self.getValue(gameState.generateSuccessor(0, action),
                                             2, 1, scaledDepthLimit, alpha, beta)
            if candidate > value:
                value = candidate
                move = action
        return move



    def getValue(self, gameState, currentDepth, agentIndex, scaledDepthLimit, alpha, beta):
        """
        Current depth tells the recursive function how deep it is based on the call stack.
        For example, at the top of the minimax tree, currentDepth = 1. When this function
        is called to evaluate the agent acting directly next, currentdepth = 2.

        Scaled Depth is the maximum number of recursive calls that can be resolved in the minimax search.
        It varies based on the depth allowed and the number of agents.
        """
        if gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)
        if currentDepth > scaledDepthLimit:
            return self.evaluationFunction(gameState)
        if agentIndex == 0:
            return self.maxValue(gameState, currentDepth, agentIndex, scaledDepthLimit, alpha, beta)
        else:
            return self.minValue(gameState, currentDepth, agentIndex, scaledDepthLimit, alpha, beta)


    def maxValue(self, gameState, currentDepth, agentIndex, scaledDepthLimit, alpha, beta):
        value = -100000000
        for act in gameState.getLegalActions(agentIndex):
            nextAgent = (agentIndex+1)%gameState.getNumAgents()
            value = max(value, self.getValue(gameState.generateSuccessor(agentIndex, act),
                                             currentDepth+1, nextAgent, scaledDepthLimit, alpha, beta))
            if value > beta:
                return value
            alpha = max(alpha, value)
        return value

    def minValue(self, gameState, currentDepth, agentIndex, scaledDepthLimit, alpha, beta):
        value = +100000000
        for act in gameState.getLegalActions(agentIndex):
            nextAgent = (agentIndex + 1) % gameState.getNumAgents()
            value = min(value, self.getValue(gameState.generateSuccessor(agentIndex, act),
                                             currentDepth + 1, nextAgent, scaledDepthLimit, alpha, beta))
            if value < alpha:
                return value
            beta = min(beta, value)
        return value

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        scaledDepthLimit = self.depth * gameState.getNumAgents()
        value = -100000000
        for action in gameState.getLegalActions(0):
            candidate = self.getValue(gameState.generateSuccessor(0, action),
                                      2, 1, scaledDepthLimit)
            if candidate > value:
                value = candidate
                move = action
        return move

    def getValue(self, gameState, currentDepth, agentIndex, scaledDepthLimit):
        """
        Current depth tells the recursive function how deep it is based on the call stack.
        For example, at the top of the minimax tree, currentDepth = 1. When this function
        is called to evaluate the agent acting directly next, currentdepth = 2.

        Scaled Depth is the maximum number of recursive calls that can be resolved in the minimax search.
        It varies based on the depth allowed and the number of agents.
        """
        if gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)
        if currentDepth > scaledDepthLimit:
            return self.evaluationFunction(gameState)
        if agentIndex == 0:
            return self.maxValue(gameState, currentDepth, agentIndex, scaledDepthLimit)
        else:
            return self.expectedValue(gameState, currentDepth, agentIndex, scaledDepthLimit)

    def maxValue(self, gameState, currentDepth, agentIndex, scaledDepthLimit):
        value = -100000000
        for act in gameState.getLegalActions(agentIndex):
            nextAgent = (agentIndex + 1) % gameState.getNumAgents()
            value = max(value, self.getValue(gameState.generateSuccessor(agentIndex, act),
                                             currentDepth + 1, nextAgent, scaledDepthLimit))
        return value

    def expectedValue(self, gameState, currentDepth, agentIndex, scaledDepthLimit):
        value = 0
        actions = gameState.getLegalActions(agentIndex)
        for act in actions:
            nextAgent = (agentIndex + 1) % gameState.getNumAgents()
            value += self.getValue(gameState.generateSuccessor(agentIndex, act),
                                             currentDepth + 1, nextAgent, scaledDepthLimit)
        return value/len(actions)

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    # Useful information you can extract from a GameState (pacman.py)
    pos = currentGameState.getPacmanState().getPosition()
    ghostStates = currentGameState.getGhostStates()

    "Features to calculate: " \
    "+ dangerSense || av distance from all non-scared ghosts (zero if no ghosts are within 4 spaces)" \
    "- foodCount || number of food left on the map" \
    "+ score || the current score at the sates" \
    "- capsNum || the umber of capsules left on the map"

    dangerSense = 0
    dangers = 0
    huntingSense = 0
    closestGhost = float("inf")
    for ghost in ghostStates:
        if ghost.scaredTimer == 0:
            dangers += 1
            temp = util.manhattanDistance(pos, ghost.getPosition())
            dangerSense += temp
            if temp < closestGhost:
                closestGhost = temp
        else:
            huntingSense += util.manhattanDistance(pos, ghost.getPosition())
    dangerSense /= max(dangers, 1)
    "don't worry about ghosts at all unless they are close"
    if closestGhost >= 4:
        dangerSense = 0
    huntingSense /= max(len(ghostStates) - dangers, 1)
    foodCount = currentGameState.getNumFood()
    score = currentGameState.getScore()
    capsNum = len(currentGameState.getCapsules())
    return 0.4*dangerSense + 0.3*score - 3*foodCount - 3*capsNum

# Abbreviation
better = betterEvaluationFunction
