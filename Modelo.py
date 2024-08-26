from mesa import Model
from mesa import Agent
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

class FirefighterAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.position = None
        self.ap = 4
        self.saved_ap = 0
        self.carrying_victim = False

    def move(self, new_pos):
        ap_cost = 2 if new_pos in self.model.fire else 1
        if self.carrying_victim:
            ap_cost = 2
            if new_pos in self.model.fire:
                return False  # Can't move into fire while carrying a victim
        
        if self.ap >= ap_cost:
            self.ap -= ap_cost
            old_pos = self.position
            self.model.grid.move_agent(self, new_pos)
            self.position = new_pos
            
            if new_pos in self.model.pois and not self.model.pois[new_pos]["revealed"]:
                self.reveal_poi(new_pos)
            
            if self.carrying_victim and new_pos in self.model.exits:
                self.rescue_victim()
            
            return True
        return False

    def reveal_poi(self, pos):
        is_victim = self.model.reveal_poi(pos)
        if is_victim and not self.carrying_victim:
            self.carrying_victim = True
            print(f"Firefighter {self.unique_id} is now carrying a victim.")

    def rescue_victim(self):
        self.model.rescued_victims += 1
        self.carrying_victim = False
        print(f"Victim rescued by Firefighter {self.unique_id}! Total rescued: {self.model.rescued_victims}")

    def open_close_door(self):
        for door in self.model.doors:
            if self.position in [door.cell1, door.cell2]:
                if self.ap >= 1:
                    self.ap -= 1
                    door.state = "open" if door.state == "closed" else "closed"
                    return True
        return False

    def extinguish(self, target_pos):
        if target_pos in self.model.fire:
            if self.ap >= 2:
                self.ap -= 2
                self.model.fire.remove(target_pos)
                return True
        elif target_pos in self.model.smoke:
            if self.ap >= 1:
                self.ap -= 1
                self.model.smoke.remove(target_pos)
                return True
        return False

    def chop(self):
        for wall in self.model.walls:
            if self.position in [wall.cell1, wall.cell2]:
                if self.ap >= 2:
                    self.ap -= 2
                    wall.damage += 1
                    if wall.damage == 2:
                        wall.state = "broken"
                    else:
                        wall.state = "damaged"
                    self.model.damage_markers += 1
                    return True
        return False

    def step(self):
        self.ap += self.saved_ap
        self.saved_ap = 0

        while self.ap > 0:
            actions = [
                self.move_action,
                self.open_close_door,
                self.extinguish_action,
                self.chop
            ]
            random.shuffle(actions)

            action_performed = False
            for action in actions:
                if action():
                    action_performed = True
                    break

            if not action_performed:
                break

        self.saved_ap = min(self.ap, 4)
        self.ap = 0
    
    def move_action(self):
        if self.carrying_victim:
            exit_positions = [exit_pos for exit_pos in self.model.exits if self.model.grid.is_cell_empty(exit_pos)]
            if exit_positions:
                target = min(exit_positions, key=lambda pos: ((pos[0] - self.position[0])**2 + (pos[1] - self.position[1])**2)**0.5)
                dx = target[0] - self.position[0]
                dy = target[1] - self.position[1]
                if dx != 0:
                    new_pos = (self.position[0] + (1 if dx > 0 else -1), self.position[1])
                elif dy != 0:
                    new_pos = (self.position[0], self.position[1] + (1 if dy > 0 else -1))
                else:
                    new_pos = target
                return self.move(new_pos)
        
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            new_pos = (self.position[0] + dx, self.position[1] + dy)
            if self.model.grid.is_cell_empty(new_pos):
                return self.move(new_pos)
        return False

    def extinguish_action(self):
        adjacent_cells = self.model.grid.get_neighborhood(
            self.position, moore=False, include_center=True)
        for cell in adjacent_cells:
            if cell in self.model.fire or cell in self.model.smoke:
                return self.extinguish(cell)
        return False

class FlashPointModel(Model):
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT, n_agents=1):
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
        self.building_cells = [(x, y) for x in range(width) for y in range(height)]
        self.n_agents = n_agents

        # Ambient variables
        self.fire = set()
        self.smoke = set()
        self.pois = {}
        self.poi_count = 0
        
        self.setup_board()

    def add_victim(self, pos):
        if self.poi_count < self.max_pois_onBoard:
            is_victim = random.choice([True, False])
            self.pois[pos] = {"is_victim": is_victim, "revealed": False}
            self.poi_count += 1
            if is_victim:
                self.total_victims += 1

    def setup_board(self):

        for i in range(self.num_firefighters):
            firefighter = FirefighterAgent(i, self)
            self.schedule.add(firefighter)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(firefighter, (x, y))
            firefighter.position = (x, y)

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

    def rerollPois(self):
        while len(self.pois) < self.max_pois_onBoard:
            poi_roll = random.randint(1, 8) + random.randint(1, 6)
            poi_pos = (poi_roll % self.grid.width, poi_roll // self.grid.width)
            if poi_pos not in self.pois and poi_pos not in self.fire:
                self.add_victim(poi_pos)

    def reveal_poi(self, pos):
        if pos in self.pois:
            poi_info = self.pois[pos]
            if poi_info["is_victim"]:
                print(f"A victim has been found at {pos}")
            else:
                print(f"False alarm at {pos}")
                self.pois.pop(pos)
            poi_info["revealed"] = True
            return poi_info["is_victim"]
        return False

    def step(self):
        self.advance_fire()
        self.rerollPois()
        self.schedule.step()
        self.check_game_over()

model = FlashPointModel()

model.step()


