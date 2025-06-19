from urllib.request import urlopen
import re
import graph_tool.all as gt


base_url = "https://webscraper.io/test-sites/e-commerce/allinone" # URL to scrape
depth = 2  # Depth of recursion for link extraction

def extract_html(url : str) -> str:
    try:
        return urlopen(url).read().decode("utf-8")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

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

# TODO(Dory): Make recursive function to extract links from each page
def add_links_to_graph(url: str, depth: int, current_depth: int = 0) -> None:
    if current_depth >= depth:
        return
    
    html = extract_html(url)  # Fetch the HTML content of the page
    links = extract_direct_links(html) + extract_same_page_links(html)  # Extract all links

    for link in links:
        if not link.startswith("http"):
            link = base_url + link  # Construct full URL if it's a relative link
        
        vertex = g.add_vertex()  # Add a new vertex for the link
        e = g.add_edge(origin, vertex)  # Create an edge from origin to the new vertex
        eweight[e] = 1.0
    
        # The vertex color can be set based on the depth or other criteria
        if current_depth == 0:
            vcolor[vertex] = "#00ff00"
        elif current_depth == 1:
            vcolor[vertex] = "#0000ff"
        elif current_depth == 2:
            vcolor[vertex] = "#ffff00"
        elif current_depth == 3:
            vcolor[vertex] = "#ff00ff"
        elif current_depth == 4:
            vcolor[vertex] = "#00ffff"
        else:
            vcolor[vertex] = "#ffffff"
        add_links_to_graph(link, depth, current_depth + 1)  # Recur for the next depth

# Start the recursive link extraction from the base url
add_links_to_graph(base_url, depth)

gt.graph_draw(g, vertex_fill_color=vcolor, edge_pen_width=eweight, output="output.png")
