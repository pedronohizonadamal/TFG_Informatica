import networkx as nx
import matplotlib.pyplot as plt
# import graph as g

P_VALUE = 1
Q_VALUE = -1
R_VALUE = 0 

def count_opinions(G):
    pass
def get_colours(G):
    colour_table = {
        P_VALUE:"red",
        Q_VALUE:"blue",
        R_VALUE:"green"
    }
    return [colour_table[G.nodes[node]["opinion"]] if G.nodes[node]["is_broadcaster"] == False else "purple" for node in G.nodes]
        
 
def visualize_graph(G):
    nx.draw_networkx(G, node_color=get_colours(G))
    plt.show()
    
if __name__ == "__main__":
    G = None # g.generate_graph()
    print(count_opinions(G))
    nx.draw_networkx(G, node_color=get_colours(G))
    plt.show()