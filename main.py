from urllib.request import urlopen
import re
import graph_tool.all as gt


base_url = "https://webscraper.io/test-sites/e-commerce/allinone" # URL to scrape

def extract_html(url : str) -> str:
    return urlopen(url).read().decode("utf-8")

def extract_direct_links(html: str) -> list:
    return re.findall('href="([^"]+?)(?=[?"])', html)

def extract_same_page_links(html: str) -> list:
    return re.findall('href="/([^"]+?)(?=[?"])', html)

html = extract_html(base_url)  # Fetch the HTML content 
direct_links = extract_direct_links(html)  # Extract direct links 
same_page_links = extract_same_page_links(html)  # Extract same page links 


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
