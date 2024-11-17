import matplotlib.pyplot as plt
import matplotlib.patches as patches

def stock_cutter(child_rects, parent_rect):
    """
    2D cutting stock problem solver with demand support (heuristic method).
    The algorithm now prioritizes filling the parent rectangle as much as possible
    before moving on to the next parent rectangle.

    Parameters:
        child_rects: List of [width, height, demand] for child rectangles.
        parent_rect: [width, height] of the parent rectangle.

    Returns:
        List of placements for child rectangles [[x1, y1, x2, y2], ...] and their sizes.
        The number of parent rectangles used.
    """
    # Expanded rectangles based on demand
    expanded_rects = []
    for rect in child_rects:
        width, height, demand = rect
        expanded_rects.extend([[width, height]] * demand)

    # Sort rectangles by area (descending) for better packing
    expanded_rects = sorted(expanded_rects, key=lambda x: x[0] * x[1], reverse=True)

    # List to store used spaces for each parent rectangle
    used_spaces_per_parent = [[]]

    # Store demand for each child (rectangles with their demand still pending)
    remaining_demand = {}
    for rect in child_rects:
        width, height, demand = rect
        remaining_demand[tuple([width, height])] = demand
        if width != height:  # Add rotated version as well
            remaining_demand[tuple([height, width])] = remaining_demand.get(tuple([height, width]), 0) + demand

    # Try to fit as many rectangles as possible in the parent
    placements = []
    sizes = []
    parent_count = 1

    for rect in expanded_rects:
        rect_width, rect_height = rect
        placed = False

        for parent in range(parent_count):
            for width, height in [(rect_width, rect_height), (rect_height, rect_width)]:
                for x in range(parent_rect[0] - width + 1):
                    for y in range(parent_rect[1] - height + 1):
                        if not any(
                            x < used_x2 and x + width > used_x1 and y < used_y2 and y + height > used_y1
                            for used_x1, used_y1, used_x2, used_y2 in used_spaces_per_parent[parent]
                        ):
                            placements.append([x, y, x + width, y + height])
                            sizes.append([width, height])
                            used_spaces_per_parent[parent].append([x, y, x + width, y + height])  # Mark space as used
                            placed = True
                            if (width, height) in remaining_demand:
                                remaining_demand[(width, height)] -= 1
                                if remaining_demand[(width, height)] == 0:
                                    del remaining_demand[(width, height)]
                            elif (height, width) in remaining_demand:
                                remaining_demand[(height, width)] -= 1
                                if remaining_demand[(height, width)] == 0:
                                    del remaining_demand[(height, width)]
                            break
                    if placed:
                        break
                if placed:
                    break
            if placed:
                break

        if not placed:
            parent_count += 1
            used_spaces_per_parent.append([])  # Create new space list for the new parent
            for width, height in [(rect_width, rect_height), (rect_height, rect_width)]:
                for x in range(parent_rect[0] - width + 1):
                    for y in range(parent_rect[1] - height + 1):
                        if not any(
                            x < used_x2 and x + width > used_x1 and y < used_y2 and y + height > used_y1
                            for used_x1, used_y1, used_x2, used_y2 in used_spaces_per_parent[-1]
                        ):
                            placements.append([x, y, x + width, y + height])
                            sizes.append([width, height])
                            used_spaces_per_parent[-1].append([x, y, x + width, y + height])  # Mark space as used
                            placed = True
                            if (width, height) in remaining_demand:
                                remaining_demand[(width, height)] -= 1
                                if remaining_demand[(width, height)] == 0:
                                    del remaining_demand[(width, height)]
                            elif (height, width) in remaining_demand:
                                remaining_demand[(height, width)] -= 1
                                if remaining_demand[(height, width)] == 0:
                                    del remaining_demand[(height, width)]
                            break
                    if placed:
                        break
                if placed:
                    break

    return placements, sizes, parent_count, used_spaces_per_parent

def draw_multiple_parent_rects(placements, sizes, parent_rect, parent_count, used_spaces_per_parent):
    """
    Visualize the placements of rectangles in multiple parent rectangles.

    Parameters:
        placements: List of [x1, y1, x2, y2] for placed rectangles.
        sizes: List of [width, height] for each placed rectangle.
        parent_rect: [width, height] of the parent rectangle.
        parent_count: Total number of parent rectangles used.
        used_spaces_per_parent: List containing used spaces for each parent.
    """
    parent_width, parent_height = parent_rect
    fig, axes = plt.subplots(1, parent_count, figsize=(10 * parent_count, 5))

    if parent_count == 1:
        axes = [axes]

    for i in range(parent_count):
        ax = axes[i]
        ax.set_xlim(0, parent_width)
        ax.set_ylim(0, parent_height)
        ax.set_aspect('equal')
        ax.invert_yaxis()  # Invert y-axis for better visualization

        # Draw parent rectangle
        parent = patches.Rectangle((0, 0), parent_width, parent_height, linewidth=1, edgecolor='black', facecolor='none')
        ax.add_patch(parent)

        # Assign a unique color to each unique size
        unique_sizes = list(set(tuple(size) for size in sizes))
        colors = plt.cm.get_cmap("tab10", len(unique_sizes))
        size_to_color = {size: colors(idx) for idx, size in enumerate(unique_sizes)}

        # Draw child rectangles
        for idx, (placement, size) in enumerate(zip(placements, sizes)):
            if placement in used_spaces_per_parent[i]:
                x1, y1, x2, y2 = placement
                width, height = size
                color = size_to_color[tuple(size)]
                rect = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=1, edgecolor='black', facecolor=color, alpha=0.7)
                ax.add_patch(rect)

        # Add legend for unique sizes
        legend_patches = [patches.Patch(color=size_to_color[size], label=f"{size[0]}x{size[1]}") for size in unique_sizes]
        ax.legend(handles=legend_patches, loc='upper right')

    # Return the figure for saving or embedding
    return fig


# Define child_rects once
child_rects = [
    [2, 1, 5],  # Width, Height, Demand
    [4, 2, 5],
    [5, 3, 2],
    [7, 4, 3],
    [8, 5, 2],
]

# Testing
if __name__ == '__main__':
    parent_rect = [13, 10]  # Width x Height

    placements, sizes, parent_count, used_spaces_per_parent = stock_cutter(child_rects, parent_rect)
    print("Placements:", placements)
    draw_multiple_parent_rects(placements, sizes, parent_rect, parent_count, used_spaces_per_parent)