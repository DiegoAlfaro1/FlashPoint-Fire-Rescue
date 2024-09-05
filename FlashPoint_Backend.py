import random
from typing import List, Tuple, Dict, Set
from mesa import Model, Agent
from mesa.space import MultiGrid, SingleGrid
from mesa.time import RandomActivation
import matplotlib.pyplot as plt


class FirefighterAgent(Agent):
    def __init__(self, unique_id: int, model: 'FlashPointModel'):
        """
        Inicializa un nuevo agente bombero.

        Parámetros:
        - unique_id: Identificador único del bombero.
        - model: Instancia del modelo FlashPointModel en el que el bombero operará.
        """
        super().__init__(unique_id, model)
        # Inicialización de atributos del agente bombero
        self.position: Tuple[int, int] = (0, 0)  # Posición inicial en el grid
        self.ap = 4  # Puntos de acción iniciales
        self.saved_ap = 0  # Puntos de acción guardados
        self.max_ap = 8  # Puntos de acción máximos permitidos
        self.carrying_victim = False  # Estado de si el agente está cargando una víctima

    def get_position(self) -> Tuple[int, int]:
        """
        Devuelve la posición actual del bombero.

        Retorna:
        - Tupla con las coordenadas (x, y) de la posición actual del bombero.
        """
        return self.position

    def get_ap(self) -> int:
        """
        Devuelve los puntos de acción actuales del bombero.

        Retorna:
        - Número entero que representa los puntos de acción actuales.
        """
        return self.ap
    
    def is_carrying_victim(self) -> bool:
        """
        Devuelve si el bombero está cargando una víctima.

        Retorna:
        - Verdadero si el bombero está cargando una víctima, falso en caso contrario.
        """
        return self.carrying_victim

    def move(self, new_pos: Tuple[int, int]) -> bool:
        """
        Mueve el bombero a una nueva posición si es válida y hay suficientes puntos de acción.

        Parámetros:
        - new_pos: Nueva posición a la que se desea mover el bombero.

        Retorna:
        - Verdadero si el movimiento fue exitoso, falso en caso contrario.
        """
        if not self.is_valid_position(new_pos):
            return False

        # Verifica si la celda de destino está vacía
        if not self.model.grid.is_cell_empty(new_pos):
            return False

        # Calcula el costo de puntos de acción para moverse a la nueva posición
        ap_cost = 2 if new_pos in self.model.fire else 1
        if self.carrying_victim:
            ap_cost = 2  # Mayor costo si lleva una víctima
            if new_pos in self.model.fire:
                return False  # No puede moverse a una celda en llamas con una víctima

        # Verifica si el bombero tiene suficientes puntos de acción
        if self.ap >= ap_cost:
            self.ap -= ap_cost  # Reduce los puntos de acción
            self.model.grid.move_agent(self, new_pos)  # Mueve al bombero en el grid
            self.position = new_pos  # Actualiza la posición del bombero
            
            # Revela un punto de interés (POI) si se encuentra en uno
            if new_pos in self.model.pois and not self.model.pois[new_pos]["revealed"]:
                self.reveal_poi(new_pos)
            
            # Rescata a la víctima si está en una salida
            if self.carrying_victim and new_pos in self.model.exits:
                self.rescue_victim()

            return True
        return False

    def reveal_poi(self, pos: Tuple[int, int]) -> None:
        """
        Revela un punto de interés (POI) en una posición dada.

        Parámetros:
        - pos: Tupla con las coordenadas (x, y) del punto de interés a revelar.
        """
        is_victim = self.model.reveal_poi(pos)
        if is_victim and not self.carrying_victim:
            self.carrying_victim = True  # El bombero comienza a cargar una víctima

    def rescue_victim(self) -> None:
        """
        Rescata a la víctima si el bombero está en una salida.
        """
        self.model.rescued_victims += 1  # Incrementa el contador de víctimas rescatadas
        self.carrying_victim = False  # El bombero ya no lleva una víctima

    def open_close_door(self) -> bool:
        """
        Abre o cierra una puerta adyacente si hay suficientes puntos de acción.

        Retorna:
        - Verdadero si la acción fue exitosa, falso en caso contrario.
        """
        for door in self.model.doors:
            if self.position in (door.cell1, door.cell2):
                if self.ap >= 1:
                    self.ap -= 1  # Reduce un punto de acción por abrir/cerrar una puerta
                    door.toggle()  # Alterna el estado de la puerta
                    return True
        return False

    def extinguish(self, target_pos: Tuple[int, int]) -> bool:
        """
        Extingue fuego o humo en una posición objetivo si hay suficientes puntos de acción.

        Parámetros:
        - target_pos: Tupla con las coordenadas (x, y) de la posición a extinguir.

        Retorna:
        - Verdadero si la acción fue exitosa, falso en caso contrario.
        """
        if target_pos in self.model.fire and self.ap >= 2:
            self.ap -= 2  # Extinguir fuego cuesta 2 puntos de acción
            self.model.fire.remove(target_pos)  # Remueve el fuego de la posición
            return True
        elif target_pos in self.model.smoke and self.ap >= 1:
            self.ap -= 1  # Extinguir humo cuesta 1 punto de acción
            self.model.smoke.remove(target_pos)  # Remueve el humo de la posición
            return True
        return False

    def chop(self) -> bool:
        """
        Daño una pared adyacente si hay suficientes puntos de acción.

        Retorna:
        - Verdadero si la acción fue exitosa, falso en caso contrario.
        """
        for wall in self.model.walls:
            if self.position in (wall.cell1, wall.cell2):
                if self.ap >= 2:
                    self.ap -= 2  # Reducir dos puntos de acción por romper una pared
                    wall.damage_wall()  # Daño a la pared
                    self.model.damage_markers += 1  # Aumenta el contador de marcadores de daño
                    return True
        return False

    def step(self) -> None:
        """
        Define el comportamiento del bombero en cada paso de la simulación.
        Este método se llama en cada paso del modelo y realiza las acciones 
        del bombero en el siguiente orden de prioridad:
        1. Moverse hacia una salida si está cargando una víctima.
        2. Apagar fuego o humo.
        3. Revelar puntos de interés (POIs) adyacentes.
        4. Realizar un movimiento aleatorio.
        """
        self.ap += self.saved_ap  # Añade los puntos de acción guardados al total
        self.saved_ap = 0  # Reinicia los puntos de acción guardados

        # Acciones de estrategia en orden de prioridad
        if self.carrying_victim and self.move_action():
            return  # Si se movió con éxito hacia una salida, termina el paso

        if self.extinguish_action():
            return  # Si extinguió fuego o humo con éxito, termina el paso

        if self.reveal_poi_action():
            return  # Si reveló un POI con éxito, termina el paso

        if self.random_move():
            return  # Si se movió aleatoriamente con éxito, termina el paso

        # Guarda los puntos de acción restantes para el próximo paso
        self.saved_ap = min(self.ap, 4)  # Limita los puntos de acción guardados a 4
        self.ap = 0  # Establece los puntos de acción actuales a 0

    def move_action(self) -> bool:
        """
        Acción de movimiento hacia una salida si el bombero lleva una víctima.
        Intenta moverse en dirección a una salida si el bombero está cargando una víctima.

        Retorna:
        - Verdadero si el movimiento fue exitoso, falso en caso contrario.
        """
        if self.carrying_victim:
            # Selecciona una dirección de movimiento hacia una salida
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
        """
        Acción de revelar un punto de interés (POI) adyacente.
        Intenta revelar un POI en una celda adyacente si está vacía.

        Retorna:
        - Verdadero si se reveló un POI con éxito, falso en caso contrario.
        """
        adjacent_cells = self.model.grid.get_neighborhood(self.position, moore=False, include_center=True)
        for cell in adjacent_cells:
            if cell in self.model.pois and not self.model.pois[cell]["revealed"]:
                # Verifica si la celda está vacía antes de moverse
                if self.model.grid.is_cell_empty(cell):
                    if self.move(cell):
                        return True
        return False

    def random_move(self) -> bool:
        """
        Realiza un movimiento aleatorio del bombero en una dirección posible.
        Baraja las direcciones posibles (arriba, abajo, izquierda, derecha) y
        intenta mover al bombero a una celda vacía en una de esas direcciones.

        Retorna:
        - Verdadero si el movimiento fue exitoso, falso en caso contrario.
        """
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Direcciones posibles: derecha, izquierda, abajo, arriba
        random.shuffle(directions)  # Baraja las direcciones aleatoriamente

        for dx, dy in directions:
            new_pos = (self.position[0] + dx, self.position[1] + dy)
            # Verifica si la nueva posición es válida y está vacía
            if self.is_valid_position(new_pos) and self.model.grid.is_cell_empty(new_pos):
                return self.move(new_pos)  # Intenta mover al bombero a la nueva posición
        
        return False  # No se pudo mover a ninguna dirección

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """
        Verifica si una posición está dentro de los límites del grid.
        
        Argumentos:
        - pos: La posición a verificar como una tupla (x, y).

        Retorna:
        - Verdadero si la posición está dentro de los límites del grid, falso en caso contrario.
        """
        return 0 <= pos[0] < self.model.grid.width and 0 <= pos[1] < self.model.grid.height

    def extinguish_action(self) -> bool:
        """
        Acción de extinguir fuego o humo en las celdas adyacentes.
        Revisa las celdas adyacentes y, si hay fuego o humo, intenta extinguirlo.

        Retorna:
        - Verdadero si se extinguió con éxito fuego o humo, falso en caso contrario.
        """
        adjacent_cells = self.model.grid.get_neighborhood(self.position, moore=False, include_center=True)
        for cell in adjacent_cells:
            if cell in self.model.fire or cell in self.model.smoke:
                return self.extinguish(cell)  # Intenta extinguir el fuego o humo en la celda adyacente
        
        return False  # No se pudo extinguir fuego o humo en ninguna celda adyacente

class FlashPointModel(Model):

    '''Configuración e inicialización'''
    def __init__(self, width: int, height: int, wall_matrix, victims, fire, doors: List[Tuple[Tuple[int, int], Tuple[int, int]]], exits, n_agents: int = 6):
        """
        Inicializa una nueva instancia del juego con los parámetros dados.

        Parámetros:
        - width: Ancho de la cuadrícula.
        - height: Altura de la cuadrícula.
        - wall_matrix: Matriz que describe las paredes en el grid.
        - victims: Lista de víctimas iniciales.
        - fire: Lista de posiciones iniciales de fuego.
        - doors: Lista de puertas entre celdas.
        - exits: Lista de posiciones de salida.
        - n_agents: Número de agentes bomberos a inicializar (por defecto es 6).
        """
        # Inicializar la cuadrícula y el schedule
        self.grid = SingleGrid(height+1, width+1, torus=False)  # Crear una cuadrícula sin torus
        self.schedule = RandomActivation(self)  # Crear un scheduler para la activación aleatoria de agentes

        # Configurar parámetros del juego
        self.doors = set(doors) if doors else set()  # Inicializar puertas
        self.damage_markers = 0  # Contador de marcadores de daño
        self.rescued_victims = 0  # Contador de víctimas rescatadas
        self.lost_victims = 0  # Contador de víctimas perdidas
        self.victims = [True, True, True, True, True, True, True, True, True, True, False, False, False, False]  # Lista de estados de las víctimas
        self.max_pois_onBoard = 3  # Número máximo de puntos de interés en el tablero
        self.running = True  # Indicador de si el juego está en ejecución
        self.building_cells = frozenset((x, y) for x in range(1, width + 1) for y in range(1, height + 1))  # Celdas de construcción
        self.n_agents = n_agents  # Número de agentes bomberos
        self.ff_ids = []  # Lista de IDs de bomberos disponibles

        self.current_step = 0  # Paso actual de la simulación

        # Configurar elementos del juego
        self.exits = exits  # Posiciones de salida
        self.fire: Set[Tuple[int, int]] = set()  # Conjunto de posiciones de fuego
        self.smoke: Set[Tuple[int, int]] = set()  # Conjunto de posiciones de humo
        self.pois: Dict[Tuple[int, int], Dict[str, bool]] = {}  # Puntos de interés (víctimas potenciales)
        self.poi_count = 0  # Contador de puntos de interés

        # Inicializar estructuras de la cuadrícula
        self.grid_structure = {}  # Estructura de la cuadrícula
        self.ouf_of_bounds_grid_structure = {}  # Estructura de la cuadrícula fuera de los límites
        self.wall_health = {}  # Salud de las paredes

        # Almacenar el estado inicial del juego
        self.initial_victims = victims  # Víctimas iniciales
        self.initial_fire = fire  # Fuego inicial
        self.width = width  # Ancho de la cuadrícula
        self.height = height  # Altura de la cuadrícula

        self.agents = []  # Lista de agentes en el juego

        # Configurar el tablero de juego
        self.setup_board(wall_matrix, victims, fire)

    def setup_board(self, wall_matrix: List[str], victims, fire) -> None:
        """
        Configura el tablero del juego según la matriz de paredes, víctimas y fuego inicial.

        Parámetros:
        - wall_matrix: Matriz que describe las paredes en el grid.
        - victims: Lista de víctimas iniciales.
        - fire: Lista de posiciones iniciales de fuego.
        """
        # Generar la estructura de la cuadrícula
        self.grid_structure, self.ouf_of_bounds_grid_structure = self.generate_grid(self.width, self.height, wall_matrix, self.exits)

        # Inicializar la salud de las paredes
        for pos, connections in self.grid_structure.items():
            for adj, cost in connections:
                if cost == 5:  # Si es una pared
                    self.wall_health[(pos, adj)] = 2  # Salud inicial de la pared

        # Procesar las puertas
        self.update_walls_to_doors(self.grid_structure, self.doors)

        # Añadir el fuego inicial
        for i in range(len(fire)):
            self.fire.add(fire[i])  # Añadir posiciones de fuego al conjunto de fuego

        # Añadir agentes bomberos
        for i in range(self.n_agents):
            firefighter = FirefighterAgent(i, self)  # Crear un nuevo agente bombero
            self.schedule.add(firefighter)  # Añadir el bombero al scheduler
            while True:
                x, y = self.random.randrange(1, self.grid.width), self.random.randrange(1,self.grid.height)  # Generar una posición aleatoria
                if self.grid.is_cell_empty((x, y)) and (x, y) not in self.fire and (x, y) not in self.pois:
                    break  # Salir del ciclo si la celda es válida

            self.grid.place_agent(firefighter, (x, y))  # Colocar el bombero en la cuadrícula
            firefighter.position = (x, y)  # Establecer la posición del bombero
            self.agents.append(firefighter)  # Añadir el bombero a la lista de agentes

        # Añadir víctimas iniciales
        for i in range(len(victims)):
            self.add_initial_victimas(victims)  # Añadir víctimas iniciales a los puntos de interés

    def process_cell(self, x: int, y: int, cell: str) -> None:
        """
        Procesa una celda de la cuadrícula para actualizar su estructura de acuerdo con el contenido de la celda.

        Parámetros:
        - x: Coordenada x de la celda.
        - y: Coordenada y de la celda.
        - cell: String que representa el contenido de la celda (paredes y caminos).
        """
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # Direcciones: arriba, izquierda, abajo, derecha
        for i, direction in enumerate(directions):
            new_x, new_y = x + direction[0], y + direction[1]  # Coordenadas de la celda adyacente
            if 1 <= new_x < self.width and 1 <= new_y < self.height:
                if cell[i] == '0':
                    self.grid_structure[(x, y)].append(((new_x, new_y), 1))  # Agregar camino
                else:
                    # Establecer paredes con costo 5
                    self.grid_structure[(x, y)].append(((new_x, new_y), 5))
                    # Inicializar la salud de la pared
                    self.wall_health[((x, y), (new_x, new_y))] = 2

    def update_grid_for_door(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> None:
        """
        Actualiza la estructura de la cuadrícula para reflejar una puerta entre dos celdas.

        Parámetros:
        - cell1: La primera celda de la puerta.
        - cell2: La segunda celda de la puerta.
        """
        # Verificar si las celdas están en la estructura de la cuadrícula
        if cell1 not in self.grid_structure or cell2 not in self.grid_structure:
            print(f"Advertencia: La puerta entre {cell1} y {cell2} está fuera de la cuadrícula. Omitiendo.")
            return

        # Actualizar la estructura de la cuadrícula para reflejar una puerta (costo 2) entre cell1 y cell2
        self.grid_structure[cell1] = [((x, y), 2 if (x, y) == cell2 else c) for ((x, y), c) in self.grid_structure[cell1]]
        self.grid_structure[cell2] = [((x, y), 2 if (x, y) == cell1 else c) for ((x, y), c) in self.grid_structure[cell2]]

        # Asegurar que la puerta esté en self.doors
        door = (cell1, cell2)
        reverse_door = (cell2, cell1)
        if door not in self.doors and reverse_door not in self.doors:
            self.doors.add(door)  # Añadir la puerta a la lista de puertas

    '''victims and false alarms'''

    def add_initial_victimas(self, victims) -> None:
        """
        Agrega las víctimas iniciales a la lista de puntos de interés (pois).

        Parámetros:
        - victims: una lista de tuplas, donde cada tupla contiene la posición
                de la víctima y un booleano indicando si es una víctima o no.
        """
        for v in victims:
            # Se añade cada víctima a la lista de puntos de interés (pois) con sus propiedades.
            self.pois[v[0]] = {"is_victim": v[1], "revealed": False}

    def add_victim(self, pos: Tuple[int, int]) -> None:
        """
        Agrega una nueva víctima en una posición específica del grid.

        Parámetros:
        - pos: Una tupla que representa la posición (x, y) en el grid.
        """
        # Se saca una víctima de la lista de víctimas y se asigna a la posición dada.
        is_victim = self.victims.pop()
        self.pois[pos] = {"is_victim": is_victim, "revealed": False}
        # Se elimina fuego y humo en la posición especificada.
        self.remove_fire_and_smoke(pos) 

    def check_firefighters_and_victims(self, actual_step) -> None:
        """
        Verifica la situación de los bomberos y las víctimas en el grid,
        agregando nuevos bomberos si es necesario.

        Parámetros:
        - actual_step: el paso actual de la simulación.
        """
        print("Checking firefighters and victims")
        agents_to_remove = []  # Lista para almacenar agentes a ser removidos.
        flag = True

        # Recolecta agentes que deben ser removidos del grid.
        for agent in self.agents:
            if isinstance(agent, FirefighterAgent) and agent.position in self.fire:
                self.ff_ids.append(agent.unique_id)
                print(f"Firefighter in fire in {agent.position}")
                print(self.ff_ids)
                agents_to_remove.append(agent)

        # Remueve agentes recolectados del grid y del planificador.
        for agent in agents_to_remove:
            self.grid.remove_agent(agent)
            self.schedule.remove(agent)
            self.agents.remove(agent)

        # Verifica si hay menos de 6 bomberos en el grid.
        num_firefighters = len([agent for agent in self.agents if isinstance(agent, FirefighterAgent)])

        # Añade nuevos agentes si las condiciones son adecuadas.
        attempt_counter = 0
        while flag and num_firefighters < 6:
            x, y = random.randint(1, 6), random.randint(1, 8)  # Genera una posición aleatoria.
            attempt_counter += 1

            # Verifica si la posición es válida para agregar un nuevo bombero.
            if self.grid.is_cell_empty((x, y)) and (x, y) not in self.fire and (x, y) not in self.pois:
                # Agrega un nuevo bombero si es un paso par y hay bomberos disponibles para agregar.
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

            # Si no se puede agregar un nuevo bombero después de 20 intentos, se rompe el ciclo.
            if attempt_counter >= 20:
                print("Unable to place a new firefighter after 20 attempts.")
                break

        # Verifica si alguna posición en los puntos de interés (pois) tiene fuego.
        for pos in list(self.pois.keys()):
            if pos in self.fire:
                self.lose_victim(pos)

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """
        Verifica si una posición es válida dentro del grid.

        Parámetros:
        - pos: Una tupla que representa la posición (x, y).

        Retorna:
        - True si la posición está dentro de los límites del grid, False en caso contrario.
        """
        return 0 <= pos[0] < self.grid.width and 0 <= pos[1] < self.grid.height

    def is_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """
        Verifica si dos posiciones son adyacentes.

        Parámetros:
        - pos1: Una tupla que representa la primera posición (x, y).
        - pos2: Una tupla que representa la segunda posición (x, y).

        Retorna:
        - True si las posiciones son adyacentes, False en caso contrario.
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    def lose_victim(self, pos: Tuple[int, int]) -> None:
        """
        Marca una víctima como perdida si está en una posición con fuego y no ha sido revelada.

        Parámetros:
        - pos: Una tupla que representa la posición (x, y).
        """
        if pos in self.pois:
            # Incrementa el contador de víctimas perdidas si hay una víctima en la posición que no ha sido revelada.
            if self.pois[pos]["is_victim"] and not self.pois[pos]["revealed"]:
                self.lost_victims += 1
            # Elimina la víctima de los puntos de interés (pois).
            del self.pois[pos]

    '''walls and doors'''

    # nueva generacion de grid y actualizacion de paredes a puertas

    def generate_grid(self, grid_width, grid_height, cell_walls, exits):
        """
        Genera la estructura de la cuadrícula del juego basada en las paredes y salidas especificadas.

        Parámetros:
        - grid_width: Ancho de la cuadrícula.
        - grid_height: Altura de la cuadrícula.
        - cell_walls: Matriz que representa las paredes de cada celda en el grid.
        - exits: Lista de posiciones de salida.

        Retorna:
        - Una lista con dos diccionarios:
            1. grid_dict: Estructura de la cuadrícula con costos de movimiento.
            2. out_of_bounds_dict: Estructura de celdas fuera de los límites con costos de movimiento.
        """
        grid_dict = {}  # Diccionario para almacenar la estructura de la cuadrícula
        out_of_bounds_dict = {}  # Diccionario para almacenar las celdas fuera de los límites

        # Iterar sobre cada celda en la cuadrícula
        for i in range(grid_height):
            for j in range(grid_width):
                cell_key = (i+1, j+1)  # Clave de la celda actual
                walls = cell_walls[i][j]  # Paredes de la celda actual
                neighbors = []  # Lista para almacenar los vecinos y costos
                out_of_bounds_neighbor_list = []  # Lista para vecinos fuera de los límites

                # Verificar si hay un vecino arriba
                if i > 0:  # No es la primera fila
                    neighbors.append([(i, j+1), 5 if walls[0] == '1' else 1])  # Pared con costo 5 si existe, de lo contrario, 1
                else:
                    out_of_bounds_neighbor = (i, j+1)
                    if cell_key in exits:
                        print(f"Cell {cell_key} is connected to out-of-bounds exit at {out_of_bounds_neighbor} (UP)")
                        out_of_bounds_neighbor_list.append([(i, j+1), 2])  # Costo de 2 para salidas
                    else:
                        out_of_bounds_neighbor_list.append([(i, j+1), 5 if walls[0] == '1' else 1])  # Costo de pared

                # Verificar si hay un vecino a la izquierda
                if j > 0:  # No es la primera columna
                    neighbors.append([(i+1, j), 5 if walls[1] == '1' else 1])  # Pared con costo 5 si existe, de lo contrario, 1
                else:
                    out_of_bounds_neighbor = (i+1, j)
                    if cell_key in exits:
                        print(f"Cell {cell_key} is connected to out-of-bounds exit at {out_of_bounds_neighbor} (LEFT)")
                        out_of_bounds_neighbor_list.append([(i+1, j), 2])  # Costo de 2 para salidas
                    else:
                        out_of_bounds_neighbor_list.append([(i, j), 5 if walls[1] == '1' else 1])  # Costo de pared

                # Verificar si hay un vecino abajo
                if i < grid_height - 1:  # No es la última fila
                    neighbors.append([(i+2, j+1), 5 if walls[2] == '1' else 1])  # Pared con costo 5 si existe, de lo contrario, 1
                else:
                    out_of_bounds_neighbor = (i+2, j+1)
                    if cell_key in exits:
                        print(f"Cell {cell_key} is connected to out-of-bounds exit at {out_of_bounds_neighbor} (DOWN)")
                        out_of_bounds_neighbor_list.append([(i+2, j+1), 2])  # Costo de 2 para salidas
                    else:
                        out_of_bounds_neighbor_list.append([(i+2, j+1), 5 if walls[2] == '1' else 1])  # Costo de pared

                # Verificar si hay un vecino a la derecha
                if j < grid_width - 1:  # No es la última columna
                    neighbors.append([(i+1, j+2), 5 if walls[3] == '1' else 1])  # Pared con costo 5 si existe, de lo contrario, 1
                else:
                    out_of_bounds_neighbor = (i+1, j+2)
                    if cell_key in exits:
                        print(f"Cell {cell_key} is connected to out-of-bounds exit at {out_of_bounds_neighbor} (RIGHT)")
                        out_of_bounds_neighbor_list.append([(i+1, j+2), 2])  # Costo de 2 para salidas
                    else:
                        out_of_bounds_neighbor_list.append([(i+1, j+2), 5 if walls[3] == '1' else 1])  # Costo de pared

                grid_dict[cell_key] = neighbors  # Guardar los vecinos y costos en el diccionario
                out_of_bounds_dict[cell_key] = out_of_bounds_neighbor_list  # Guardar los vecinos fuera de límites en el diccionario

        return [grid_dict, out_of_bounds_dict]  # Retornar los diccionarios

    def update_walls_to_doors(self, grid_dict, door_pairs):
        """
        Actualiza las paredes en la estructura de la cuadrícula para reflejar las puertas.

        Parámetros:
        - grid_dict: Estructura de la cuadrícula con los costos actuales de las paredes.
        - door_pairs: Lista de pares de celdas que representan puertas.
        """
        for (cell1, cell2) in door_pairs:
            # Extraer coordenadas
            x1, y1 = cell1
            x2, y2 = cell2

            # Determinar la dirección de la pared y actualizarla a una puerta (valor 2)
            if x1 == x2:  # Misma fila, pared horizontal (izquierda-derecha)
                if y1 < y2:  # cell1 está a la izquierda de cell2
                    self.update_wall_value(grid_dict, (x1, y1), (x2, y2), 3, 1)  # Pared derecha de cell1, pared izquierda de cell2
                else:  # cell1 está a la derecha de cell2
                    self.update_wall_value(grid_dict, (x2, y2), (x1, y1), 3, 1)  # Pared derecha de cell2, pared izquierda de cell1
            elif y1 == y2:  # Misma columna, pared vertical (arriba-abajo)
                if x1 < x2:  # cell1 está arriba de cell2
                    self.update_wall_value(grid_dict, (x1, y1), (x2, y2), 2, 0)  # Pared inferior de cell1, pared superior de cell2
                else:  # cell1 está abajo de cell2
                    self.update_wall_value(grid_dict, (x2, y2), (x1, y1), 2, 0)  # Pared inferior de cell2, pared superior de cell1

    def update_wall_value(self, grid_dict, cell1, cell2, wall_index1, wall_index2):
        """
        Actualiza el valor de la pared a puerta entre dos celdas especificadas.

        Parámetros:
        - grid_dict: Estructura de la cuadrícula con los costos actuales de las paredes.
        - cell1: La primera celda.
        - cell2: La segunda celda.
        - wall_index1: Índice de la pared en cell1.
        - wall_index2: Índice de la pared en cell2.
        """
        # Convertir los valores actuales de la pared de 5 (pared) a 2 (puerta) entre cell1 y cell2
        for i, neighbor in enumerate(grid_dict[cell1]):
            if neighbor[0] == cell2 and neighbor[1] == 5:
                grid_dict[cell1][i][1] = 2  # Actualizar a puerta
        for i, neighbor in enumerate(grid_dict[cell2]):
            if neighbor[0] == cell1 and neighbor[1] == 5:
                grid_dict[cell2][i][1] = 2  # Actualizar a puerta

    def wall_in_direction(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> bool:
        """
        Verifica si hay una pared en la dirección especificada entre dos posiciones.

        Parámetros:
        - pos: Posición inicial.
        - new_pos: Posición final.

        Retorna:
        - True si hay una pared, False de lo contrario.
        """
        if pos not in self.grid_structure:
            print(f"Warning: Wall Position {pos} not found in grid_structure")
            return False

        return any(adj == new_pos and cost == 5 for adj, cost in self.grid_structure[pos])

    def door_in_direction(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> bool:
        """
        Verifica si hay una puerta en la dirección especificada entre dos posiciones.

        Parámetros:
        - pos: Posición inicial.
        - new_pos: Posición final.

        Retorna:
        - True si hay una puerta entre las posiciones, False de lo contrario.
        """
        if pos not in self.grid_structure:
            print(f"Warning: Door Position {pos} not found in grid_structure")
            return False

        # Verifica si el vecino en la posición new_pos tiene un costo de 2 (puerta)
        return any(adj == new_pos and cost == 2 for adj, cost in self.grid_structure[pos])

    def damage_wall(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> None:
        """
        Daña una pared entre dos posiciones especificadas y actualiza la estructura del grid si la pared se destruye.

        Parámetros:
        - pos: Posición inicial.
        - new_pos: Posición final.
        """
        if self.wall_in_direction(pos, new_pos):
            # Determina la clave de la pared en la estructura de salud de paredes
            wall_key = (pos, new_pos) if (pos, new_pos) in self.wall_health else (new_pos, pos)
            self.wall_health[wall_key] -= 1  # Disminuye la salud de la pared
            self.damage_markers += 1  # Incrementa el contador de daños

            # Verifica si la pared se ha destruido completamente
            if self.wall_health[wall_key] == 0:
                # La pared está destruida, actualiza la estructura para que sea un camino abierto
                self.update_connection_cost(pos, new_pos, 1)
                self.update_connection_cost(new_pos, pos, 1)
                del self.wall_health[wall_key]  # Elimina la pared de la estructura de salud
                print(f"Wall between {pos} and {new_pos} has been destroyed.")
            # else:
            #     print(f"Wall between {pos} and {new_pos} has been damaged. Health: {self.wall_health[wall_key]}")
        else:
            print(f"No wall found between {pos} and {new_pos}")

    def damage_door(self, pos: Tuple[int, int], new_pos: Tuple[int, int]) -> None:
        """
        Daño a una puerta entre dos posiciones especificadas y actualiza la estructura del grid si la puerta se abre.

        Parámetros:
        - pos: Posición inicial.
        - new_pos: Posición final.
        """
        if self.door_in_direction(pos, new_pos):
            # Actualiza la puerta para que sea un camino abierto (costo 1)
            self.update_connection_cost(pos, new_pos, 1)
            self.update_connection_cost(new_pos, pos, 1)
        else:
            print(f"No door found between {pos} and {new_pos}")

    def update_connection_cost(self, pos: Tuple[int, int], neighbor: Tuple[int, int], new_cost: int) -> None:
        """
        Actualiza el costo de conexión entre dos celdas en la estructura de la cuadrícula.

        Parámetros:
        - pos: Posición de la celda actual.
        - neighbor: Posición del vecino.
        - new_cost: Nuevo costo de conexión a asignar.
        """
        # Encuentra el vecino en la celda actual y actualiza el costo de conexión
        for i, (adj, cost) in enumerate(self.grid_structure[pos]):
            if adj == neighbor:
                self.grid_structure[pos][i] = (adj, new_cost)
                break

    '''Rerrolling, steps, and checking game over'''

    def check_game_over(self) -> None:
        """
        Verifica las condiciones de fin del juego y actualiza el estado del juego si se cumple alguna condición.

        Condiciones de fin del juego:
        - El número de marcadores de daño llega a 24.
        - Se pierden 4 víctimas.
        - Se rescatan 7 víctimas.
        - No quedan bomberos disponibles.

        Cambia el estado del juego a no en ejecución si alguna de las condiciones se cumple.
        """
        if self.damage_markers == 24:
            print("Game Over: Building has collapsed!")  # El edificio ha colapsado debido a daños excesivos
            self.running = False
        elif self.lost_victims == 4:
            print("Game Over: Too many victims lost!")  # Demasiadas víctimas han sido perdidas
            self.running = False
        elif self.rescued_victims == 7:
            print("Game Over: All victims accounted for!")  # Todas las víctimas han sido rescatadas
            self.running = False
        elif len(self.agents) == 0:
            print("Game Over: No more firefighters left!")  # No quedan bomberos para continuar
            self.running = False

    def step(self):
        """
        Avanza el juego un paso, ejecutando las acciones de los bomberos, el fuego y los puntos de interés.

        Llama a métodos para:
        - Avanzar el fuego.
        - Verificar bomberos y víctimas.
        - Re-rolar puntos de interés.
        - Ejecutar el paso del planificador de agentes.
        - Verificar condiciones de fin del juego.

        Retorna:
        - El estado actual del juego después de realizar el paso.
        """
        if self.running:
            self.advance_fire()  # Avanza el estado del fuego
            self.check_firefighters_and_victims(self.current_step)  # Verifica el estado de bomberos y víctimas
            self.reroll_pois()  # Re-rola los puntos de interés
            self.schedule.step()  # Avanza el planificador de agentes
            self.check_game_over()  # Verifica las condiciones de fin del juego
            self.current_step += 1  # Incrementa el contador de pasos del juego
            print(self.grid_structure)
        return self.get_game_state()  # Retorna el estado del juego

    def advance_fire(self) -> None:
        """
        Avanza el estado del fuego en el juego.

        - Rola para determinar la posición del nuevo humo.
        - Maneja la propagación del fuego (flashover).
        """
        fire_roll = (random.randint(1, 6), random.randint(1, 8))  # Genera una nueva posición para el humo
        self.place_smoke(fire_roll)  # Coloca humo en la nueva posición
        self.handle_flashover()  # Maneja la propagación del fuego

    def reroll_pois(self) -> None:
        """
        Re-rola los puntos de interés (POIs) en el tablero.

        - Añade nuevos POIs si hay menos de max_pois_onBoard.
        - Elimina fuego y humo de las posiciones de los nuevos POIs.
        """
        revealed_pois = sum(1 for poi in self.pois.values() if poi["revealed"])  # Cuenta los POIs revelados

        # Añade nuevos POIs si es necesario
        while len(self.pois) < self.max_pois_onBoard:
            poi_roll = (random.randint(1, 6), random.randint(1, 8))  # Genera una nueva posición para un POI
            poi_pos = poi_roll
            if poi_pos not in self.pois:
                self.add_victim(poi_pos)  # Añade una víctima en la nueva posición
                # Elimina fuego y humo de la posición del POI
                self.remove_fire_and_smoke(poi_pos)

    def reveal_poi(self, pos: Tuple[int, int]) -> bool:
        """
        Revela un punto de interés (POI) en la posición especificada.

        Parámetros:
        - pos: Posición del POI a revelar.

        Retorna:
        - True si el POI revelado es una víctima, False en caso contrario.
        """
        if pos in self.pois:
            poi_info = self.pois[pos]
            if not poi_info["revealed"]:
                poi_info["revealed"] = True  # Marca el POI como revelado
                if poi_info["is_victim"]:
                    print(f"A victim has been found at {pos}")  # Se ha encontrado una víctima en la posición
                else:
                    self.pois.pop(pos)  # Elimina el POI si no es una víctima
                return poi_info["is_victim"]
        return False

    '''Handling explosions smoke and fire'''

    def place_smoke(self, pos: Tuple[int, int]) -> None:
        """
        Coloca humo en la posición especificada y maneja la conversión de humo a fuego si es necesario.

        Parámetros:
        - pos: Posición donde colocar el humo.
        
        Comportamiento:
        - Si la posición ya tiene fuego, maneja la explosión.
        - Si la posición ya tiene humo, convierte el humo en fuego.
        - Si la posición está adyacente a un fuego, agrega fuego en la posición.
        - De lo contrario, simplemente coloca humo en la posición.
        """
        if pos in self.fire:
            self.handle_explosion(pos)  # Maneja la explosión si ya hay fuego en la posición
        elif pos in self.smoke:
            self.convert_smoke_to_fire(pos)  # Convierte el humo en fuego si ya hay humo en la posición
        else:
            adjacent_fire = any(self.is_adjacent(pos, fire_pos) for fire_pos in self.fire)
            if adjacent_fire:
                self.fire.add(pos)  # Coloca fuego si está adyacente a fuego existente
            else:
                self.smoke.add(pos)  # Coloca humo si no está adyacente a fuego

    def convert_smoke_to_fire(self, pos: Tuple[int, int]) -> None:
        """
        Convierte el humo en fuego en la posición especificada.

        Parámetros:
        - pos: Posición donde se convierte el humo en fuego.

        Comportamiento:
        - Elimina el humo de la posición.
        - Agrega fuego en la posición.
        - Si la posición tiene un POI, pierde la víctima en esa posición.
        """
        self.smoke.remove(pos)  # Elimina el humo
        self.fire.add(pos)  # Agrega fuego
        if pos in self.pois:
            self.lose_victim(pos)  # Pierde la víctima si hay una en la posición

    def handle_explosion(self, pos: Tuple[int, int]) -> None:
        """
        Maneja la explosión en la posición especificada y propaga el efecto de la explosión.

        Parámetros:
        - pos: Posición donde ocurre la explosión.
        
        Comportamiento:
        - Imprime un mensaje de explosión.
        - Propaga el efecto de la explosión en las cuatro direcciones (arriba, abajo, izquierda, derecha).
        - Maneja daños a paredes, puertas, y coloca fuego o convierte humo según corresponda.
        """
        print(f"Explosion at {pos}")  # Mensaje de explosión
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Direcciones de propagación
        for dx, dy in directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            if new_pos in self.grid_structure:  # Verifica si la nueva posición es válida
                if self.wall_in_direction(pos, new_pos):
                    self.damage_wall(pos, new_pos)  # Daño a la pared si hay una
                elif self.door_in_direction(pos, new_pos):
                    self.damage_door(pos, new_pos)  # Daño a la puerta si hay una
                elif new_pos in self.fire:
                    self.handle_shockwave(new_pos, (dx, dy))  # Maneja la onda de choque si hay fuego en la nueva posición
                else:
                    self.place_fire_or_flip_smoke(new_pos)  # Coloca fuego o convierte humo según corresponda

    def handle_shockwave(self, start_pos: Tuple[int, int], direction: Tuple[int, int]) -> None:
        """
        Maneja la onda de choque del fuego desde la posición de inicio en la dirección especificada.

        Parámetros:
        - start_pos: Posición de inicio de la onda de choque.
        - direction: Dirección en la que se propaga la onda de choque.

        Comportamiento:
        - Propaga el efecto de la onda de choque en la dirección especificada hasta que encuentre un límite.
        - Conviertiendo humo en fuego, dañando paredes o puertas según corresponda.
        """
        current_pos = start_pos
        while True:
            next_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
            if not self.is_valid_position(next_pos):
                break  # Sale del bucle si la posición no es válida
            
            if next_pos not in self.fire:
                if next_pos in self.smoke:
                    self.convert_smoke_to_fire(next_pos)  # Convierte el humo en fuego
                elif self.wall_in_direction(current_pos, next_pos):
                    self.damage_wall(current_pos, next_pos)  # Daño a la pared
                    break
                elif self.door_in_direction(current_pos, next_pos):
                    self.damage_door(current_pos, next_pos)  # Daño a la puerta
                    break
                else:
                    self.place_fire_or_flip_smoke(next_pos)  # Coloca fuego o convierte humo
                    break
            
            current_pos = next_pos  # Continúa con la siguiente posición

    def place_fire_or_flip_smoke(self, pos: Tuple[int, int]) -> None:
        """
        Coloca fuego en la posición especificada o convierte humo en fuego si ya hay humo en esa posición.

        Parámetros:
        - pos: Posición donde colocar fuego o convertir humo en fuego.
        
        Comportamiento:
        - Si la posición tiene humo, convierte el humo en fuego.
        - Si la posición no tiene humo, simplemente agrega fuego en esa posición.
        - Si hay un POI en la posición, pierde la víctima en esa posición.
        """
        if pos in self.smoke:
            self.convert_smoke_to_fire(pos)  # Convierte humo en fuego
        else:
            self.fire.add(pos)  # Agrega fuego
        
        if pos in self.pois:
            self.lose_victim(pos)  # Pierde la víctima si hay una en la posición

    def handle_flashover(self) -> None:
        """
        Maneja el fenómeno de flashover, donde el fuego se propaga de manera explosiva a todas las posiciones adyacentes al humo.

        Comportamiento:
        - Itera sobre las posiciones de humo y convierte el humo en fuego si alguna posición adyacente tiene fuego.
        - Continúa el proceso hasta que no haya cambios adicionales.
        """
        changed = True
        while changed:
            changed = False
            for smoke_pos in list(self.smoke):
                if any(self.is_adjacent(smoke_pos, fire_pos) for fire_pos in self.fire):
                    self.convert_smoke_to_fire(smoke_pos)  # Convierte humo a fuego
                    changed = True  # Marca que hubo un cambio

    def remove_fire_and_smoke(self, pos: Tuple[int, int]) -> None:
        """
        Elimina el fuego y el humo en la posición especificada.

        Parámetros:
        - pos: Posición donde eliminar el fuego y el humo.
        
        Comportamiento:
        - Si hay fuego en la posición, lo elimina.
        - Si hay humo en la posición, también lo elimina.
        """
        if pos in self.fire:
            self.fire.remove(pos)  # Elimina el fuego
        
        if pos in self.smoke:
            self.smoke.remove(pos)  # Elimina el humo

    '''Funcion para genera el json'''
    
    def return_json(self):
        print(f"Grid actual {self.grid_structure}")
        print("\n")
        print(f"Grid out of bounds {self.ouf_of_bounds_grid_structure}")
        print("\n")
        print(f"Paredes no derrumbadas y su salud: {self.wall_health}")
        print(f"Ubicacion del fuego: {self.fire}")
        print(f"Ubicacion del humo: {self.smoke}")
        print(f"Ubicacion de los pois: {self.pois}")
        for agent in range(len(self.agents)):
            print(f"Ubicacion de los agentes: {self.agents[agent].position}, esta cargando vicima: {self.agents[agent].carrying_victim}")

    def get_game_state(self):
        return {
            "step": self.current_step, # int
            "grid_structure": self.grid_structure, # dict
            "out_of_bounds_grid_structure": self.ouf_of_bounds_grid_structure, # dict
            "damage_markers": self.damage_markers, # int
            "rescued_victims": self.rescued_victims, # int
            "lost_victims": self.lost_victims, # int
            "running": self.running, # bool
            "agent_count": len(self.agents),  # int
            "fire_locations": list(self.fire), # list(iterable: Iterable[_T@list],/)
            "smoke_locations": self.smoke, # Set[Tuple[int, int]]
            "poi_locations": [{"position": pos, "revealed": info["revealed"]} for pos, info in self.pois.items()], # List[Dict[str, Union[Tuple[int, int], bool]]]
            "firefighter_positions": [{"id": agent.unique_id, "position": agent.position, "carrying_victim": agent.carrying_victim} for agent in self.agents if isinstance(agent, FirefighterAgent)] # List[Dict[str, Union[int, Tuple[int, int], bool]]]
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

# Example usage
if __name__ == "__main__":
    model = FlashPointModel(GRID_WIDTH,GRID_HEIGHT,wall_matrix,victims,fuego,puertas,entrada)
    i =0

    model.return_json()
    while model.running and  i < 100: 
        print(f"\n--- Step {i} ---")
        model.step()
        if i % 10 == 0:
            model.return_json()
            # visualize_grid_with_doors(GRID_WIDTH, GRID_HEIGHT, wall_matrix, model.grid_structure,i)
        i+=1
