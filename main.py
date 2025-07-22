from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import re
import graph_tool.all as gt
from concurrent.futures import ThreadPoolExecutor
import time
import sys

# Variables that CAN NOT be modified by the user
MAX_DEPTH = 5  # Maximum depth of recursion

# Variables that CAN be modified by the user
base_url = "https://github.com/dorythecat" # URL to scrape
depth = 3  # Depth of recursion for link extraction
output_file = "output.png"  # Output file name for the graph image
debug_mode = False  # Enable debug mode for verbose output

forbidden_content = [ # List of content to skip
    ".css", ".js", ".php", ".json", ".xml", "mailto:", "googleapis.com",
    "gstatic.com", "googleusercontent.com", "google.com", "linkedin.com",
    "facebook.com", "twitter.com", "x.com", "instagram.com", "youtube.com",
    "youtu.be", ".zip", ".tar", ".gz", ".ico", ".png", ".jpg", ".jpeg",
    ".gif", ".bmp", ".svg", ".webp", ".pdf", ".doc", ".docx", ".xls",
    ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".csv", ".exe", ".apk",
    ".mp3", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm",
    ".ogg", ".ogv", ".wav", ".flac", ".aac", ".m4a", ".zip", ".rar",
    ".7z", ".tar", ".iso", ".dmg", ".pkg", ".deb", ".rpm", ".msi",
    ".apk", ".bat", ".sh", ".ps1", ".exe", ".dll", ".so", ".dylib"
]

if len(sys.argv) > 1:
    base_url = sys.argv[1]  # Override base URL from command line argument
    if not base_url.startswith("http") or len(base_url.split("/")) < 3:
        print("Invalid URL! Please provide a valid URL!")
        exit(1)

if len(sys.argv) > 2:
    try:
        depth = int(sys.argv[2])  # Override depth from command line argument
    except ValueError:
        print("Invalid depth value!")
        exit(1)
    if depth <= 0:
        print(f"Depth cannot be negative or zero!")
        exit(1)

if len(sys.argv) > 3:
    output_file = sys.argv[3]  # Override output file name from command line argument

if len(sys.argv) > 4:
    debug_mode = sys.argv[4].lower() == "true"  # Override debug mode from command line argument

# Ensure depth is not too large to avoid excessive recursion
if depth > MAX_DEPTH:
    print(f"Depth exceeds maximum allowed!")
    print(f"Using maximum depth of {MAX_DEPTH}.")
    depth = MAX_DEPTH

def extract_html(url : str) -> str:
    """Fetch HTML content from a URL."""
    try:
        return urlopen(url).read().decode("utf-8")
    except HTTPError as e:
        if debug_mode:
            print(f"HTTPError: {e.code} for URL: {url}")
        if e.code == 429:  # Too Many Requests
            time.sleep(60) # Wait a minute before retrying
            return extract_html(url)
        return ""
    except URLError as e:
        if debug_mode:
            print(f"URLError: {e.reason} for URL: {url}")
        return ""
    except Exception as e:
        if debug_mode:
            print(f"Error: {e} for URL: {url}")
        return ""

def extract_links_from_url(url: str) -> list:
    """Extract links from a given URL."""
    html = extract_html(url)
    if not html:
        return []
    return re.findall('href="([^"]+?)(?=[?:"])', html) # Extract href links from HTML content

def prune_links(url: str, links: list) -> list:
    """Prune links to remove duplicates and ensure they are absolute."""
    seen = set()
    pruned_links = []
    domain = "/".join(url.split("/")[:3]) # OMG HIDDEN :3
    for link in links:
        if not link or link.startswith("#"):
            continue
        if not link.startswith("http"):
            link = ("http:" + link) if link.startswith("//") else (domain + ("" if link.startswith("/") else "/") + link)
        if link in seen:
            continue
        seen.add(link)
        if not any(forbidden in link for forbidden in forbidden_content): # Skip forbidden links
            pruned_links.append(link)
    return pruned_links

g = gt.Graph(directed=True)

eweight = g.new_ep("float")
vcolor = g.new_vp("string")
vlink = g.new_vp("string")

origin = g.add_vertex()
vcolor[origin] = "#ff0000"
vlink[origin] = base_url

next_stage_vertices = []
seen = set(base_url)
def add_links_to_graph(current_depth: int = 0, origin_vert: gt.Vertex = origin) -> None:
    if current_depth >= depth:
        return
    
    links = prune_links(vlink[origin_vert], extract_links_from_url(vlink[origin_vert]))
    for link in links:
        if link in seen:
            vertex = g.vertex(vlink.a == link)
            if vertex is None or g.edge(origin_vert, vertex) is not None:
                continue
            e = g.add_edge(origin_vert, vertex)
            eweight[e] = 10.0 / len(links)
            continue;
        seen.add(link)
        if len(link.split("/")) < 3:
            continue
        vertex = g.add_vertex()
        e = g.add_edge(origin_vert, vertex)
        eweight[e] = 10.0 / len(links)
    
        match current_depth:
            case 0:
                vcolor[vertex] = "#00ff00"
            case 1:
                vcolor[vertex] = "#0000ff"
            case 2:
                vcolor[vertex] = "#ffff00"
            case 3:
                vcolor[vertex] = "#ff00ff"
            case 4:
                vcolor[vertex] = "#00ffff"
            case _:
                vcolor[vertex] = "#ffffff"
        vlink[vertex] = link
        next_stage_vertices.append(vertex)
    if not next_stage_vertices:
        return
    with ThreadPoolExecutor() as executor:
        # Submit the next stage of link extraction for each vertex in parallel
        futures = [executor.submit(add_links_to_graph, current_depth + 1, v) for v in next_stage_vertices]
        # Wait for all futures to complete
        for future in futures:
            future.result()
    next_stage_vertices.clear()

# Start the recursive link extraction from the base url
# The block will make sure that if we hit Ctrl+C, the graph will still be drawn
# Unless we hit it twice, in which case it will exit immediately
if __name__ == "__main__":
    start_time = time.time()
    try:
        add_links_to_graph()
    finally:
        gt.graph_draw(g, vertex_fill_color=vcolor, edge_pen_width=eweight, output=output_file, output_size=(1920, 1080))
        print(f"Graph drawn in {time.time() - start_time:.2f} seconds. (Saved as {output_file})")
        print(f"Total vertices: {g.num_vertices()}, Total edges: {g.num_edges()}")
