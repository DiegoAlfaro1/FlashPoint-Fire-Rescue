from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import random

GRID_WIDTH = 8
GRID_HEIGHT = 6
INITIAL_FIRE_LOCATIONS = [(2, 2), (2, 3), (3, 2),(3, 3),(3,4),(3,5),(4,4),(5,6),(5,7),(6,6)]
POI_LOCATIONS = [(2, 4), (5, 8), (5, 1)]

class Wall:
    def __init__(self, cell1, cell2, orientation, state="intact"):
        self.cell1 = cell1  # First cell
        self.cell2 = cell2  # Second cell
        self.orientation = orientation  # "horizontal" or "vertical"
        self.state = state  # "intact" or "broken" or "damaged"
        self.damage = 0

class Door:
    def __init__(self, cell1, cell2, orientation, state="closed"):
        self.cell1 = cell1
        self.cell2 = cell2
        self.orientation = orientation
        self.state = state

class FlashPointModel(Model):
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.walls =[]
        self.doors = {}
        self.damage_markers = 0
        self.rescued_victims = 0
        self.lost_victims = 0
        self.total_victims = 0
        self.max_victims = 12
        self.max_false_alarms = 6 
        self.max_pois_onBoard = 3
        self.running = True

        # Ambient variables
        self.fire = set()
        self.smoke = set()
        self.pois = {}
        self.poi_count = 0
        
        self.setup_board()

    #cambio
    def add_victim(self, pos):
        if self.poi_count < self.max_pois_onBoard:
            is_victim = random.choice([True, False])
            self.pois[pos] = {"is_victim": is_victim, "revealed": False}
            self.poi_count += 1
            if is_victim:
                self.total_victims += 1

    def setup_board(self):
        for pos in INITIAL_FIRE_LOCATIONS:
            self.fire.add(pos)
        
        for idx, pos in enumerate(POI_LOCATIONS):
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

    def place_smoke(self, pos):
        if pos in self.fire:
            self.handle_explosion(pos)
        elif pos in self.smoke:
            self.convert_smoke_to_fire(pos)
        else:
            self.add_new_smoke(pos)

    def convert_smoke_to_fire(self, pos):
        self.smoke.remove(pos)
        self.fire.add(pos)
        if pos in self.pois and self.pois[pos]:
            self.lose_victim(pos)

    def add_new_smoke(self, pos):
        self.smoke.add(pos)

    def handle_explosion(self, pos):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            if new_pos[0] < 0 or new_pos[0] >= self.grid.width or new_pos[1] < 0 or new_pos[1] >= self.grid.height:
                continue
            
            if self.wall_in_direction(pos, new_pos):
                self.damage_wall(pos, new_pos)
            elif self.door_in_direction(pos, new_pos):
                self.damage_door(pos, new_pos)
            else:
                self.place_smoke(new_pos)
        
        self.check_game_over()

    def wall_in_direction(self, pos, new_pos):
        return any(
            ((w.cell1 == pos and w.cell2 == new_pos) or 
             (w.cell2 == pos and w.cell1 == new_pos))
            for w in self.walls if w.state != "broken"
        )
    
    def door_in_direction(self, pos, new_pos):
        return any(
            ((d.cell1 == pos and d.cell2 == new_pos) or 
             (d.cell2 == pos and d.cell1 == new_pos))
            for d in self.doors if d.state == "closed"
        )
    
    def damage_wall(self, pos, new_pos):
        for wall in self.walls:
            if ((wall.cell1 == pos and wall.cell2 == new_pos) or 
                (wall.cell2 == pos and wall.cell1 == new_pos)):
                if wall.state == "intact":
                    wall.damage += 1
                    self.damage_markers += 1
                    if wall.damage == 2:
                        wall.state = "broken"
                    else:
                        wall.state = "damaged"
                elif wall.state == "damaged":
                    wall.state = "broken"
                    self.damage_markers += 1
                break

    """
    def break_wall(self, pos, new_pos):
        for wall in self.walls:
            if ((wall.cell1 == pos and wall.cell2 == new_pos) or 
                (wall.cell2 == pos and wall.cell1 == new_pos)):
                wall.state = "broken"
                break
    """

    def destroy_door(self, pos, new_pos):
        if (pos, new_pos) in self.doors:
            del self.doors[(pos, new_pos)]
        elif (new_pos, pos) in self.doors:
            del self.doors[(new_pos, pos)]

    def damage_door(self, pos, new_pos):
        for door in self.doors:
            if ((door.cell1 == pos and door.cell2 == new_pos) or 
                (door.cell2 == pos and door.cell1 == new_pos)):
                door.state = "broken"
                break

    #cambio
    def lose_victim(self, pos):
        if pos in self.pois:
            if self.pois[pos]["is_victim"]:
                self.lost_victims += 1
                print(f"A victim has been lost! Total lost: {self.lost_victims}")
            del self.pois[pos]
            self.poi_count -= 1

    def check_game_over(self):
        if self.damage_markers >= 24:
            print("Game Over: Building has collapsed!")
            self.running = False
        elif self.lost_victims >= 4:
            print("Game Over: Too many victims lost!")
            self.running = False
        elif self.rescued_victims == 7:
            print("Victory: All victims have been rescued!")
            self.running = False

    def advance_fire(self):
        fire_roll = random.randint(1, 8) + random.randint(1, 6)
        fire_pos = (fire_roll % self.grid.width, fire_roll // self.grid.width)
        self.place_smoke(fire_pos)

    #cambio
    def rerollPois(self):
        while len(self.pois) < self.max_pois_onBoard:
            poi_roll = random.randint(1, 8) + random.randint(1, 6)
            poi_pos = (poi_roll % self.grid.width, poi_roll // self.grid.width)
            if poi_pos not in self.pois and poi_pos not in self.fire:
                self.add_victim(poi_pos)

    #cambio
    def reveal_poi(self, pos):
        if pos in self.pois:
            self.pois[pos]["revealed"] = True
            if self.pois[pos]["is_victim"]:
                self.rescued_victims += 1
                print(f"A victim has been rescued! Total rescued: {self.rescued_victims}")
            else:
                print("False alarm!")
            del self.pois[pos]
            self.poi_count -= 1

    def step(self):
        #step de agente
        self.advance_fire()
        self.rerollPois()
        self.schedule.step()
        self.check_game_over()

model = FlashPointModel()

model.step()


