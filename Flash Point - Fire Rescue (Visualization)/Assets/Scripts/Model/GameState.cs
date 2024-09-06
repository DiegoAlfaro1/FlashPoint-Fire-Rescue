using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class GameState
{
    // Represents the current step in the simulation
    public int step;

    // Grid structures representing the game state and out-of-bounds areas
    public Dictionary<string, List<List<object>>> grid_structure;
    public Dictionary<string, List<List<object>>> out_of_bounds_grid_structure;

    // Game state variables for damage, rescued and lost victims, and the running state
    public int damage_markers;
    public int rescued_victims;
    public int lost_victims;
    public bool running;
    public int agent_count;

    // Lists to keep track of various game elements' locations
    public List<List<int>> fire_locations;
    public List<List<int>> smoke_locations;
    public List<POI> poi_locations;
    public List<Firefighter> firefighter_positions;

    /// <summary>
    /// Constructor to initialize the game state with empty data structures.
    /// </summary>
    public GameState()
    {
        // Initialize data structures
        grid_structure = new Dictionary<string, List<List<object>>>();
        out_of_bounds_grid_structure = new Dictionary<string, List<List<object>>>();
        fire_locations = new List<List<int>>();
        smoke_locations = new List<List<int>>();
        poi_locations = new List<POI>();
        firefighter_positions = new List<Firefighter>();
    }
}

// Auxiliary class representing a point of interest (POI) in the game
[Serializable]
public class POI
{
    public List<int> position;
    public bool revealed;
}

// Auxiliary class representing a firefighter in the game
[Serializable]
public class Firefighter
{
    public int id;
    public List<int> position;
    public bool carrying_victim;
}
