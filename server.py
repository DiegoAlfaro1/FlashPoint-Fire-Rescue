from flask import Flask, request, jsonify
from FlashPoint_Backend import FlashPointModel
from file_parser import parse_game_config

app = Flask(__name__)

# Global variable to store the current game state
current_game = None

def convert_to_json_serializable(obj):
    if isinstance(obj, (set, tuple)):
        return list(obj)
    elif isinstance(obj, dict):
        return {str(key) if isinstance(key, tuple) else key: convert_to_json_serializable(value)
                for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj

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
        fire = config['fire']
        doors = config['doors']
        exits = config['exits']
        n_agents = 6
        
        current_game = FlashPointModel(width, height, wall_matrix, victims, fire, doors, exits, n_agents)
        return jsonify({"message": "Game started successfully"}), 200
    except FileNotFoundError:
        return jsonify({"error": f"Config file not found: {file_path}"}), 404
    except KeyError as e:
        return jsonify({"error": f"Missing required config key: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to start game: {str(e)}"}), 500

@app.route('/step', methods=['GET'])
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
        game_state = current_game.get_game_state()
        # Convert specific elements that might need special handling
        serializable_state = {
            "step": game_state["step"],
            "grid_structure": convert_to_json_serializable(game_state["grid_structure"]),
            "out_of_bounds_grid_structure": convert_to_json_serializable(game_state["out_of_bounds_grid_structure"]),
            "damage_markers": convert_to_json_serializable(game_state["damage_markers"]),
            "rescued_victims": game_state["rescued_victims"],
            "lost_victims": game_state["lost_victims"],
            "running": game_state["running"],
            "agent_count": game_state["agent_count"],
            "fire_locations": game_state["fire_locations"],
            "smoke_locations": convert_to_json_serializable(game_state["smoke_locations"]),
            "poi_locations": game_state["poi_locations"],
            "firefighter_positions": game_state["firefighter_positions"]
        }
        return jsonify(serializable_state), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve game state: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
