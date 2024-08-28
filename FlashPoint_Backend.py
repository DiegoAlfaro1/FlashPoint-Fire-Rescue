import random
from typing import List, Tuple, Dict, Set
from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.time import RandomActivation

# Constants
GRID_WIDTH, GRID_HEIGHT = 8, 6
INITIAL_FIRE_LOCATIONS = frozenset([(2, 2), (2, 3), (3, 2), (3, 3), (3, 4), (3, 5), (4, 4), (5, 6), (5, 7), (6, 6)])
POI_LOCATIONS = frozenset([(2, 4), (5, 8), (5, 1)])

class Wall:
    def __init__(self, cell1: Tuple[int, int], cell2: Tuple[int, int], orientation: str):
        self.cell1, self.cell2 = cell1, cell2
        self.orientation = orientation
        self.state = "intact"
        self.damage = 0

    def get_state(self) -> str:
        return self.state

    def get_damage(self) -> int:
        return self.damage

    def damage_wall(self) -> None:
        if self.state == "intact":
            self.damage += 1
            self.state = "damaged" if self.damage == 1 else "broken"
        elif self.state == "damaged":
            self.state = "broken"

class Door:
    def __init__(self, cell1: Tuple[int, int], cell2: Tuple[int, int], orientation: str):
        self.cell1, self.cell2 = cell1, cell2
        self.orientation = orientation
        self.state = "closed"

    def get_state(self) -> str:
        return self.state

    def toggle(self) -> None:
        self.state = "open" if self.state == "closed" else "closed"

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
    def __init__(self, width: int = GRID_WIDTH, height: int = GRID_HEIGHT, n_agents: int = 6):
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.walls: List[Wall] = []
        self.doors: List[Door] = []
        self.damage_markers = 0
        self.rescued_victims = 0
        self.lost_victims = 0
        self.victims = [True,True,True,True,True,True,True,True,True,True,False,False,False,False]
        # self.total_victims = 0
        # self.max_victims = 12
        # self.max_false_alarms = 6 
        self.max_pois_onBoard = 3
        self.running = True
        self.building_cells = frozenset((x, y) for x in range(width) for y in range(height))
        self.n_agents = n_agents

        self.fire: Set[Tuple[int, int]] = set()
        self.smoke: Set[Tuple[int, int]] = set()
        self.pois: Dict[Tuple[int, int], Dict[str, bool]] = {}
        self.poi_count = 0
        self.exits: Set[Tuple[int, int]] = set()  # Add exits here

        self.exits = set([(0, y) for y in range(height)] + [(width-1, y) for y in range(height)] + 
                 [(x, 0) for x in range(width)] + [(x, height-1) for x in range(width)])
        
        self.setup_board()

    def setup_board(self) -> None:
        for i in range(self.n_agents):
            firefighter = FirefighterAgent(i, self)
            self.schedule.add(firefighter)
            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(firefighter, (x, y))
            firefighter.position = (x, y)

        self.fire = set(INITIAL_FIRE_LOCATIONS)
        
        random.shuffle(self.victims)
        for pos in POI_LOCATIONS:
            self.add_victim(pos)

        self.walls = [
            Wall((3, 3), (3, 4), "vertical"),
            Wall((4, 5), (5, 5), "horizontal"),
            Wall((5, 5), (5, 6), "vertical"),
        ]

        self.doors = [
            Door((1, 2), (1, 3), "vertical"),
            Door((4, 2), (5, 2), "horizontal"),
        ]

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
        return any(
            ((w.cell1 == pos and w.cell2 == new_pos) or 
             (w.cell2 == pos and w.cell1 == new_pos))
            for w in self.walls if w.state != "broken"
        )
    
    def door_in_direction(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> bool:
        return any(
            ((d.cell1 == pos and d.cell2 == new_pos) or 
             (d.cell2 == pos and d.cell1 == new_pos))
            for d in self.doors if d.state == "closed"
        )
    
    def damage_wall(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> None:
        for wall in self.walls:
            if ((wall.cell1 == pos and wall.cell2 == new_pos) or 
                (wall.cell2 == pos and wall.cell1 == new_pos)):
                wall.damage_wall()
                self.damage_markers += 1
                break

    def damage_door(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> None:
        for door in self.doors:
            if ((door.cell1 == pos and door.cell2 == new_pos) or 
                (door.cell2 == pos and door.cell1 == new_pos)):
                door.state = "broken"
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

# Example usage
if __name__ == "__main__":
    model = FlashPointModel()
    i =0
    while model.running and i < 100: 
        print(f"\n--- Step {i} ---")
        model.step()
        i+=1

