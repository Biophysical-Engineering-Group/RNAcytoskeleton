import cv2
import numpy as np
import pandas as pd
from skimage.morphology import skeletonize, thin, binary_erosion
from skimage.util import img_as_ubyte
import networkx as nx
import matplotlib.pyplot as plt
import os

import matplotlib.patches as mpatches

# Global list to store selected path indices
selected_paths = []

def onclick(event, paths, colors, ax, fig):
    """
    Event handler for mouse clicks on the plot. Selects/deselects paths.
    """
    global selected_paths
    
    if event.inaxes == ax:
        for idx, path in enumerate(paths):
            # Check if click is near any point in the path (within a small radius)
            for (y, x) in path:
                if abs(event.xdata - x) < 5 and abs(event.ydata - y) < 5:
                    if idx+1 in selected_paths:
                        selected_paths.remove(idx+1)
                    else:
                        selected_paths.append(idx+1)
                    
                    # Update the title with selected paths
                    ax.set_title(f'Selected Paths: {selected_paths}')
                    fig.canvas.draw()
                    return

# Create a graph from the image
def image_to_graph(binary_image):
    rows, cols = binary_image.shape
    G = nx.Graph()

    for i in range(rows):
        for j in range(cols):
            if binary_image[i, j]:  # If the pixel is white (1)
                G.add_node((i, j))

                # Check adjacent pixels and add edges
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols and binary_image[ni, nj]:
                        G.add_edge((i, j), (ni, nj))

    return G

# Find the longest path in a connected component
def longest_path_in_component(G, component):
    subgraph = G.subgraph(component)
    # Find terminal nodes using DFS
    start_node = next(iter(subgraph.nodes))
    # First DFS to find the farthest node from the start node
    farthest_node, _ = nx.single_source_dijkstra(subgraph, start_node)
    # Second DFS from the farthest node found
    farthest_node = max(farthest_node, key=farthest_node.get)  # Farthest node from the start node
    distances, path = nx.single_source_dijkstra(subgraph, farthest_node)
    # Find the longest path
    farthest_node = max(distances, key=distances.get)
    return path[farthest_node]

# Find the top 10 longest paths in the entire graph
def find_top_n_longest_paths(G, n=5):
    paths = []
    # Find connected components
    components = nx.connected_components(G)
    for component in components:
        # Find the longest path in this component
        path = longest_path_in_component(G, component)
        paths.append(path)
    # Sort paths by length in descending order and return the top n
    paths = sorted(paths, key=len, reverse=True)[:n]
    return paths

def overlay_paths_on_image(image, paths, alpha=0.5, thicken_line=1):
    # Create an RGB image from the grayscale image
    color_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Generate a list of distinct colors using a colormap
    colormap = plt.get_cmap('tab10')
    colors = [colormap(i)[:3] for i in range(len(paths))]

    # Overlay each path with a different color
    for idx, path in enumerate(paths):
        color = tuple([int(c * 255) for c in colors[idx]])  # Convert to 8-bit color
        for y, x in path:
            for dy in range(-thicken_line, thicken_line+1):
                for dx in range(-thicken_line, thicken_line+1):
                    if 0 <= y+dy < image.shape[0] and 0 <= x+dx < image.shape[1]:
                        color_image[y+dy, x+dx] = color

    # Blend the colored paths with the original grayscale image
    overlay = cv2.addWeighted(color_image, alpha, cv2.cvtColor(image, cv2.COLOR_GRAY2BGR), 1 - alpha, 0)
    return overlay, colors

def save_path_to_csv(paths, directory, base_name, selected_paths):
    """
    Save each path's coordinates (X, Y) to a separate CSV file.
    """
    for i, path in enumerate(paths):
        if i+1 not in selected_paths:
            continue
        # Create a DataFrame for the coordinates of the path
        coordinates = pd.DataFrame(path, columns=['Y', 'X'])  # Y, X because of how image indexing works
        
        # Define the file name for the path
        csv_file = os.path.join(directory, f"{base_name}_path_{i+1}.csv")
        
        # Save the path coordinates to a CSV file
        coordinates.to_csv(csv_file, index=False)
        print(f"Path {i+1} saved to {csv_file}")

def process_image(filepath, save_folder, n_filament_choice = 5):
    """
    Process the image, remove branches from skeleton, and save the output.
    """
    global selected_paths
    selected_paths = []  # Reset selection for each image
    
    # Load the image in grayscale mode
    img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    
    blur_kernel = (3, 3)
    thicken_line = 1
    if '0.5x' in filepath:
        blur_kernel = (11, 11)
        thicken_line = 2
    elif '0.25x' in filepath:
        blur_kernel = (27, 27)
        thicken_line = 3
    blurred_img = cv2.GaussianBlur(img, blur_kernel, 0)
    
    # Initial threshold for binary conversion
    threshold_value = 5
    
    # Apply threshold
    _, binary_img = cv2.threshold(blurred_img, threshold_value, 255, cv2.THRESH_BINARY)

    eroded = binary_erosion(binary_img)
    
    # Skeletonize the binary image
    skeleton = skeletonize(eroded > 0)
    skeleton = thin(skeleton)
    G = image_to_graph(skeleton)
    top_paths = find_top_n_longest_paths(G, n=n_filament_choice)

    selected_paths = [i for i in range(1, len(top_paths)+1)]
    
    # Overlay the paths on the original image with different colors
    overlay_image, colors = overlay_paths_on_image(img, top_paths, alpha=0.8, thicken_line=thicken_line)

    # Display the overlaid image with a legend and interactive clicks
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(overlay_image)
    ax.axis('off')

    # Add legend for each path
    for idx, color in enumerate(colors):
        plt.plot([], [], color=color, label=f'Path {idx+1}')
    
    # Add legend with patches for color labels
    handles = [mpatches.Patch(color=color, label=f'Path {i+1}') for i, color in enumerate(colors)]
    ax.legend(handles=handles, loc='center left', bbox_to_anchor=(1, 0.5))

    ax.set_title('All Path selected, click on a path to deselect it')

    # Connect the click event handler
    cid = fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, top_paths, colors, ax, fig))
    
    # Show the plot and wait for user to select paths
    plt.show()

    # Disconnect the event after the selection is done
    fig.canvas.mpl_disconnect(cid)

    # Save the selected paths after user closes the plot
    if selected_paths:
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        # directory = os.path.dirname(save_folder)
        directory = save_folder

        # Convert selected paths to mask
        keep_paths_mask = np.zeros_like(img)
        for idx in selected_paths:
            if 1 <= idx <= len(top_paths):
                for y, x in top_paths[idx-1]:
                    keep_paths_mask[y, x] = 255
        
        # Save the selected paths as an image
        selected_paths_png = os.path.join(directory, f"{base_name}_selected_paths.png")
        cv2.imwrite(selected_paths_png, keep_paths_mask)
        print(f"Selected paths saved to {selected_paths_png}")

        # Save the selected paths to CSV
        save_path_to_csv(top_paths, directory, base_name, selected_paths=selected_paths)
    else:
        print("No paths were selected.")

if __name__ == "__main__": 
    # collect images in the run folder in dsOV/iSpi folders
    for fold in os.listdir():
        if not os.path.isdir(fold) or 'analysis' in fold:
            continue
        for run in os.listdir(fold):
            if not os.path.isdir(fold + "_analysis"):
                os.mkdir(fold + "_analysis")
            if not os.path.isdir(fold + "/" + run):
                continue
            for file in os.listdir(f"{fold}/{run}"):
                if not os.path.isdir(fold + "_analysis" + "/" + run):
                    os.mkdir(fold + "_analysis" + "/" + run)
                if file.endswith(".tiff") or file.endswith(".tif"):
                    print(f"Processing {fold}/{run}/{file}")
                    process_image(f"{fold}/{run}/{file}", save_folder= fold + "_analysis" + "/" + run + "/", n_filament_choice = 20)
