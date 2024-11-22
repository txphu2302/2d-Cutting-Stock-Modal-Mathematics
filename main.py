import matplotlib.pyplot as plt
import matplotlib.patches as patches

def stock_cutter(child_rects, parent_rects):
    """
    2D cutting stock problem solver with support for multiple parent rectangles.
    This heuristic method attempts to fit child rectangles into parent rectangles efficiently.

    Parameters:
        child_rects: List of [width, height, demand] for child rectangles.
        parent_rects: List of [width, height, quantity] for parent rectangles.

    Returns:
        placements: List of placements for child rectangles [[x1, y1, x2, y2], ...].
        sizes: List of sizes [width, height] for each placed rectangle.
        placement_parents: List of parent indices for each placement.
        expanded_parents: List of expanded parent rectangles [width, height].
        used_spaces_per_parent: Used spaces for each parent rectangle.
    """
    # Expand child rectangles based on demand
    expanded_rects = []
    for rect in child_rects:
        width, height, demand = rect
        expanded_rects.extend([[width, height]] * demand)

    # Sort rectangles by area (descending) for better packing
    expanded_rects = sorted(expanded_rects, key=lambda x: x[0] * x[1], reverse=True)

    # Expand parent rectangles based on quantity
    expanded_parents = []
    for rect in parent_rects:
        width, height, quantity = rect
        expanded_parents.extend([[width, height]] * quantity)

    # List to store used spaces for each parent rectangle
    used_spaces_per_parent = [[] for _ in expanded_parents]

    # Track demand for each rectangle
    remaining_demand = {}
    for rect in child_rects:
        width, height, demand = rect
        remaining_demand[(width, height)] = demand
        if width != height:
            remaining_demand[(height, width)] = remaining_demand.get((height, width), 0) + demand

    # Fit rectangles into parent rectangles
    placements = []
    sizes = []
    placement_parents = []

    for rect in expanded_rects:
        rect_width, rect_height = rect
        placed = False

        for parent_idx, (parent_width, parent_height) in enumerate(expanded_parents):
            used_spaces = used_spaces_per_parent[parent_idx]
            for width, height in [(rect_width, rect_height), (rect_height, rect_width)]:
                if width > parent_width or height > parent_height:
                    continue
                for x in range(parent_width - width + 1):
                    for y in range(parent_height - height + 1):
                        if not any(
                            x < used_x2 and x + width > used_x1 and y < used_y2 and y + height > used_y1
                            for used_x1, used_y1, used_x2, used_y2 in used_spaces
                        ):
                            # Place rectangle
                            placements.append([x, y, x + width, y + height])
                            sizes.append([width, height])
                            placement_parents.append(parent_idx)
                            used_spaces.append([x, y, x + width, y + height])
                            placed = True
                            # Update demand
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
        if not placed:
            print(f"Cannot place rectangle of size {rect_width}x{rect_height}")
            continue

    return placements, sizes, placement_parents, expanded_parents, used_spaces_per_parent


def draw_multiple_parent_rects(placements, sizes, expanded_parents, placement_parents, used_spaces_per_parent):
    """
    Visualize the placements of rectangles in multiple parent rectangles.

    Parameters:
        placements: List of [x1, y1, x2, y2] for placed rectangles.
        sizes: List of [width, height] for each placed rectangle.
        expanded_parents: List of [width, height] for each parent rectangle.
        placement_parents: List of indices indicating which parent rectangle each placement is in.
        used_spaces_per_parent: List containing used spaces for each parent.
    """
    parent_count = len(expanded_parents)
    fig, axes = plt.subplots(1, parent_count, figsize=(10 * parent_count, 5))

    if parent_count == 1:
        axes = [axes]

    for i in range(parent_count):
        parent_width, parent_height = expanded_parents[i]
        ax = axes[i]
        ax.set_xlim(0, parent_width)
        ax.set_ylim(0, parent_height)
        ax.set_aspect('equal')
        ax.invert_yaxis()

        # Draw parent rectangle
        parent = patches.Rectangle((0, 0), parent_width, parent_height, linewidth=1, edgecolor='black', facecolor='none')
        ax.add_patch(parent)

        # Assign unique colors to sizes
        unique_sizes = list(set(tuple(size) for size in sizes))
        colors = plt.cm.get_cmap("tab10", len(unique_sizes))
        size_to_color = {size: colors(idx % 10) for idx, size in enumerate(unique_sizes)}

        # Draw child rectangles
        for idx, (placement, size, parent_idx) in enumerate(zip(placements, sizes, placement_parents)):
            if parent_idx == i:
                x1, y1, x2, y2 = placement
                color = size_to_color[tuple(size)]
                rect = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=1, edgecolor='black', facecolor=color, alpha=0.7)
                ax.add_patch(rect)

        # Add legend
        legend_patches = [patches.Patch(color=size_to_color[size], label=f"{size[0]}x{size[1]}") for size in unique_sizes]
        ax.legend(handles=legend_patches, loc='upper right')

    plt.tight_layout()
    return fig