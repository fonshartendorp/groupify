#! /usr/bin/env python3

"""
Python script as used by my old high school to assign students to one of their
prefered trips. The most optimal assignment is determined by implementing
the Ford-Fulkerson algorithm. All students and trips are added to a graph and
finding the most optimal assigning scheme is reduced to a max-flow problem on
this graph.

TODO:
x Parse input from their .csv file.
- Change print statements to proper print formatting.
- Find better solution to terminate algorithm if not every student can be
  assigned to one of his preferences.
"""
import fileinput
import csv
import sys
import re

SOURCE = 'source'
SINK = 'sink'
mates = {}
start = 0
r = 0


def checkMates(student):
    """
    If the student applied as pair, returns his/her mate.
    """

    if student in mates:
        print(mates[student])


def beautifyOutcome(flow, trips):
    """
    Just for development purposes.
    """
    edges = []

    # First select the edges with a flow of 1.
    filterDict = {k:v for (k,v) in flow.items() if v==1}

    # Convert from dict to list of tuples.
    for k, v in filterDict.items():
        edges.append(tuple([str(k).split(',')[0], str(k).split(',')[1]]))

    # Filter on edges between students and trips.
    # filteredEdges = [(x,y) for (x,y) in edges if re.search("student_[0-9]+", x)]
    filteredEdges = [(x,y) for (x,y) in edges if re.search("student_[A-z, ]+", x)]

    for trip in trips:
        print('---------------' + trip.upper()+ '---------------')
        localStudents = set([edge[0] for edge in filteredEdges if edge[1] == trip])

        [print(student.split('_')[1]) for student in localStudents]
        print('Aantal: ' + str(len(localStudents)))

        print('------------------------------------\n')


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


def parseCSV(students, trips, g, file):
    """
    Parses .csv input file for getting the students names and preferences.
    """
    fields = []

    with open(file, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        capacity = 1

        # Trips as offered by my high-school in 2019. The integer is the
        # maximum number of students every trip can take.
        trips = {'Citysurf': 44,
                 'Kitesurfen': 24,
                 'Lekker thuis': 46,
                 'Survival': 41,
                 'Londen': 35,
                 'Rome': 43,
                 'Schotland': 23,
                 'Zuid-Polen': 44,
                 'Venetië': 37,
                 'Geen keuze gemaakt': 10}

        # Get trips and capacities.
        for werkweek, capacitet in trips.items():
            g.addVertex(werkweek)
            g.addEdge(werkweek, SINK, capacitet)

        for row in csvreader:
            # Get students name.
            name = row[0].split('(')[0].rstrip(' ')
            firstname = name.split(',')[1].rstrip(' ')
            lastname = name.split(',')[0].rstrip(' ')
            student = 'student_' + firstname + ' ' + lastname

            # Get his three preferences
            option1 = row[1]
            option2 = row[2]
            option3 = row[3]

            # If the student is not yet in the graph, add its vertex and and
            # edge from the source to student vertex to the graph.
            if student not in students:
                g.addVertex(student)
                g.addEdge(SOURCE, student, capacity)
                students.append(student)

            # Add the three preference-edges to the graph.
            g.addEdge(student, option1, 1)
            g.addEdge(student, option2, 1)
            g.addEdge(student, option3, 1)

    return students, trips, g


def parseInput(students, trips, g):
    """
    Parses input from .txt file.
    """
    for line in fileinput.input():

        if line.split(',')[0].isalpha():
            # If the line denotes a trip.
            trip = 'trip_' + line.split(' ')[0]
            capacity = int(line.split(' ')[1].rstrip())

            # If this trip is not yet in the graph, add it together with a
            # edge to the sink vertex.
            if trip not in trips:
                g.addVertex(trip)
                g.addEdge(trip, SINK, capacity)
                trips.append(trip)

        if line != '\n':
            # If not, the line denotes a student and his three preferences.
            student = 'student_' + line.split(',')[0]
            mate = 'student_' + line.split(',')[1]
            capacity = 1

            if mate != 'student_0':
                if mate not in mates:
                    capacity = 2
                    mates['student_' + line.split(',')[0]] = mate
                else:
                    continue

            # Get his three preferences.
            option1 = 'trip_' + line.split(',')[2].rstrip()
            option2 = 'trip_' + line.split(',')[3].rstrip()
            option3 = 'trip_' + line.split(',')[4].rstrip()

            # If the student is not yet in the graph, add its vertex and and
            # edge from the source to student vertex to the graph.
            if student not in students:
                g.addVertex(student)
                g.addEdge(SOURCE, student, capacity)
                students.append(student)

            # Add the three preference-edges to the graph.
            g.addEdge(student, option1, 1)
            g.addEdge(student, option2, 1)
            g.addEdge(student, option3, 1)

    return students, trips, g


class Edge(object):
    """
    Class for edge objects. Every edge has an origin, destination and
    capacity. For the edges from the trips to the sink vertex, this capacity
    equals the maximum number of students that can be assigned to this trip.
    The other edges usually have a capacity of 1, except for the students whom
    formed pairs.

    """
    def __init__(self, u, v, w=1):
        self.origin = u
        self.destination = v
        self.capacity = w

    def __repr__(self):
        return '{},{}'.format(self.origin, self.destination)


class Graph(object):
    """
    Class for graph objects. Each graph objects has a dictionary for its
    vertices and its flow.

    Based on: https://startupnextdoor.com/maximum-flow-minimum-cut-and-the-
            ford-fulkerson-method/
    """
    def __init__(self):
        self.vertices = {}
        self.flow = {}

    # Add a empty list of edges to this vertex in the vertices dict.
    def addVertex(self, vertex):
        self.vertices[vertex] = []

    # Returns adjecent edges.
    def getEdges(self, v):
        return self.vertices[v]

    def printEdges(self):
        for vertex in self.vertices:
            print(vertex)
            for edge in self.vertices[vertex]:
                print(edge)
            print("---")

    def printFlow(self):
        for edge in self.flow:
            print(edge)

    # Adds edge from vertex u to v with capacity w.
    def addEdge(self, u, v, w):
        edge = Edge(u, v, w)
        # Also adds a return edge, later used for calculating the residual.
        returnEdge = Edge(v, u, 0)
        edge.returnEdge = returnEdge
        returnEdge.returnEdge = edge
        # Append edge to the edges-list for both vertices.
        self.vertices[u].append(edge)
        self.vertices[v].append(returnEdge)
        # Initally set flow to
        self.flow[edge] = 0
        self.flow[returnEdge] = 0

    def findPath(self, origin, destination, path):
        """
        Recursively finds still possible paths.
        """
        # R is used to terminate algorithm if there is no optimal solution
        # where every student is assigned to one of his preferences. Bit of a
        # hacky solution, need to find something better here.
        global r
        r += 1
        if r > 100000:
            return None

        # Meaning we have arrived.
        if origin == destination:
            return path

        for edge in self.getEdges(origin):
            # calculating residual flow.
            residual = edge.capacity - self.flow[edge]

            if residual > 0 and edge not in path:
                # If still residual and edge is not yet in this path (no
                # cycles), add edge to path and recursively find next edge.
                result = self.findPath(edge.destination,
                                       destination,
                                       path + [edge])


                if result is not None:
                    return result

    def fordFulkerson(self, origin, destination):
        """
        Where the magic happens. Implements a version of the Ford Fulkerson
        algorithm.
        """
        # Find a possible path from source to sink vertex.
        path = self.findPath(origin, destination, [])
        while path is not None:

            # Gather list with residuals of all edges.
            residuals = [edge.capacity - self.flow[edge] for edge in path]
            # The flow is the minimum of these residuals.
            flow = min(residuals)

            # Update every edge with this flow.
            for edge in path:
                self.flow[edge] += flow
                self.flow[edge.returnEdge] -= flow

            # And try to find a new possible path.
            path = self.findPath(origin, destination, [])

        # Eventually no possible paths with residual are to be found anymore.
        # Then the max flow has been determined. The number of students
        # assigned is returned by taking the sum of the flow for every edge.
        return sum(self.flow[edge] for edge in self.getEdges(origin))


def main():
    """
    Initialize graph, add source and sink vertices. Parse input, run
    Ford-Fulkerson algorithm and print outcome.
    """
    students = []
    trips = []
    g = Graph()
    file = sys.argv[1]

    # Start with a sink and a source vertex.
    g.addVertex(SOURCE)
    g.addVertex(SINK)

    # Parse input and add student-, tripvertices and edges to graph.
    # students, trips, g = parseInput(students, trips, g)
    students, trips, g = parseCSV(students, trips, g, file)

    numberAssigned = g.fordFulkerson(SOURCE, SINK)
    print('Students assigned: ' + str(numberAssigned) + '/' + str(len(students)))
    print('Number of trips: ' + str(len(trips)) + '\n')

    beautifyOutcome(g.flow, trips)


if __name__ == '__main__':
    main()
