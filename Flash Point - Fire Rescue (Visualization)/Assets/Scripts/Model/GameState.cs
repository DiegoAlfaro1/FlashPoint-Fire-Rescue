using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class GameState
{
    public int step;
    public Dictionary<string, List<List<Vector2>>> grid_structure;
    public Dictionary<string, List<List<Vector2>>> out_of_bounds_grid_structure;
    public int damage_markers;
    public int rescued_victims;
    public int lost_victims;
    public bool running;
    public int agent_count;
    public List<Vector2> fire_locations;
    public List<Vector2> smoke_locations;
    public List<POI> poi_locations;
    public List<Firefighter> firefighter_positions;

    public GameState()
    {
        // Initialize the data structures
        grid_structure = new Dictionary<string, List<List<Vector2>>>();
        out_of_bounds_grid_structure = new Dictionary<string, List<List<Vector2>>>();
        fire_locations = new List<Vector2>();
        smoke_locations = new List<Vector2>();
        poi_locations = new List<POI>();
        firefighter_positions = new List<Firefighter>();
    }
}

// Auxiliary classes for the GameState
[Serializable]
public class POI
{
    public Vector2 position;
    public bool revealed;
}

[Serializable]
public class Firefighter
{
    public int id;
    public Vector2 position;
    public bool carrying_victim;
}
