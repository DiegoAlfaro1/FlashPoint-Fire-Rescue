import random
from typing import List, Tuple, Dict, Set
from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.time import RandomActivation

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
            exit_positions = [exit_pos for exit_pos in self.model.exits if self.model.grid.is_cell_empty(exit_pos)]
            if exit_positions:
                target = min(exit_positions, key=lambda pos: ((pos[0] - self.position[0])**2 + (pos[1] - self.position[1])**2)**0.5)
                dx, dy = target[0] - self.position[0], target[1] - self.position[1]
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
    def __init__(self, width: int, height: int, wall_matrix,victims,fire, doors: List[Tuple[Tuple[int, int], Tuple[int, int]]],n_agents: int = 6,):
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        # self.walls: List[Wall] = []
        self.doors = set(doors) if doors else set()
        self.damage_markers = 0
        self.rescued_victims = 0
        self.lost_victims = 0
        self.victims = [True,True,True,True,True,True,True,True,True,True,False,False,False,False]
        self.max_pois_onBoard = 3
        self.running = True
        self.building_cells = frozenset((x, y) for x in range(1, width + 1) for y in range(1, height + 1))
        self.n_agents = n_agents

        self.fire: Set[Tuple[int, int]] = set()
        self.smoke: Set[Tuple[int, int]] = set()
        self.pois: Dict[Tuple[int, int], Dict[str, bool]] = {}
        self.poi_count = 0
        self.exits: Set[Tuple[int, int]] = set()  # Add exits here

        self.exits = set([(0, y) for y in range(height)] + [(width-1, y) for y in range(height)] + 
                 [(x, 0) for x in range(width)] + [(x, height-1) for x in range(width)])
        
        self.grid_structure = {}
        self.wall_health = {}
        self.initial_victims = victims
        self.initial_fire = fire
        self.width = width
        self.height = height

        self.setup_board(wall_matrix, victims, fire)

    '''Setup and initialization'''

    def setup_board(self, wall_matrix: List[str],victims,fire) -> None:
        for x in range(1, self.width + 1):
            for y in range(1, self.height + 1):
                self.grid_structure[(x, y)] = []

        # Process the wall matrix
        for i, cell in enumerate(wall_matrix):
            x, y = (i % self.width) + 1, (i // self.width) + 1
            self.process_cell(x, y, cell)
        
        for pos, connections in self.grid_structure.items():
            for adj, cost in connections:
                if cost == 5:  # If it's a wall
                    self.wall_health[(pos, adj)] = 2

        # Process the doors
        for door in self.doors:
            self.update_grid_for_door(*door)

        # Add firefighters (keep existing code)
        for i in range(self.n_agents):
            firefighter = FirefighterAgent(i, self)
            self.schedule.add(firefighter)
            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(firefighter, (x, y))
            firefighter.position = (x, y)

        for i in range(len(victims)):
            self.add_initial_victimas(victims)

        for i in range(len(fire)):
            self.fire.add(fire[i])

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

        # Remove wall health if there was a wall here
        self.wall_health.pop((cell1, cell2), None)
        self.wall_health.pop((cell2, cell1), None)

    '''victims and false alarms'''

    def add_initial_victimas(self, victims) -> None:
        for v in victims:
            self.pois[v[0]] = {"is_victim": v[1], "revealed": False}

    def add_victim(self, pos: Tuple[int, int]) -> None:
        is_victim = self.victims.pop()
        self.pois[pos] = {"is_victim": is_victim, "revealed": False}
        # print(f"Added {'victim' if is_victim else 'false alarm'} at {pos}")
        self.remove_fire_and_smoke(pos) 

    def check_firefighters_and_victims(self) -> None:
        # for agent in self.schedule.agents:
        #     if isinstance(agent, FirefighterAgent) and agent.position in self.fire:
        #         agent.knock_down()
        
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
                # print(f"A victim has been lost at {pos}! Total lost: {self.lost_victims}")
            del self.pois[pos]
            # print(f"Removed POI at {pos}")

    '''walls and doors'''

    def wall_in_direction(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> bool:
        return any(adj == new_pos and cost == 5 for adj, cost in self.grid_structure[pos])

    def door_in_direction(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> bool:
        return any(adj == new_pos and cost == 2 for adj, cost in self.grid_structure[pos])

    def damage_wall(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> None:
        if (pos, new_pos) in self.wall_health:
            self.wall_health[(pos, new_pos)] -= 1
            if self.wall_health[(pos, new_pos)] == 0:
                # Wall is destroyed
                self.grid_structure[pos] = [((x, y), 1 if (x, y) == new_pos else c) for ((x, y), c) in self.grid_structure[pos]]
                self.grid_structure[new_pos] = [((x, y), 1 if (x, y) == pos else c) for ((x, y), c) in self.grid_structure[new_pos]]
                del self.wall_health[(pos, new_pos)]
                self.damage_markers += 1
            else:
                print(f"Wall between {pos} and {new_pos} damaged. Health: {self.wall_health[(pos, new_pos)]}")
                self.damage_markers += 1
        elif (new_pos, pos) in self.wall_health:
            # Check the reverse direction
            self.damage_wall(new_pos, pos)

    def damage_door(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> None:
        # print(self.doors)
        print(self.grid_structure)
        self.grid_structure[pos] = [((x, y), 1 if (x, y) == new_pos else c) for ((x, y), c) in self.grid_structure[pos]]
        self.grid_structure[new_pos] = [((x, y), 1 if (x, y) == pos else c) for ((x, y), c) in self.grid_structure[new_pos]]
        self.doors.remove((pos, new_pos))

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

    def step(self) -> None:
        print("\nStarting new step")
        # print("Fire locations:", self.fire)
        # print("Smoke locations:", self.smoke)
        # print("POI locations:", self.pois)
        
        if self.running:
            self.advance_fire()
            self.reroll_pois()
            self.schedule.step()
            self.check_game_over()
            print(f"Fire positions: {self.fire}")
        else:
            return
        
        print("Step completed")
        # print("Fire locations:", self.fire)
        # print("Smoke locations:", self.smoke)
        # print("POI locations:", self.pois)
        print(f"Game state: {self.get_game_state()}")

    def advance_fire(self) -> None:
        fire_roll = (random.randint(1, 8), random.randint(1, 6))
        print(f"Advancing fire: rolled {fire_roll}")
        self.place_smoke(fire_roll)
        self.handle_flashover()
        self.check_firefighters_and_victims()

    def reroll_pois(self) -> None:
        # print(f"Rerolling POIs. Current POIs: {self.pois}")
        
        # # Remove POIs that are in fire locations
        # pois_to_remove = [pos for pos in self.pois if pos in self.fire]
        # # print(f"POIs to remove: {pois_to_remove}")
        # for pos in pois_to_remove:
        #     self.lose_victim(pos)
        
        # Count revealed POIs
        revealed_pois = sum(1 for poi in self.pois.values() if poi["revealed"])
        
        # Add new POIs if necessary
        while len(self.pois) < self.max_pois_onBoard:
            poi_roll = (random.randint(1, 8), random.randint(1, 6))
            print(f"Rolled POI: {poi_roll}")
            poi_pos = poi_roll
            if poi_pos not in self.pois:
                self.add_victim(poi_pos)
                # Remove fire and smoke from the POI position
                self.remove_fire_and_smoke(poi_pos)
        
        print(f"After rerolling, POIs: {self.pois}")

    def reveal_poi(self, pos: Tuple[int, int]) -> bool:
        print(self.pois)
        if pos in self.pois:
            poi_info = self.pois[pos]
            if not poi_info["revealed"]:
                poi_info["revealed"] = True
                if poi_info["is_victim"]:
                    print(f"A victim has been found at {pos}")
                else:
                    print(f"False alarm at {pos}")
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
                print(f"Placed fire at {pos} (adjacent to existing fire)")
            else:
                self.smoke.add(pos)
                print(f"Placed smoke at {pos}")

    def convert_smoke_to_fire(self, pos: Tuple[int, int]) -> None:
        self.smoke.remove(pos)
        self.fire.add(pos)
        print(f"Converted smoke to fire at {pos}")
        if pos in self.pois:
            self.lose_victim(pos)

    def handle_explosion(self, pos: Tuple[int, int]) -> None:
        print(f"Explosion at {pos}")
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            if self.is_valid_position(new_pos):
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
            print(f"Placed fire at {pos}")
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
            print(f"Removed fire at {pos} due to POI placement")
        if pos in self.smoke:
            self.smoke.remove(pos)
            print(f"Removed smoke at {pos} due to POI placement")

    '''Getters'''

    def get_grid_dimensions(self) -> Tuple[int, int]:
        return self.grid.width, self.grid.height

    def get_fire_locations(self) -> List[Tuple[int, int]]:
        return list(self.fire)

    def get_smoke_locations(self) -> List[Tuple[int, int]]:
        return list(self.smoke)

    def get_poi_locations(self) -> Dict[Tuple[int, int], Dict[str, bool]]:
        return {pos: info for pos, info in self.pois.items() if info["revealed"]}

    def get_wall_info(self) -> List[Tuple[Tuple[int, int], Tuple[int, int], str, str]]:
        return [(wall.cell1, wall.cell2, wall.orientation, wall.get_state()) for wall in self.walls]

    def get_door_info(self) -> List[Tuple[Tuple[int, int], Tuple[int, int], str, str]]:
        return [(door.cell1, door.cell2, door.orientation, door.get_state()) for door in self.doors]

    def get_firefighter_info(self) -> List[Tuple[int, Tuple[int, int], int, bool]]:
        return [(agent.unique_id, agent.get_position(), agent.get_ap(), agent.is_carrying_victim()) 
                for agent in self.schedule.agents]

    def get_game_state(self) -> Dict[str, int]:
        return {
            "damage_markers": self.damage_markers,
            "rescued_victims": self.rescued_victims,
            "lost_victims": self.lost_victims,
            "running": self.running
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

for y, line in enumerate(lines[:6]):
    bits= ''.join(line.split())
    for x, cell in enumerate(chunks(bits, 4)):
        wall_matrix.append(cell)

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

# Example usage
if __name__ == "__main__":
    model = FlashPointModel(GRID_WIDTH,GRID_HEIGHT,wall_matrix,victims,fuego,puertas)
    i =0
    # while model.running and i < 100: 
    #     print(f"\n--- Step {i} ---")
    #     model.step()
    #     i+=1

    for x in range(1, model.width + 1):  # Iterate from 1 to model.width
        for y in range(1, model.height + 1):  # Iterate from 1 to model.height
            key = (x, y)
            value = model.grid_structure[key]
            print(f"Key: {key}, Value: {value}")

