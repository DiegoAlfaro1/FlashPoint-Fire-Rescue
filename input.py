
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

# print(f"pois: {pois}")


print(f"wall_matrix: {wall_matrix}")
print(f"victims: {victims}")
print(f"fuego: {fuego}")
print(f"puertas: {puertas}")
print(f"entrada: {entrada}")




