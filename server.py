from flask import Flask, request, jsonify
from FlashPoint_Backend import FlashPointModel
from file_parser import parse_game_config

app = Flask(__name__)

# Global variable to store the current game state
current_game = None

def convert_to_json_compatible(obj):
    # Converts complex Python data types to JSON-compatible types.
    if isinstance(obj, dict):
        # Convert all keys to strings and recursively apply conversion to values
        return {str(k): convert_to_json_compatible(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        # Convert tuples and sets to lists and recursively apply conversion
        return [convert_to_json_compatible(i) for i in obj]
    elif isinstance(obj, (int, float, str, bool)):
        # Return primitive compatible data types as is
        return obj
    else:
        # For any other non-compatible object type, convert to string
        return str(obj)

@app.route('/start_game', methods=['POST'])
def start_game():
    global current_game
    
    # Direct path to the input file
    file_path = 'input.txt'
    
    try:
        config = parse_game_config(file_path)
        width = 8
        height = 6
        wall_matrix = config['wall_matrix']
        victims = config['victims']
        print(f"victims: {victims}")
        fire = config['fire']
        print(f"fire: {fire}")
        doors = config['doors']
        print(f"doors: {doors}")
        exits = config['exits']
        print(f"exits: {exits}")
        n_agents = 6
        
        current_game = FlashPointModel(width, height, wall_matrix, victims, fire, doors, exits, n_agents)
        return jsonify({"message": "Game started successfully"}), 200
    except FileNotFoundError:
        return jsonify({"error": f"Config file not found: {file_path}"}), 404
    except KeyError as e:
        return jsonify({"error": f"Missing required config key: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to start game: {str(e)}"}), 500

@app.route('/step', methods=['POST'])
def step():
    global current_game
    if current_game is None:
        return jsonify({"error": "No game in progress"}), 400
    
    try:
        current_game.step()
        return jsonify({"message": "Simulation advanced by one step"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to perform step: {str(e)}"}), 500

@app.route('/game_state', methods=['GET'])
def game_state():
    global current_game
    if current_game is None:
        return jsonify({"error": "No game in progress"}), 400
    
    try:
        # Get the game state
        game_state = current_game.get_game_state()
        # Convert complex data types to JSON-compatible types
        game_state_json_compatible = convert_to_json_compatible(game_state)
        # Return the converted game state
        return jsonify(game_state_json_compatible), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve game state: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
