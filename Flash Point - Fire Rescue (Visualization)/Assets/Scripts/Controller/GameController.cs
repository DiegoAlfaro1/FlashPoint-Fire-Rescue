using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameController : MonoBehaviour
{
    private GameState currentGameState;
    private HTTPService httpService;

    void Start()
    {
        httpService = GetComponent<HTTPService>();

        // Start the game without parameters
        StartCoroutine(httpService.StartGame(OnGameStarted));
    }

    private void OnGameStarted(string response)
    {
        Debug.Log("Game Started: " + response);
        
        // Obtain the game state after the game has started
        StartCoroutine(httpService.GetGameState(OnGameStateReceived));
    }

    private void OnGameStateReceived(GameState gameState)
    {
        currentGameState = gameState;
        Debug.Log("Updated State Of The Game.");

        // Mostrar datos del estado del juego
        Debug.Log($"Step: {currentGameState.step}");
        Debug.Log($"Damage Markers: {currentGameState.damage_markers}");
        Debug.Log($"Rescued Victims: {currentGameState.rescued_victims}");
        Debug.Log($"Lost Victims: {currentGameState.lost_victims}");
        Debug.Log($"Running: {currentGameState.running}");
        Debug.Log($"Agent Count: {currentGameState.agent_count}");

        // Mostrar grid structures
        Debug.Log("Grid Structure:");
        foreach (var entry in currentGameState.grid_structure)
        {
            Debug.Log($"Cell {entry.Key}:");
            foreach (var list in entry.Value)
            {
                foreach (var item in list)
                {
                    if (item is List<object> sublist)
                    {
                        Debug.Log($"  - Sublist: [{string.Join(", ", sublist)}]");
                    }
                    else
                    {
                        Debug.Log($"  - Value: {item}");
                    }
                }
            }
        }

        Debug.Log("Out of Bounds Grid Structure:");
        foreach (var entry in currentGameState.out_of_bounds_grid_structure)
        {
            Debug.Log($"Out of Bounds Cell {entry.Key}:");
            foreach (var list in entry.Value)
            {
                foreach (var item in list)
                {
                    if (item is List<object> sublist)
                    {
                        Debug.Log($"  - Sublist: [{string.Join(", ", sublist)}]");
                    }
                    else
                    {
                        Debug.Log($"  - Value: {item}");
                    }
                }
            }
        }

        // Mostrar ubicaciones de fuego y humo
        Debug.Log("Fire Locations:");
        foreach (var location in currentGameState.fire_locations)
        {
            Debug.Log($" - [{string.Join(", ", location)}]");
        }

        Debug.Log("Smoke Locations:");
        foreach (var location in currentGameState.smoke_locations)
        {
            Debug.Log($" - [{string.Join(", ", location)}]");
        }

        // Mostrar POIs
        Debug.Log("POI Locations:");
        foreach (var poi in currentGameState.poi_locations)
        {
            Debug.Log($" - Position: [{string.Join(", ", poi.position)}], Revealed: {poi.revealed}");
        }

        // Mostrar posiciones de bomberos
        Debug.Log("Firefighter Positions:");
        foreach (var firefighter in currentGameState.firefighter_positions)
        {
            Debug.Log($" - ID: {firefighter.id}, Position: [{string.Join(", ", firefighter.position)}], Carrying Victim: {firefighter.carrying_victim}");
        }
    }

}
