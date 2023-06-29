class Node:
    """
    Represent a node or position in the Labyrinth
    f is the total cost of the node
    g is the distance between this node and the start
    h is the heuristic or estimated distance between this node and the end
    """
    def __init__(self, parent=None, position=None, orientation='h'):
        self.parent = parent
        self.position = position
        self.orientation = orientation

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position and self.orientation == other.orientation

    def __str__(self):
        return "({}, {}), {}".format(self.position[0], self.position[1], self.orientation)


class Labyrinth:
    """
    Represent a Labyrinth, including the rod
    """
    def __init__(self, labyrinth, x=1, y=0, orientation='h'):
        self.labyrinth = labyrinth

        # Initial position of the rod
        self.x = x
        self.y = y
        self.orientation = orientation

        # Check the input labyrinth is valid (initial position not blocked)
        assert orientation == 'h' or orientation == 'v'
        if orientation == 'h':
            assert self.labyrinth[y][x] == '.' and self.labyrinth[y][x - 1] == '.' and self.labyrinth[y][x + 1] == '.', "Invalid initial position"
        elif orientation == 'v':
            assert self.labyrinth[y][x] == '.' and self.labyrinth[y - 1][x] == '.' and self.labyrinth[y + 1][x] == '.', "Invalid initial position"

    def solve(self, display=False):
        """
        Solves the labyrinth checking if the final vertical or horizontal position is better

        display determines if the solution is printed

        Note that we subtract 1 from the length of the path because we only want the number of moves, not the number of nodes
        """
        solution1 = self.aStar((len(self.labyrinth) - 2, len(self.labyrinth[0]) - 1), 'v')
        solution2 = self.aStar((len(self.labyrinth) - 1, len(self.labyrinth[0]) - 2), 'h')

        if solution1 is not None:
            # If both solutions are valid
            if solution2 is not None and len(solution2) < len(solution1):
                if display:
                    self.displaySolution(solution2)
                return len(solution2) - 1

            # If only solution1 (vertical) is valid
            else:
                if display:
                    self.displaySolution(solution1)
                return len(solution1) - 1

        # If only solution2 (horizontal) is valid
        elif solution2 is not None:
            if display:
                self.displaySolution(solution2)
            return len(solution2) - 1

        # If there is no solution
        else:
            return -1

    def aStar(self, end, endOrientation):
        """
        Solves the labyrinth using the A* Pathfinding Algorithm
        Requieres the final position and orientation
        """

        # Check the final position is valid
        if self.labyrinth[end[0]][end[1]] == "#":
            return None

        # Create the initial node
        startNode = Node(None, (self.y, self.x), self.orientation)
        startNode.g = 0
        startNode.h = 0
        startNode.f = 0

        # Create the final node
        endNode = Node(None, end, endOrientation)
        endNode.g = 0
        endNode.h = 0
        endNode.f = 0

        # List to store the nodes that need to be explored
        openList = []
        openList.append(startNode)

        # List to store the explored nodes
        closedList = []

        # Loop while there are still nodes to be explored
        while len(openList) > 0:
            currentNode = openList[0]
            currentIndex = 0

            # Explore the best node
            for index, item in enumerate(openList):
                if item.f < currentNode.f:
                    currentNode = item
                    currentIndex = index

            # Remove the current node from the nodes to be explored and add it to the already explored nodes
            openList.pop(currentIndex)
            closedList.append(currentNode)

            # Check if done
            if currentNode == endNode:
                path = []
                current = currentNode
                while current is not None:
                    path.append((current.position, current.orientation))
                    current = current.parent
                return path[::-1]

            # Add new nodes to be explored
            children = []

            # Rotations
            if currentNode.position[0] - 1 >= 0 and currentNode.position[0] + 1 < len(self.labyrinth) and \
                    currentNode.position[1] - 1 >= 0 and currentNode.position[1] + 1 < len(self.labyrinth[0]):
                # Check if the rod has space to rotate
                valid = True
                for checkMoves in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    checkPosition = (currentNode.position[0] + checkMoves[0], currentNode.position[1] + checkMoves[1])
                    if self.labyrinth[checkPosition[0]][checkPosition[1]] != '.':
                        valid = False

                if valid:
                    # Horizontal to vertical
                    if currentNode.orientation == 'h':
                        newNode = Node(currentNode, currentNode.position, 'v')
                        children.append(newNode)
                    # Vertical to horizontal
                    elif currentNode.orientation == 'v':
                        newNode = Node(currentNode, currentNode.position, 'h')
                        children.append(newNode)

            # Expand current node
            for newPosition in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nodePosition = (currentNode.position[0] + newPosition[0], currentNode.position[1] + newPosition[1])

                # Check position inside labyrinth
                if nodePosition[0] > len(self.labyrinth) - 1 or nodePosition[0] < 0 or nodePosition[1] > len(
                        self.labyrinth[0]) - 1 or nodePosition[1] < 0:
                    continue

                # Check wall
                if self.labyrinth[nodePosition[0]][nodePosition[1]] != '.':
                    continue

                # Check non-center nodes
                if currentNode.orientation == 'h':
                    if nodePosition[1] - 1 < 0 or self.labyrinth[nodePosition[0]][nodePosition[1] - 1] != '.' or nodePosition[1] + 1 > len(self.labyrinth[0]) - 1 or self.labyrinth[nodePosition[0]][nodePosition[1] + 1] != '.':
                        continue
                elif currentNode.orientation == 'v':
                    if nodePosition[0] - 1 < 0 or self.labyrinth[nodePosition[0] - 1][nodePosition[1]] != '.' or nodePosition[0] + 1 > len(self.labyrinth) - 1 or self.labyrinth[nodePosition[0] + 1][nodePosition[1]] != '.':
                        continue

                newNode = Node(currentNode, nodePosition, currentNode.orientation)
                children.append(newNode)

            # Check if the new nodes have been explored or already added to the list to explore, and calculate their
            # values
            for child in children:
                add = True
                for closedChild in closedList:
                    if child == closedChild:
                        add = False

                child.g = currentNode.g + 1
                child.h = ((child.position[0] - endNode.position[0]) ** 2) + (
                        (child.position[1] - endNode.position[1]) ** 2)
                child.f = child.g + child.h

                for openNode in openList:
                    if child == openNode and child.g > openNode.g:
                        add = False
                if add:
                    openList.append(child)

    def displaySolution(self, path):
        """
        Displays the solution indicated in path
        """
        print("\nSolving Labyrinth...\n")
        for i in range(len(path)):
            print("\t> Moves: {}".format(i))
            print(Labyrinth(self.labyrinth, path[i][0][1], path[i][0][0], path[i][1]))
        print("Done solving!")

    def __str__(self):
        """
        Print the current state of the labyrinth and the rod
        """
        output = ""
        for i in range(len(self.labyrinth)):
            for j in range(len(self.labyrinth[0])):
                if self.orientation == 'h' and j - 1 <= self.x <= j + 1 and self.y == i:  # Horizontal
                    output += " x "
                elif self.orientation == 'v' and i - 1 <= self.y <= i + 1 and self.x == j:  # Vertical
                    output += " x "
                else:
                    output += " " + self.labyrinth[i][j] + " "
            output += "\n"
        return output


# ----- CHECK TESTS ----- #

labyrinth1 = [[".", ".", ".", ".", ".", ".", ".", ".", "."],
              ["#", ".", ".", ".", "#", ".", ".", ".", "."],
              [".", ".", ".", ".", "#", ".", ".", ".", "."],
              [".", "#", ".", ".", ".", ".", ".", "#", "."],
              [".", "#", ".", ".", ".", ".", ".", "#", "."]]
labyrinth = Labyrinth(labyrinth1)
print("Labyrinth 1 results:", labyrinth.solve(True))

labyrinth2 = [[".", ".", ".", ".", ".", ".", ".", ".", "."],
              ["#", ".", ".", ".", "#", ".", ".", "#", "."],
              [".", ".", ".", ".", "#", ".", ".", ".", "."],
              [".", "#", ".", ".", ".", ".", ".", "#", "."],
              [".", "#", ".", ".", ".", ".", ".", "#", "."]]
labyrinth = Labyrinth(labyrinth2)
print("Labyrinth 2 results:", labyrinth.solve(False))

labyrinth3 = [[".", ".", "."],
              [".", ".", "."],
              [".", ".", "."]]
labyrinth = Labyrinth(labyrinth3)
print("Labyrinth 3 results:", labyrinth.solve(False))

labyrinth4 = [[".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
              [".", "#", ".", ".", ".", ".", "#", ".", ".", "."],
              [".", "#", ".", ".", ".", ".", ".", ".", ".", "."],
              [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
              [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
              [".", "#", ".", ".", ".", ".", ".", ".", ".", "."],
              [".", "#", ".", ".", ".", "#", ".", ".", ".", "."],
              [".", ".", ".", ".", ".", ".", "#", ".", ".", "."],
              [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
              [".", ".", ".", ".", ".", ".", ".", ".", ".", "."]]
labyrinth = Labyrinth(labyrinth4)
print("Labyrinth 4 results:", labyrinth.solve(False))

# Bonus

labyrinth5 = [[".", ".", ".", "#", ".", ".", ".", ".", ".", ".", "."],
              [".", ".", ".", "#", ".", ".", ".", "#", ".", ".", "."],
              [".", ".", ".", "#", ".", ".", ".", "#", ".", ".", "."],
              [".", "#", "#", "#", ".", "#", "#", "#", "#", "#", "."],
              [".", "#", ".", ".", ".", ".", ".", ".", ".", "#", "."],
              [".", "#", ".", ".", ".", "#", ".", ".", ".", "#", "."],
              [".", "#", ".", ".", ".", "#", ".", ".", ".", "#", "."],
              [".", "#", "#", "#", "#", "#", "#", "#", ".", "#", "."],
              [".", ".", ".", ".", ".", "#", ".", ".", ".", "#", "."],
              [".", ".", ".", ".", ".", "#", ".", ".", ".", "#", "."],
              [".", ".", ".", ".", ".", ".", ".", ".", ".", "#", "."]]
labyrinth = Labyrinth(labyrinth5)
print("Labyrinth 5 results:", labyrinth.solve(True))
