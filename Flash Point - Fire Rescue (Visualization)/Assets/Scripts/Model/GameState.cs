using System.Collections.Generic;
using UnityEngine;

public class GameState
{
    public int Step { get; set; }
    public List<List<int>> GridStructure { get; set; }
    public List<List<int>> OutOfBoundsGridStructure { get; set; }
    public int DamageMarkers { get; set; }
    public int RescuedVictims { get; set; }
    public int LostVictims { get; set; }
    public bool Running { get; set; }
    public int AgentCount { get; set; }
    public List<Vector2> FireLocations { get; set; }
    public List<Vector2> SmokeLocations { get; set; }
    public List<POI> PoiLocations { get; set; }
    public List<Firefighter> FirefighterPositions { get; set; }

    public GameState()
    {
        GridStructure = new List<List<int>>();
        OutOfBoundsGridStructure = new List<List<int>>();
        FireLocations = new List<Vector2>();
        SmokeLocations = new List<Vector2>();
        PoiLocations = new List<POI>();
        FirefighterPositions = new List<Firefighter>();
    }
}

// Auxiliar Classes for Other Game Objects
public class POI
{
    public Vector2 Position { get; set; }
    public bool Revealed { get; set; }
}

public class Firefighter
{
    public int Id { get; set; }
    public Vector2 Position { get; set; }
    public bool CarryingVictim { get; set; }
}
