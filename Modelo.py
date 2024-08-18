from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
import random

GRID_WIDTH = 8
GRID_HEIGHT = 6
INITIAL_FIRE_LOCATIONS = [(3, 3), (2, 4), (5, 1)]
POI_LOCATIONS = [(1, 1), (4, 5), (6, 3)]

class Fire(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "Fire"

class Smoke(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "Smoke"

class POI(Agent):
    def __init__(self, unique_id, model, is_victim):
        super().__init__(unique_id, model)
        self.type = "POI"
        self.is_victim = is_victim

class FlashPointModel(Model):
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = SimultaneousActivation(self)
        self.walls = {}
        self.doors = {}
        self.damage_markers = 0
        self.rescued_victims = 0
        self.lost_victims = 0
        self.total_victims = 0
        self.setup_board()

    def setup_board(self):
        # Place initial fire and smoke
        for idx, pos in enumerate(INITIAL_FIRE_LOCATIONS):
            fire = Fire(idx, self)
            self.grid.place_agent(fire, pos)
            self.schedule.add(fire)
        
        # Place initial POIs
        for idx, pos in enumerate(POI_LOCATIONS):
            is_victim = random.choice([True, False])
            poi = POI(idx + 100, self, is_victim)
            self.grid.place_agent(poi, pos)
            self.schedule.add(poi)
            if is_victim:
                self.total_victims += 1

        # Initialize walls and doors (example setup, customize as needed)
        self.walls = {
            ((3, 3), (3, 4)): "intact",
            ((4, 5), (5, 5)): "intact",
        }
        self.doors = {
            ((1, 2), (1, 3)): "closed",
            ((4, 2), (5, 2)): "closed",
        }

    def place_smoke(self, pos):
        contents = self.grid.get_cell_list_contents([pos])
        smoke_present = any(isinstance(agent, Smoke) for agent in contents)
        fire_present = any(isinstance(agent, Fire) for agent in contents)

        if fire_present:
            self.handle_explosion(pos)
        elif smoke_present:
            self.convert_smoke_to_fire(pos)
        else:
            self.add_new_smoke(pos)

    def convert_smoke_to_fire(self, pos):
        for agent in self.grid.get_cell_list_contents([pos]):
            if isinstance(agent, Smoke):
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)
            elif isinstance(agent, POI) and agent.is_victim:
                self.lose_victim(agent)
        fire = Fire(f"Fire-{pos}", self)
        self.grid.place_agent(fire, pos)
        self.schedule.add(fire)

    def add_new_smoke(self, pos):
        smoke = Smoke(f"Smoke-{pos}", self)
        self.grid.place_agent(smoke, pos)
        self.schedule.add(smoke)

    def handle_explosion(self, pos):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            if self.grid.out_of_bounds(new_pos):
                continue
            
            if self.wall_in_direction(pos, new_pos):
                self.break_wall(pos, new_pos)
            elif self.door_in_direction(pos, new_pos):
                self.destroy_door(pos, new_pos)
            else:
                self.place_smoke(new_pos)
        
        self.damage_markers += 1
        self.check_game_over()

    def wall_in_direction(self, pos, new_pos):
        return ((pos, new_pos) in self.walls and self.walls[(pos, new_pos)] == "intact") or \
               ((new_pos, pos) in self.walls and self.walls[(new_pos, pos)] == "intact")

    def door_in_direction(self, pos, new_pos):
        return ((pos, new_pos) in self.doors) or ((new_pos, pos) in self.doors)

    def break_wall(self, pos, new_pos):
        if (pos, new_pos) in self.walls:
            self.walls[(pos, new_pos)] = "broken"
        elif (new_pos, pos) in self.walls:
            self.walls[(new_pos, pos)] = "broken"

    def destroy_door(self, pos, new_pos):
        if (pos, new_pos) in self.doors:
            del self.doors[(pos, new_pos)]
        elif (new_pos, pos) in self.doors:
            del self.doors[(new_pos, pos)]

    def lose_victim(self, victim):
        self.grid.remove_agent(victim)
        self.schedule.remove(victim)
        self.lost_victims += 1
        print(f"A victim has been lost! Total lost: {self.lost_victims}")

    def check_game_over(self):
        if self.damage_markers >= 24:
            print("Game Over: Building has collapsed!")
            self.running = False
        elif self.lost_victims >= 7:
            print("Game Over: Too many victims lost!")
            self.running = False
        elif self.rescued_victims == self.total_victims:
            print("Victory: All victims have been rescued!")
            self.running = False

    def advance_fire(self):
        fire_roll = random.randint(1, 6) + random.randint(1, 6)
        fire_pos = (fire_roll % self.grid.width, fire_roll // self.grid.width)
        self.place_smoke(fire_pos)

    def step(self):
        self.advance_fire()
        self.schedule.step()
        self.check_game_over()

model = FlashPointModel()