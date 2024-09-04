using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class GameState
{
    public int step;
    public Dictionary<string, List<List<object>>> grid_structure;
    public Dictionary<string, List<List<object>>> out_of_bounds_grid_structure;
    public int damage_markers;
    public int rescued_victims;
    public int lost_victims;
    public bool running;
    public int agent_count;
    public List<List<int>> fire_locations;
    public List<List<int>> smoke_locations;
    public List<POI> poi_locations;
    public List<Firefighter> firefighter_positions;

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

// Auxiliary classes for the GameState
[Serializable]
public class POI
{
    public List<int> position;
    public bool revealed;
}

[Serializable]
public class Firefighter
{
    public int id;
    public List<int> position;
    public bool carrying_victim;
}
