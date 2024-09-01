from flask import Flask, request, jsonify
from FlashPoint_Backend import FlashPointModel
from file_parser import parse_game_config  # Assuming we save the parser in file_parser.py
import json

app = Flask(__name__)

# Global variable to store the current game state
current_game = None

@app.route('/start_game', methods=['POST'])
def start_game():
    global current_game
    data = request.json
    
    # Get the file path from the request
    file_path = data.get('file_path')
    if not file_path:
        return jsonify({"error": "File path not provided"}), 400
    
    try:
        # Parse the game configuration from the file
        config = parse_game_config(file_path)
        
        # Extract parameters from the config
        width = 8  # Assuming fixed width
        height = 6  # Assuming fixed height
        wall_matrix = config['wall_matrix']
        victims = config['victims']
        fire = config['fire']
        doors = config['doors']
        exits = config['exits']
        n_agents = data.get('n_agents', 6)  # Get n_agents from request or use default
        
        # Initialize the game
        current_game = FlashPointModel(width, height, wall_matrix, victims, fire, doors, exits, n_agents)
        
        return jsonify({"message": "Game started successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to start game: {str(e)}"}), 500

@app.route('/step', methods=['GET'])
def step():
    global current_game
    if current_game is None:
        return jsonify({"error": "No game in progress"}), 400
    
    game_state = current_game.step()
    
    return jsonify(game_state), 200

@app.route('/game_state', methods=['GET'])
def game_state():
    global current_game
    if current_game is None:
        return jsonify({"error": "No game in progress"}), 400
    
    return jsonify(current_game.get_game_state()), 200

if __name__ == '__main__':
    app.run(debug=True)