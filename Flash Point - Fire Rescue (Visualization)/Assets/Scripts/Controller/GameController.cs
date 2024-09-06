using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class GameController : MonoBehaviour
{
    private GameState currentGameState;
    private HTTPService httpService;

    // References to the containers for the generated elements
    public WallAndDoorGenerator wallAndDoorGenerator;
    public GameElementsGenerator gameElementsGenerator;
    public FirefighterGenerator firefighterGenerator;

    // References to UI text elements
    public TMP_Text damageMarkersText;
    public TMP_Text savedVictimsText;
    public TMP_Text deadVictimsText;

    void Start()
    {
        // Initialize HTTPService and start the game without parameters
        httpService = GetComponent<HTTPService>();
        StartCoroutine(httpService.StartGame(OnGameStarted));
    }

    /// <summary>
    /// Callback for handling the response when the game is started.
    /// </summary>
    /// <param name="response">Server response after game starts.</param>
    private void OnGameStarted(string response)
    {
        Debug.Log("Game Started: " + response);
        
        // Obtain the game state after the game has started
        StartCoroutine(httpService.GetGameState(OnGameStateReceived));
    }

    /// <summary>
    /// Callback for processing the received game state from the server.
    /// </summary>
    /// <param name="gameState">Current state of the game.</param>
    private void OnGameStateReceived(GameState gameState)
    {
        currentGameState = gameState;
        Debug.Log("Updated State Of The Game.");

        // Clear previously generated elements before generating new ones
        ClearGeneratedElements();

        // Process wall and door grid structure
        if (wallAndDoorGenerator != null && currentGameState.grid_structure != null)
        {
            wallAndDoorGenerator.ProcessGridStructure(currentGameState.grid_structure);
        }

        // Generate game elements such as POIs, fire, smoke, and firefighters
        if (currentGameState.poi_locations != null)
        {
            gameElementsGenerator.GeneratePOIs(currentGameState.poi_locations);
        }

        if (currentGameState.fire_locations != null)
        {
            gameElementsGenerator.GenerateFire(currentGameState.fire_locations);
        }

        if (currentGameState.smoke_locations != null)
        {
            gameElementsGenerator.GenerateSmoke(currentGameState.smoke_locations);
        }

        if (currentGameState.firefighter_positions != null)
        {
            firefighterGenerator.GenerateFirefighters(currentGameState.firefighter_positions);
        }

        // Continue advancing the simulation if the game is running
        if (currentGameState.running)
        {
            StartCoroutine(AdvanceSimulationStep());
        }

        // Update the game UI elements
        UpdateUI();
    }

    /// <summary>
    /// Clears all generated elements from the scene.
    /// </summary>
    private void ClearGeneratedElements()
    {
        // Clear children objects from each generator while keeping the generators themselves intact
        ClearChildren(wallAndDoorGenerator.transform);
        ClearChildren(gameElementsGenerator.transform);
        ClearChildren(firefighterGenerator.transform);
    }

    /// <summary>
    /// Helper method to clear all child objects of a specified parent.
    /// </summary>
    /// <param name="parent">The parent Transform to clear.</param>
    private void ClearChildren(Transform parent)
    {
        if (parent != null)
        {
            foreach (Transform child in parent)
            {
                Destroy(child.gameObject);
            }
        }
    }

    /// <summary>
    /// Coroutine to automatically advance the simulation steps at set intervals.
    /// </summary>
    private IEnumerator AdvanceSimulationStep()
    {
        while (currentGameState.running)
        {
            yield return new WaitForSeconds(10f); // Wait 10 seconds between steps

            Debug.Log("Advancing simulation step...");

            // Make a request to advance one step in the game
            yield return StartCoroutine(httpService.AdvanceStep(OnStepAdvanced));
        }

        Debug.Log("Simulation ended.");
    }

    /// <summary>
    /// Callback for handling the response after advancing a simulation step.
    /// </summary>
    /// <param name="response">Server response after advancing a step.</param>
    private void OnStepAdvanced(string response)
    {
        Debug.Log("Step advanced: " + response);
        
        // Retrieve the new game state after advancing a step
        StartCoroutine(httpService.GetGameState(OnGameStateReceived));
    }

    /// <summary>
    /// Updates the UI elements to reflect the current game state.
    /// </summary>
    private void UpdateUI()
    {
        if (currentGameState != null)
        {
            damageMarkersText.text = "Damage Markers: " + currentGameState.damage_markers;
            savedVictimsText.text = "Saved Victims: " + currentGameState.rescued_victims;
            deadVictimsText.text = "Dead Victims: " + currentGameState.lost_victims;
        }
    }
}
