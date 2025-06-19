from urllib.request import urlopen
import re
import graph_tool.all as gt


url = "https://webscraper.io/test-sites/e-commerce/allinone" # URL to scrape

page = urlopen(url)
html = page.read().decode("utf-8")  # Read and decode the HTML content

direct_links = re.findall('https*:.+?(?=[?"])', html)  # Find all URLs in the HTML content

same_page_links = re.findall('href="/([^"]+?)(?=[?"])', html)  # Find all relative links

for i in range(len(same_page_links)):
    same_page_links[i] = url + "/" + same_page_links[i]  # Convert relative links to absolute links

g = gt.Graph(directed=True)  # Create a directed graph 

eweight = g.new_ep("float")
vcolor = g.new_vp("string")

origin = g.add_vertex()  # Add an origin vertex
vcolor[origin] = "#ff0000"  # Color the origin vertex red

for link in direct_links:
    v = g.add_vertex()  # Add each link as a vertex in the graph 
    vcolor[v] = "#0000ff"  # Color the vertex blue
    e = g.add_edge(origin, v)
    eweight[e] = 3.0  # Set edge weight to 1.0

gt.graph_draw(g, vertex_fill_color=vcolor, edge_pen_width=eweight, output="output.svg")
