import networkx as nx
import matplotlib.pyplot as plt



def main():
    G = nx.Graph([(0, 1), (1, 2), (1, 3), (3, 4)])
    layers = {"Rank 0": [0], "Rank 1": [1], "Rank 2": [2, 3], "Rank 3": [4]}
    pos = nx.multipartite_layout(G, subset_key=layers, align="horizontal")

    print(pos[0][1])

    nx.draw(G,pos=pos, with_labels=True)
    plt.show()


# if __name__=="__main__":
#     main()