def parse_game_config(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
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
    
    #C:/Users/die_g/OneDrive/desktop/Multiagentes/FlashPoint-Fire-Rescue/input.txt

    '''
        curl -X POST http://localhost:5000/start_game \
    -H "Content-Type: application/json" \
    -d '{
    "file_path": "input.txt",
    "n_agents": 6
    }'

    '''


    return {
        'wall_matrix': wall_matrix,
        'victims': victims,
        'fire': fuego,
        'doors': puertas,
        'exits': entrada
    }


