import networkx as nx
import matplotlib.pyplot as plt



def main():
    G = nx.Graph([(0, 1), (1, 2), (1, 3), (3, 4)])
    layers = {"a": [0], "b": [1], "c": [2, 3], "d": [4]}
    pos = nx.multipartite_layout(G, subset_key=layers)

    nx.draw(G,pos=pos, with_labels=True)
    plt.show()


if __name__=="__main__":
    main()