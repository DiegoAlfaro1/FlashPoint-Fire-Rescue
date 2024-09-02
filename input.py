import matplotlib.pyplot as plt

with open("input.txt", 'r') as file:
    lines = file.readlines()

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

wall_matrix = []
victims = []
fuego= []
puertas=[]
entrada=[]


for line in lines[:6]:
    row = line.strip().split()
    wall_matrix.append(row)

for line in lines[6:9]:
    parts = line.split()
    if len(parts) == 3:
        x, y = int(parts[0]), int(parts[1])
        entity_type = parts[2]
        if entity_type == 'v':
            victims.append(((x, y), True))
        else:
            victims.append(((x, y), False))

for line in lines[9:19]:
    # Split the line into x and y
    parts = line.split()
    if len(parts) == 2:
        x, y = int(parts[0]), int(parts[1])
        fuego.append((x, y))

for line in lines[19:27]:
    parts = line.split()
    if len(parts) == 4:
        x1, y1, x2, y2 = map(int, parts)
        puertas.append(((x1, y1), (x2, y2)))

for line in lines[27:31]:
    parts = line.split()
    if len(parts) == 2:
        x, y = int(parts[0]), int(parts[1])
        entrada.append((x, y))

# print(f"pois: {pois}")
# print(f"wall_matrix: {wall_matrix}")
# print(f"victims: {victims}")
# print(f"fuego: {fuego}")
# print(f"puertas: {puertas}")
# print(f"entrada: {entrada}")

grid_width = 8
grid_height = 6

def generate_grid(grid_width, grid_height, cell_walls,exits):
    grid_dict = {}
    out_of_bounds_dict = {}

    for i in range(grid_height):
        for j in range(grid_width):
            cell_key = (i+1, j+1)
            walls = cell_walls[i][j]
            neighbors = []
            out_of_bounds_neighbor_list = []

            # Check UP
            if i > 0:  # Not the first row
                neighbors.append([(i, j+1), 5 if walls[0] == '1' else 1])
            else:
                out_of_bounds_neighbor = (i, j+1)
                if cell_key in exits:
                    print(f"Cell {cell_key} is connected to out-of-bounds exit at {out_of_bounds_neighbor} (UP)")
                    out_of_bounds_neighbor_list.append([(i, j+1), 2])
                else:
                    out_of_bounds_neighbor_list.append([(i, j+1), 5 if walls[0] == '1' else 1])

            # Check LEFT
            if j > 0:  # Not the first column
                neighbors.append([(i+1, j), 5 if walls[1] == '1' else 1])
            else:
                out_of_bounds_neighbor = (i+1, j)
                if cell_key in exits:
                    print(f"Cell {cell_key} is connected to out-of-bounds exit at {out_of_bounds_neighbor} (UP)")
                    out_of_bounds_neighbor_list.append([(i+1, j), 2])
                else:
                    out_of_bounds_neighbor_list.append([(i, j), 5 if walls[0] == '1' else 1])

            # Check DOWN
            if i < grid_height - 1:  # Not the last row
                neighbors.append([(i+2, j+1), 5 if walls[2] == '1' else 1])
            else:
                out_of_bounds_neighbor = (i+2, j+1)
                if cell_key in exits:
                    print(f"Cell {cell_key} is connected to out-of-bounds exit at {out_of_bounds_neighbor} (DOWN)")
                    out_of_bounds_neighbor_list.append([(i+2, j+1), 2])
                else:
                    out_of_bounds_neighbor_list.append([(i+2, j+1), 5 if walls[0] == '1' else 1])


            # Check RIGHT
            if j < grid_width - 1:  # Not the last column
                neighbors.append([(i+1, j+2), 5 if walls[3] == '1' else 1])
            else:
                out_of_bounds_neighbor = (i+1, j+2)
                if cell_key in exits:
                    print(f"Cell {cell_key} is connected to out-of-bounds exit at {out_of_bounds_neighbor} (RIGHT)")
                    out_of_bounds_neighbor_list.append([(i+1, j+2), 2])
                else:
                    out_of_bounds_neighbor_list.append([(i+1, j+2), 5 if walls[0] == '1' else 1])


            grid_dict[cell_key] = neighbors
            out_of_bounds_dict[cell_key] = out_of_bounds_neighbor_list

    return [grid_dict, out_of_bounds_dict]

def update_walls_to_doors(grid_dict, door_pairs):
    for (cell1, cell2) in door_pairs:
        # Extract coordinates
        x1, y1 = cell1
        x2, y2 = cell2

        # Determine the direction of the wall and update it to a door (value 2)
        if x1 == x2:  # Same row, horizontal wall (left-right)
            if y1 < y2:  # cell1 is to the left of cell2
                update_wall_value(grid_dict, (x1, y1), (x2, y2), 3, 1)  # Right wall of cell1, Left wall of cell2
            else:  # cell1 is to the right of cell2
                update_wall_value(grid_dict, (x2, y2), (x1, y1), 3, 1)  # Right wall of cell2, Left wall of cell1
        elif y1 == y2:  # Same column, vertical wall (up-down)
            if x1 < x2:  # cell1 is above cell2
                update_wall_value(grid_dict, (x1, y1), (x2, y2), 2, 0)  # Bottom wall of cell1, Top wall of cell2
            else:  # cell1 is below cell2
                update_wall_value(grid_dict, (x2, y2), (x1, y1), 2, 0)  # Bottom wall of cell2, Top wall of cell1

def update_wall_value(grid_dict, cell1, cell2, wall_index1, wall_index2):
    # Convert the current wall values from 5 (wall) to 2 (door) between cell1 and cell2
    for i, neighbor in enumerate(grid_dict[cell1]):
        if neighbor[0] == cell2 and neighbor[1] == 5:
            grid_dict[cell1][i][1] = 2
    for i, neighbor in enumerate(grid_dict[cell2]):
        if neighbor[0] == cell1 and neighbor[1] == 5:
            grid_dict[cell2][i][1] = 2

grid_dict,out_of_bounds_dict = generate_grid(grid_width, grid_height, wall_matrix,entrada)

update_walls_to_doors(grid_dict, puertas)

print(f"grid_dict: {grid_dict}")
# print(f"out_of_bounds_dict: {out_of_bounds_dict}")

'''

si una celda tiene una salida entonces que se meta a un diccionario o lista de lista donde salga la coordenada y 
un costo o la direccion donde esta esa salida, eso que lo use el agente para determinar si salir
o que simpleente los agentes sepan que en esa celda hay una salida y que si llevan una victima cargada, prioricen salir

'''


def visualize_grid(grid_width, grid_height, cell_walls):
    fig, ax = plt.subplots(figsize=(grid_width, grid_height))

    # Draw the grid
    for i in range(grid_width + 1):
        ax.plot([i, i], [0, grid_height], color="black")
    for j in range(grid_height + 1):
        ax.plot([0, grid_width], [j, j], color="black")

    # Draw the walls
    for i in range(grid_height):
        for j in range(grid_width):
            walls = cell_walls[i][j]
            x = j
            y = grid_height - 1 - i  # Flip the y-axis for proper visualization

            if walls[0] == '1':  # Top wall
                ax.plot([x, x + 1], [y + 1, y + 1], color="red", linewidth=2)
            if walls[1] == '1':  # Left wall
                ax.plot([x, x], [y, y + 1], color="red", linewidth=2)
            if walls[2] == '1':  # Bottom wall
                ax.plot([x, x + 1], [y, y], color="red", linewidth=2)
            if walls[3] == '1':  # Right wall
                ax.plot([x + 1, x + 1], [y, y + 1], color="red", linewidth=2)

    # Set the limits and aspect ratio
    ax.set_xlim(0, grid_width)
    ax.set_ylim(0, grid_height)
    ax.set_aspect('equal')
    ax.axis('off')  # Turn off the axis

    plt.show()

def visualize_grid_with_doors(grid_width, grid_height, cell_walls, grid_dict):
    fig, ax = plt.subplots(figsize=(grid_width, grid_height))

    # Draw the grid
    for i in range(grid_width + 1):
        ax.plot([i, i], [0, grid_height], color="black")
    for j in range(grid_height + 1):
        ax.plot([0, grid_width], [j, j], color="black")

    # Draw the walls and doors
    for i in range(grid_height):
        for j in range(grid_width):
            walls = cell_walls[i][j]
            x = j
            y = grid_height - 1 - i  # Flip the y-axis for proper visualization

            # Check for walls and doors in grid_dict for each cell
            current_cell = (i+1, j+1)

            for neighbor in grid_dict[current_cell]:
                neighbor_cell, wall_value = neighbor

                # Determine the direction to draw the wall/door
                nx, ny = neighbor_cell
                if nx == current_cell[0]:  # Same row, horizontal wall/door
                    if ny > current_cell[1]:  # Neighbor is to the right
                        if wall_value == 2:
                            color = "blue" 
                        elif wall_value == 5:
                            color = "red"                        
                        else:
                            color = "black"
                        ax.plot([x + 1, x + 1], [y, y + 1], color=color, linewidth=2)
                    else:  # Neighbor is to the left
                        if wall_value == 2:
                            color = "blue" 
                        elif wall_value == 5:
                            color = "red"                        
                        else:
                            color = "black"
                        ax.plot([x, x], [y, y + 1], color=color, linewidth=2)
                elif ny == current_cell[1]:  # Same column, vertical wall/door
                    if nx > current_cell[0]:  # Neighbor is below
                        if wall_value == 2:
                            color = "blue" 
                        elif wall_value == 5:
                            color = "red"                        
                        else:
                            color = "black"
                        ax.plot([x, x + 1], [y, y], color=color, linewidth=2)
                    else:  # Neighbor is above
                        if wall_value == 2:
                            color = "blue" 
                        elif wall_value == 5:
                            color = "red"                        
                        else:
                            color = "black"
                        ax.plot([x, x + 1], [y + 1, y + 1], color=color, linewidth=2)

    # Set the limits and aspect ratio
    ax.set_xlim(0, grid_width)
    ax.set_ylim(0, grid_height)
    ax.set_aspect('equal')
    ax.axis('off')  # Turn off the axis

    plt.show()

# visualize_grid(grid_width, grid_height, wall_matrix)
# visualize_grid_with_doors(grid_width, grid_height, wall_matrix, grid_dict)