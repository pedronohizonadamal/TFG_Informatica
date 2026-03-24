import networkx as nx
import matplotlib.pyplot as plt
import graph as g
 
def get_colours(G):
    colour_table = {
        g.P_VALUE:"red",
        g.R_VALUE:"green",
        g.Q_VALUE:"blue"
    }
    return [colour_table[G.nodes[node]["opinion"]] for node in G.nodes]
 
G = g.generate_graph()
nx.draw_networkx(G, node_color=get_colours(G))
plt.show()
