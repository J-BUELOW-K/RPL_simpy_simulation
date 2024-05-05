import networkx as nx
import matplotlib.pyplot as plt



class Student:
    def __init__(self, name, grade, age):
        self.name = name
        self.grade = grade
        self.age = age
    def __repr__(self):
        return repr((self.name, self.grade, self.age))


def main():
    
    student_objects = [
    Student('john', 'A', 15),
    Student('jane', 'B', 12),
    Student('dave', 'B', 10),
    ]   
    
    print(student_objects)
    student_objects_sorted = sorted(student_objects, key=lambda hi: hi.age)   # sort by age    
    print(student_objects_sorted)
    
    
    
    
    
    
    # temp = []
    # print(temp)
    # print(len(temp))
    # G = nx.Graph([(0, 1), (1, 2), (1, 3), (3, 4)])
    # layers = {"Rank 0": [0], "Rank 1": [1], "Rank 2": [2, 3], "Rank 3": [4]}
    # pos = nx.multipartite_layout(G, subset_key=layers, align="horizontal")

    # for i in range(0, len(pos)):     
    #     pos[i][1] *= -1


    # nx.draw(G, pos=pos, with_labels=True)
    # plt.show()


if __name__=="__main__":
    main()