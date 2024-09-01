import random
from typing import List, Tuple, Dict, Set
from mesa import Model, Agent
from mesa.space import MultiGrid, SingleGrid
from mesa.time import RandomActivation
import matplotlib.pyplot as plt

#problema con la generacion de celdas, parece que esta interpretando erroneamente las entradas

class FirefighterAgent(Agent):
    def __init__(self, unique_id: int, model: 'FlashPointModel'):
        super().__init__(unique_id, model)
        self.position: Tuple[int, int] = (0, 0)
        self.ap = 4
        self.saved_ap = 0
        self.max_ap = 8
        self.carrying_victim = False

    def get_position(self) -> Tuple[int, int]:
        return self.position

    def get_ap(self) -> int:
        return self.ap

    def is_carrying_victim(self) -> bool:
        return self.carrying_victim

    def move(self, new_pos: Tuple[int, int]) -> bool:
        if not self.is_valid_position(new_pos):
            return False

        # Check if the target cell is empty
        if not self.model.grid.is_cell_empty(new_pos):
            return False

        ap_cost = 2 if new_pos in self.model.fire else 1
        if self.carrying_victim:
            ap_cost = 2
            if new_pos in self.model.fire:
                return False

        if self.ap >= ap_cost:
            self.ap -= ap_cost
            self.model.grid.move_agent(self, new_pos)
            self.position = new_pos
            
            if new_pos in self.model.pois and not self.model.pois[new_pos]["revealed"]:
                self.reveal_poi(new_pos)
            
            if self.carrying_victim and new_pos in self.model.exits:
                self.rescue_victim()

            return True
        return False

    def reveal_poi(self, pos: Tuple[int, int]) -> None:
        is_victim = self.model.reveal_poi(pos)
        if is_victim and not self.carrying_victim:
            self.carrying_victim = True
            # print(f"Firefighter {self.unique_id} is now carrying a victim.")

    def rescue_victim(self) -> None:
        self.model.rescued_victims += 1
        self.carrying_victim = False
        # print(f"Victim rescued by Firefighter {self.unique_id}! Total rescued: {self.model.rescued_victims}")

    def open_close_door(self) -> bool:
        for door in self.model.doors:
            if self.position in (door.cell1, door.cell2):
                if self.ap >= 1:
                    self.ap -= 1
                    door.toggle()
                    return True
        return False

    def extinguish(self, target_pos: Tuple[int, int]) -> bool:
        if target_pos in self.model.fire and self.ap >= 2:
            self.ap -= 2
            self.model.fire.remove(target_pos)
            return True
        elif target_pos in self.model.smoke and self.ap >= 1:
            self.ap -= 1
            self.model.smoke.remove(target_pos)
            return True
        return False

    def chop(self) -> bool:
        for wall in self.model.walls:
            if self.position in (wall.cell1, wall.cell2):
                if self.ap >= 2:
                    self.ap -= 2
                    wall.damage_wall()
                    self.model.damage_markers += 1
                    return True
        return False

    def step(self) -> None:
        self.ap += self.saved_ap
        self.saved_ap = 0

        # Strategy actions in order of priority
        if self.carrying_victim and self.move_action():
            return

        if self.extinguish_action():
            return

        if self.reveal_poi_action():
            return

        if self.random_move():
            return

        # Save remaining AP for the next step
        self.saved_ap = min(self.ap, 4)
        self.ap = 0

    def move_action(self) -> bool:
        if self.carrying_victim:
            # Select a movement direction towards an exit or simply move
            for exit_pos in self.model.exits:
                dx = exit_pos[0] - self.position[0]
                dy = exit_pos[1] - self.position[1]
                new_pos = (
                    self.position[0] + (1 if dx > 0 else -1 if dx < 0 else 0),
                    self.position[1] + (1 if dy > 0 else -1 if dy < 0 else 0)
                )
                if self.is_valid_position(new_pos):
                    return self.move(new_pos)
        
        return False

    def reveal_poi_action(self) -> bool:
        adjacent_cells = self.model.grid.get_neighborhood(self.position, moore=False, include_center=True)
        for cell in adjacent_cells:
            if cell in self.model.pois and not self.model.pois[cell]["revealed"]:
                # Check if the cell is empty before moving
                if self.model.grid.is_cell_empty(cell):
                    if self.move(cell):
                        return True
        return False

    def random_move(self) -> bool:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            new_pos = (self.position[0] + dx, self.position[1] + dy)
            if self.is_valid_position(new_pos) and self.model.grid.is_cell_empty(new_pos):
                return self.move(new_pos)
        return False

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        return 0 <= pos[0] < self.model.grid.width and 0 <= pos[1] < self.model.grid.height

    def extinguish_action(self) -> bool:
        adjacent_cells = self.model.grid.get_neighborhood(self.position, moore=False, include_center=True)
        for cell in adjacent_cells:
            if cell in self.model.fire or cell in self.model.smoke:
                return self.extinguish(cell)
        return False

class FlashPointModel(Model):

    '''Setup and initialization'''
    def __init__(self, width: int, height: int, wall_matrix,victims,fire, doors: List[Tuple[Tuple[int, int], Tuple[int, int]]],exits,n_agents: int = 6,):
        self.grid = SingleGrid(height+1,width+1, torus=False)
        self.schedule = RandomActivation(self)
        self.doors = set(doors) if doors else set()
        self.damage_markers = 0
        self.rescued_victims = 0
        self.lost_victims = 0
        self.victims = [True,True,True,True,True,True,True,True,True,True,False,False,False,False]
        self.max_pois_onBoard = 3
        self.running = True
        self.building_cells = frozenset((x, y) for x in range(1, width + 1) for y in range(1, height + 1))
        self.n_agents = n_agents
        self.ff_ids=[]


        self.exits = exits
        self.fire: Set[Tuple[int, int]] = set()
        self.smoke: Set[Tuple[int, int]] = set()
        self.pois: Dict[Tuple[int, int], Dict[str, bool]] = {}
        self.poi_count = 0

        self.grid_structure = {}
        self.wall_health = {}
        self.initial_victims = victims
        self.initial_fire = fire
        self.width = width
        self.height = height

        self.agents = []

        self.setup_board(wall_matrix, victims, fire)

    '''Setup and initialization'''

    def setup_board(self, wall_matrix: List[str],victims,fire) -> None:

        self.grid_structure = self.generate_grid(self.width, self.height, wall_matrix)
        
        for pos, connections in self.grid_structure.items():
            for adj, cost in connections:
                if cost == 5:  # If it's a wall
                    self.wall_health[(pos, adj)] = 2

        # Process the doors
        self.update_walls_to_doors(self.grid_structure, self.doors)

        for i in range(len(fire)):
            self.fire.add(fire[i])

        for i in range(self.n_agents):
            firefighter = FirefighterAgent(i, self)
            self.schedule.add(firefighter)
            while True:
                x, y = self.random.randrange(1, self.grid.width), self.random.randrange(self.grid.height)
                if self.grid.is_cell_empty((x, y)) and (x, y) not in self.fire and (x, y) not in self.pois:
                    break

            self.grid.place_agent(firefighter, (x, y))
            firefighter.position = (x, y)
            self.agents.append(firefighter)

        for i in range(len(victims)):
            self.add_initial_victimas(victims)



        #falta poner donde van a estar las entradas

    def process_cell(self, x: int, y: int, cell: str) -> None:
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # up, left, down, right
        for i, direction in enumerate(directions):
            new_x, new_y = x + direction[0], y + direction[1]
            if 1 <= new_x < self.width and 1 <= new_y < self.height:
                if cell[i] == '0':
                    self.grid_structure[(x, y)].append(((new_x, new_y), 1))
                else:
                    # Set walls with cost 5
                    self.grid_structure[(x, y)].append(((new_x, new_y), 5))
                    # Initialize wall health
                    self.wall_health[((x, y), (new_x, new_y))] = 2

    def update_grid_for_door(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> None:
        if cell1 not in self.grid_structure or cell2 not in self.grid_structure:
            print(f"Warning: Door between {cell1} and {cell2} is outside the grid. Skipping.")
            return

        # Update the grid structure to reflect a door (cost 2) between cell1 and cell2
        self.grid_structure[cell1] = [((x, y), 2 if (x, y) == cell2 else c) for ((x, y), c) in self.grid_structure[cell1]]
        self.grid_structure[cell2] = [((x, y), 2 if (x, y) == cell1 else c) for ((x, y), c) in self.grid_structure[cell2]]

        # Ensure the door is in self.doors
        door = (cell1, cell2)
        reverse_door = (cell2, cell1)
        if door not in self.doors and reverse_door not in self.doors:
            self.doors.add(door)

    '''victims and false alarms'''

    def add_initial_victimas(self, victims) -> None:
        for v in victims:
            self.pois[v[0]] = {"is_victim": v[1], "revealed": False}

    def add_victim(self, pos: Tuple[int, int]) -> None:
        is_victim = self.victims.pop()
        self.pois[pos] = {"is_victim": is_victim, "revealed": False}
        self.remove_fire_and_smoke(pos) 

    def check_firefighters_and_victims(self,actual_step) -> None:
        print("Checking firefighters and victims")
        agents_to_remove = []
        flag = True

        # Collect agents to remove
        for agent in self.agents:
            if isinstance(agent, FirefighterAgent) and agent.position in self.fire:
                self.ff_ids.append(agent.unique_id)
                print(f"Firefighter in fire in {agent.position}")
                print(self.ff_ids)
                agents_to_remove.append(agent)

        # Remove agents outside the loop
        for agent in agents_to_remove:
            self.grid.remove_agent(agent)
            self.schedule.remove(agent)
            self.agents.remove(agent)

        # Check if less than 6 firefighter agents exist
        num_firefighters = len([agent for agent in self.agents if isinstance(agent, FirefighterAgent)])

        # Add new agents if conditions are met
        attempt_counter = 0
        while flag and num_firefighters < 6:
            x, y = random.randint(1, 6), random.randint(1, 8)
            attempt_counter += 1

            if self.grid.is_cell_empty((x, y)) and (x, y) not in self.fire and (x, y) not in self.pois:
                if actual_step % 2 == 0 and self.ff_ids:
                    new_id = self.ff_ids.pop()
                    new_agent = FirefighterAgent(new_id, self)
                    self.schedule.add(new_agent)
                    self.grid.place_agent(new_agent, (x, y))
                    self.agents.append(new_agent)
                    num_firefighters += 1
                    print(f"New firefighter added at {x}, {y}")
                    print(self.ff_ids)
                flag = False
            
            # Break the loop after 20 attempts
            if attempt_counter >= 20:
                print("Unable to place a new firefighter after 20 attempts.")
                break

        
        for pos in list(self.pois.keys()):
            if pos in self.fire:
                self.lose_victim(pos)

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        return 0 <= pos[0] < self.grid.width and 0 <= pos[1] < self.grid.height

    def is_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    def lose_victim(self, pos: Tuple[int, int]) -> None:
        if pos in self.pois:
            if self.pois[pos]["is_victim"] and not self.pois[pos]["revealed"]:
                self.lost_victims += 1
            del self.pois[pos]

    '''walls and doors'''

    # nueva generacion de grid y actualizacion de paredes a puertas

    def generate_grid(self,grid_width, grid_height, cell_walls):
        grid_dict = {}

        for i in range(grid_height):
            for j in range(grid_width):
                cell_key = (i+1, j+1)
                walls = cell_walls[i][j]
                neighbors = []

                # Check UP
                if i > 0:  # Not the first row
                    neighbors.append([(i, j+1), 5 if walls[0] == '1' else 1])
                
                # Check LEFT
                if j > 0:  # Not the first column
                    neighbors.append([(i+1, j), 5 if walls[1] == '1' else 1])
                
                # Check DOWN
                if i < grid_height - 1:  # Not the last row
                    neighbors.append([(i+2, j+1), 5 if walls[2] == '1' else 1])
                
                # Check RIGHT
                if j < grid_width - 1:  # Not the last column
                    neighbors.append([(i+1, j+2), 5 if walls[3] == '1' else 1])

                grid_dict[cell_key] = neighbors

        return grid_dict

    def update_walls_to_doors(self,grid_dict, door_pairs):
        for (cell1, cell2) in door_pairs:
            # Extract coordinates
            x1, y1 = cell1
            x2, y2 = cell2

            # Determine the direction of the wall and update it to a door (value 2)
            if x1 == x2:  # Same row, horizontal wall (left-right)
                if y1 < y2:  # cell1 is to the left of cell2
                    self.update_wall_value(grid_dict, (x1, y1), (x2, y2), 3, 1)  # Right wall of cell1, Left wall of cell2
                else:  # cell1 is to the right of cell2
                    self.update_wall_value(grid_dict, (x2, y2), (x1, y1), 3, 1)  # Right wall of cell2, Left wall of cell1
            elif y1 == y2:  # Same column, vertical wall (up-down)
                if x1 < x2:  # cell1 is above cell2
                    self.update_wall_value(grid_dict, (x1, y1), (x2, y2), 2, 0)  # Bottom wall of cell1, Top wall of cell2
                else:  # cell1 is below cell2
                    self.update_wall_value(grid_dict, (x2, y2), (x1, y1), 2, 0)  # Bottom wall of cell2, Top wall of cell1

    def update_wall_value(self,grid_dict, cell1, cell2, wall_index1, wall_index2):
        # Convert the current wall values from 5 (wall) to 2 (door) between cell1 and cell2
        for i, neighbor in enumerate(grid_dict[cell1]):
            if neighbor[0] == cell2 and neighbor[1] == 5:
                grid_dict[cell1][i][1] = 2
        for i, neighbor in enumerate(grid_dict[cell2]):
            if neighbor[0] == cell1 and neighbor[1] == 5:
                grid_dict[cell2][i][1] = 2


    def wall_in_direction(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> bool:
        if pos not in self.grid_structure:
            print(f"Warning: Wall Position {pos} not found in grid_structure")
            return False

        return any(adj == new_pos and cost == 5 for adj, cost in self.grid_structure[pos])

    def door_in_direction(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> bool:
        if pos not in self.grid_structure:
            print(f"Warning: Door Position {pos} not found in grid_structure")
            return False

        return any(adj == new_pos and cost == 2 for adj, cost in self.grid_structure[pos])

    def damage_wall(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> None:
        if self.wall_in_direction(pos, new_pos):
            wall_key = (pos, new_pos) if (pos, new_pos) in self.wall_health else (new_pos, pos)
            self.wall_health[wall_key] -= 1
            self.damage_markers += 1
            
            if self.wall_health[wall_key] == 0:
                # Wall is destroyed, update to open path
                self.update_connection_cost(pos, new_pos, 1)
                self.update_connection_cost(new_pos, pos, 1)
                del self.wall_health[wall_key]
                print(f"Wall between {pos} and {new_pos} has been destroyed.")
            # else:
            #     print(f"Wall between {pos} and {new_pos} has been damaged. Health: {self.wall_health[wall_key]}")
        else:
            print(f"No wall found between {pos} and {new_pos}")

    def damage_door(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> None:
        if self.door_in_direction(pos, new_pos):
            # Update the door to be an open path (cost 1)
            self.update_connection_cost(pos, new_pos, 1)
            self.update_connection_cost(new_pos, pos, 1)
        else:
            print(f"No door found between {pos} and {new_pos}")

    def update_connection_cost(self, pos: Tuple[int, int], neighbor: Tuple[int, int], new_cost: int) -> None:
        for i, (adj, cost) in enumerate(self.grid_structure[pos]):
            if adj == neighbor:
                self.grid_structure[pos][i] = (adj, new_cost)
                break

    '''Rerrolling, steps, and checking game over'''

    def check_game_over(self) -> None:
        if self.damage_markers == 24:
            print("Game Over: Building has collapsed!")
            self.running = False
        elif self.lost_victims == 4:
            print("Game Over: Too many victims lost!")
            self.running = False
        elif self.rescued_victims == 7:
            print("Game Over: All victims accounted for!")
            self.running = False
        elif len(self.agents) == 0:
            print("Game Over: No more firefighters left!")
            self.running = False

    def step(self,actual_step) -> None:
        print("\nStarting new step")
        
        if self.running:
            self.advance_fire()
            self.check_firefighters_and_victims(actual_step)
            self.reroll_pois()
            self.schedule.step()
            self.check_game_over()
        else:
            return
        
        print("Step completed")
        print(f"Game state: {self.get_game_state()}")

    def advance_fire(self) -> None:
        fire_roll = (random.randint(1, 6), random.randint(1, 8))
        self.place_smoke(fire_roll)
        self.handle_flashover()

    def reroll_pois(self) -> None:     
        revealed_pois = sum(1 for poi in self.pois.values() if poi["revealed"])
        
        # Add new POIs if necessary
        while len(self.pois) < self.max_pois_onBoard:
            poi_roll = (random.randint(1, 6), random.randint(1, 8))
            poi_pos = poi_roll
            if poi_pos not in self.pois:
                self.add_victim(poi_pos)
                # Remove fire and smoke from the POI position
                self.remove_fire_and_smoke(poi_pos)
        

    def reveal_poi(self, pos: Tuple[int, int]) -> bool:
        if pos in self.pois:
            poi_info = self.pois[pos]
            if not poi_info["revealed"]:
                poi_info["revealed"] = True
                if poi_info["is_victim"]:
                    print(f"A victim has been found at {pos}")
                else:
                    self.pois.pop(pos)
                return poi_info["is_victim"]
        return False

    '''Handling explosions smoke and fire'''

    def place_smoke(self, pos: Tuple[int, int]) -> None:
        if pos in self.fire:
            self.handle_explosion(pos)
        elif pos in self.smoke:
            self.convert_smoke_to_fire(pos)
        else:
            adjacent_fire = any(self.is_adjacent(pos, fire_pos) for fire_pos in self.fire)
            if adjacent_fire:
                self.fire.add(pos)
            else:
                self.smoke.add(pos)

    def convert_smoke_to_fire(self, pos: Tuple[int, int]) -> None:
        self.smoke.remove(pos)
        self.fire.add(pos)
        if pos in self.pois:
            self.lose_victim(pos)

    def handle_explosion(self, pos: Tuple[int, int]) -> None:
        print(f"Explosion at {pos}")
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            if new_pos in self.grid_structure:
                if self.wall_in_direction(pos, new_pos):
                    self.damage_wall(pos, new_pos)
                elif self.door_in_direction(pos, new_pos):
                    self.damage_door(pos, new_pos)
                elif new_pos in self.fire:
                    self.handle_shockwave(new_pos, (dx, dy))
                else:
                    self.place_fire_or_flip_smoke(new_pos)


    def handle_shockwave(self, start_pos: Tuple[int, int], direction: Tuple[int, int]) -> None:
        current_pos = start_pos
        while True:
            next_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
            if not self.is_valid_position(next_pos):
                break
            
            if next_pos not in self.fire:
                if next_pos in self.smoke:
                    self.convert_smoke_to_fire(next_pos)
                elif self.wall_in_direction(current_pos, next_pos):
                    self.damage_wall(current_pos, next_pos)
                    break
                elif self.door_in_direction(current_pos, next_pos):
                    self.damage_door(current_pos, next_pos)
                    break
                else:
                    self.place_fire_or_flip_smoke(next_pos)
                    break
            
            current_pos = next_pos

    def place_fire_or_flip_smoke(self, pos: Tuple[int, int]) -> None:
        if pos in self.smoke:
            self.convert_smoke_to_fire(pos)
        else:
            self.fire.add(pos)
        if pos in self.pois:
            self.lose_victim(pos)

    def handle_flashover(self) -> None:
        changed = True
        while changed:
            changed = False
            for smoke_pos in list(self.smoke):
                if any(self.is_adjacent(smoke_pos, fire_pos) for fire_pos in self.fire):
                    self.convert_smoke_to_fire(smoke_pos)
                    changed = True

    def remove_fire_and_smoke(self, pos: Tuple[int, int]) -> None:
        if pos in self.fire:
            self.fire.remove(pos)
        if pos in self.smoke:
            self.smoke.remove(pos)

    '''Funcion para genera el json'''
    
    def return_json(self):
        print(f"Grid actual {self.grid_structure}")
        print("\n")
        print(f"Paredes no derrumbadas y su salud: {self.wall_health}")
        print(f"Ubicacion del fuego: {self.fire}")
        print(f"Ubicacion del humo: {self.smoke}")
        print(f"Ubicacion de los pois: {self.pois}")
        for agent in range(len(self.agents)):
            print(f"Ubicacion de los agentes: {self.agents[agent].position}")

    def get_game_state(self) -> Dict[str, int]:
        return {
            "damage_markers": self.damage_markers,
            "rescued_victims": self.rescued_victims,
            "lost_victims": self.lost_victims,
            "running": self.running,
            "Agent #": len(self.agents)
        }


GRID_WIDTH,GRID_HEIGHT = 8, 6
wall_matrix = []
victims = []
fuego= []
puertas=[]
entrada=[]

#esto va a entrar en el codigo
with open("input.txt", 'r') as file:
    lines = file.readlines()

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

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

def visualize_grid_with_doors(GRID_WIDTH, GRID_HEIGTH, cell_walls, grid_dict,step):
    fig, ax = plt.subplots(figsize=(GRID_WIDTH, GRID_HEIGTH))

    # Draw the grid
    for i in range(GRID_WIDTH + 1):
        ax.plot([i, i], [0, GRID_HEIGTH], color="black")
    for j in range(GRID_HEIGTH + 1):
        ax.plot([0, GRID_WIDTH], [j, j], color="black")

    # Draw the walls and doors
    for i in range(GRID_HEIGTH):
        for j in range(GRID_WIDTH):
            walls = cell_walls[i][j]
            x = j
            y = GRID_HEIGTH - 1 - i  # Flip the y-axis for proper visualization

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
    ax.set_title(f"Step {step}")
    ax.set_xlim(0, GRID_WIDTH)
    ax.set_ylim(0, GRID_HEIGTH)
    ax.set_aspect('equal')
    ax.axis('off')  # Turn off the axis

    plt.show()

# Example usage
if __name__ == "__main__":
    model = FlashPointModel(GRID_WIDTH,GRID_HEIGHT,wall_matrix,victims,fuego,puertas,entrada)
    i =0

    model.return_json()
    while model.running and  i < 100: 
        print(f"\n--- Step {i} ---")
        model.step(i)
        # if i % 10 == 0:
        #     model.return_json()
        #     # visualize_grid_with_doors(GRID_WIDTH, GRID_HEIGHT, wall_matrix, model.grid_structure,i)
        i+=1
