from urllib.request import urlopen
import re
import graph_tool.all as gt
from concurrent.futures import ThreadPoolExecutor
import time

base_url = "https://webscraper.io/test-sites/e-commerce/allinone" # URL to scrape
depth = 2  # Depth of recursion for link extraction
debug_mode = True  # Set to True to enable debug mode

def extract_html(url : str) -> str:
    """Fetch HTML content from a URL."""
    try:
        return urlopen(url).read().decode("utf-8")
    except Exception as e:
        if debug_mode:
            print(f"Error fetching {url}: {e}")
        return ""

def extract_links(html: str) -> list:
    """Extract links from HTML content."""
    return re.findall('href="/([^"]+?)(?=[?"])', html)

def prune_links(url: str, links: list) -> list:
    """Prune links to remove duplicates and ensure they are absolute."""
    seen = set()
    pruned_links = []
    domain = url.split("/")[0] + "//" + url.split("/")[2]
    for link in links:
        link = link.strip()
        if not link.startswith("http"):
            if not link.startswith("/"):
                link = "/" + link
            link = domain + link
        if link in seen:
            continue
        seen.add(link)
        if ".css" in link or ".js" in link or ".php" in link or ".json" in link or ".xml" in link:
            continue # Skip static files
        if "mailto:" in link:
            continue # Skip mailto links
        if "googleapis.com" in link or "gstatic.com" in link or "googleusercontent.com" in link or "google.com" in link:
            continue # Skip Google API and Gstatic links
        if "linkedin.com" in link:
            continue # Skip LinkedIn links
        if "facebook.com" in link:
            continue # Skip Facebook links
        if "twitter.com" in link or "x.com" in link:
            continue # Skip Twitter links
        if "instagram.com" in link:
            continue # Skip Instagram links
        if "youtube.com" in link or "youtu.be" in link:
            continue # Skip YouTube links
        if ".zip" in link or ".tar" in link or ".gz" in link:
            continue # Skip archive files
        if ".ico" in link or ".png" in link or ".jpg" in link or ".jpeg" in link or ".gif" in link or ".bmp" in link or ".svg" in link or ".webp" in link:
            continue # Skip image files
        pruned_links.append(link)
    return pruned_links

g = gt.Graph(directed=True)  # Create a directed graph 

eweight = g.new_ep("float")
vcolor = g.new_vp("string")
vlink = g.new_vp("string")

origin = g.add_vertex()  # Add an origin vertex
vcolor[origin] = "#ff0000"  # Color the origin vertex red

next_stage_vertices = []  # List to keep track of vertices at the next stage
def add_links_to_graph(url: str, depth: int, current_depth: int = 0, origin_vert: gt.Vertex = origin) -> None:
    if current_depth >= depth:
        return
    
    links = prune_links(url, extract_links(extract_html(url)))

    for link in links:
        vertex = g.add_vertex()  # Add a new vertex for the link
        e = g.add_edge(origin_vert, vertex)  # Create an edge from origin to the new vertex
        eweight[e] = 10.0 / len(links)  # Set the edge weight based on the number of links
    
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
        vlink[vertex] = link  # Store the link in the vertex property
        next_stage_vertices.append(vertex)
    if next_stage_vertices:
        with ThreadPoolExecutor() as executor:
            # Submit the next stage of link extraction for each vertex in parallel
            futures = [executor.submit(add_links_to_graph, vlink[v], depth, current_depth + 1, v) for v in next_stage_vertices]
# Start the recursive link extraction from the base url
# The block will make sure that if we hit Ctrl+C, the graph will still be drawn
# Unless we hit it twice, in which case it will exit immediately
start_time = time.time()
try:
    add_links_to_graph(base_url, depth)
finally:
    gt.graph_draw(g, vertex_fill_color=vcolor, edge_pen_width=eweight, output="output.svg")
    print(f"Graph drawn in {time.time() - start_time:.2f} seconds.")
