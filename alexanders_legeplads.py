import networkx as nx
import matplotlib.pyplot as plt
import graphviz


class Student:
    def __init__(self, name, grade, age):
        self.name = name
        self.grade = grade
        self.age = age
    def __repr__(self):
        return repr((self.name, self.grade, self.age))


def main():

    
    f = graphviz.Digraph()
    names = ["A","B","C","D","E","F","G","H"]
    positions = ["CEO","Team A Lead","Team B Lead", "Staff A","Staff B", "Staff C", "Staff D", "Staff E"]
    for name, position in zip(names, positions):
        f.node(name, position)
    
    f.format = 'png'

    #Specify edges
    f.edge("A","B"); f.edge("A","C") #CEO to Team Leads
    f.edge("B","D"); f.edge("B","E") #Team A relationship
    f.edge("C","F"); f.edge("C","G"); f.edge("C","H") #Team B relationship
    
    f.render(directory='doctest-output', view=True)

   


if __name__=="__main__":
    main()