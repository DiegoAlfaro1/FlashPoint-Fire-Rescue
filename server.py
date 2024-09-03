from flask import Flask, request, jsonify
from FlashPoint_Backend import FlashPointModel
from file_parser import parse_game_config

app = Flask(__name__)

# Global variable to store the current game state
current_game = None

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
        game_state = current_game.get_game_state()
        return jsonify(game_state), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve game state: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
