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

print("Direct Links:")
print(direct_links)
print("\nSame Page Links:")
print(same_page_links)

g = gt.Graph(directed=True)  # Create a directed graph 

origin = g.add_vertex()  # Add an origin vertex

for link in direct_links + same_page_links:
    v = g.add_vertex()  # Add each link as a vertex in the graph 
    g.add_edge(origin, v)

gt.graph_draw(g, vertex_text=g.vertex_index, output="output.svg")
