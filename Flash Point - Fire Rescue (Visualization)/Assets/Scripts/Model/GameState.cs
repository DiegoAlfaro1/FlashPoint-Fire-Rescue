using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class GameState
{
    public int Step;
    public List<List<int>> GridStructure;
    public List<List<int>> OutOfBoundsGridStructure;
    public int DamageMarkers;
    public int RescuedVictims;
    public int LostVictims;
    public bool Running;
    public int AgentCount;
    public List<Vector2> FireLocations;
    public List<Vector2> SmokeLocations;
    public List<POI> PoiLocations;
    public List<Firefighter> FirefighterPositions;

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

[Serializable]
public class POI
{
    public Vector2 Position;
    public bool Revealed;
}

[Serializable]
public class Firefighter
{
    public int Id;
    public Vector2 Position;
    public bool CarryingVictim;
}
