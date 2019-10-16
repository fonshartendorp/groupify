# Groupify

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
