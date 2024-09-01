def parse_game_config(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    wall_matrix = [line.strip().split() for line in lines[:6]]
    
    victims = []
    fire = []
    doors = []
    exits = []
    
    current_section = 'victims'
    for line in lines[6:]:
        parts = line.strip().split()
        if len(parts) == 3 and current_section == 'victims':
            x, y, v_type = parts
            victims.append(((int(x), int(y)), v_type == 'v'))
        elif len(parts) == 2 and current_section == 'fire':
            x, y = map(int, parts)
            fire.append((x, y))
        elif len(parts) == 4 and current_section == 'doors':
            x1, y1, x2, y2 = map(int, parts)
            doors.append(((x1, y1), (x2, y2)))
        elif len(parts) == 2 and current_section == 'exits':
            x, y = map(int, parts)
            exits.append((x, y))
        elif len(parts) == 2:
            current_section = 'fire' if current_section == 'victims' else 'doors' if current_section == 'fire' else 'exits'
            x, y = map(int, parts)
            if current_section == 'fire':
                fire.append((x, y))
    
    #C:/Users/die_g/OneDrive/desktop/Multiagentes/FlashPoint-Fire-Rescue/input.txt

    return {
        'wall_matrix': wall_matrix,
        'victims': victims,
        'fire': fire,
        'doors': doors,
        'exits': exits
    }