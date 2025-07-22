# Link Grapher
Link Grapher is a python application that allows to input a webpage, and see al he places it links to, and where those paces link to, with a visual represenation of these links in the form of a graph.

This program was made for the Summer of Making 2025, organized by Hack Club.

# Usage
To use link grapher, you'll need to have the latest version of pyhon installed in your machine, as well as the graph-tool library.

To use the program, simply run the following command in your terminal:

```python main.py <url> <depth> <output_file> <debug_mode>```

Where `<url>` is the url of the webpage you want to analyze, `<depth>` is the depth of the links you want to follow, <output_file> is the name of the file to outpu to, and `<debug_mode>` is "true" when you want to run the program in Debug Mode. For example, if you want to follow links up to a depth of 2 from "https://example.com", without debug mode enabled, you would run:

```python main.py https://example.com 2```

The program takes a bit to run, and runtime pretty much grows factorially with the depth, so be careful with the depth you choose. The default max depth the program will let you put in is 5, which will usuay take a few hours at the very least, so be careful with that.

If you have debug mode enabled, you might see a lot of 429 errors. Don't worry, the program will handle them "properly".

# How it works
The program works by fetching the HTML content of the webpage, and filtering out any http(s):// links that are not in the same domain as the origina, and are proper webpages, and not just files or images. It then follows those links, and repeats the process, only stopping once the desired depth is finally reached.

To make the program slightly faster, the process is parallelized, so that each link runs as a separate thread, that terminates once it reached the desired depth. This way, we can get pretty big graphs in a "reasonable" amount of time, at least when compared to the time it would take to do it in a more canonical manner.

# Why
This program was just made as a fun litte experiment for Summer of Making 2025. Nothing special on it, to be honest. Just a fun little siy side project to learn and get some other ideas rolling.
