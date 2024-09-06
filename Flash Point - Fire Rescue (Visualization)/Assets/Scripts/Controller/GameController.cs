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

        // Clean the scene before generating the new game state
        ClearGeneratedElements();

        if (wallAndDoorGenerator != null && currentGameState.grid_structure != null)
        {
            wallAndDoorGenerator.ProcessGridStructure(currentGameState.grid_structure);
        }

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

        // Advances the corutine to the next step if the game is running
        if (currentGameState.running)
        {
            StartCoroutine(AdvanceSimulationStep());
        }

        // Update the UI
        UpdateUI();

    }

    // Method to clear a container of all its children
    private void ClearGeneratedElements()
    {
        // Limpiar los hijos de los generadores, sin eliminar los propios generadores
        ClearChildren(wallAndDoorGenerator.transform);
        ClearChildren(gameElementsGenerator.transform);
        ClearChildren(firefighterGenerator.transform);
    }

    // Auxiliar method to clear all the children of a container
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

    // Coroutine to automatically advance the simulation steps
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

    // Callback for handling the response after a step is advanced
    private void OnStepAdvanced(string response)
    {
        Debug.Log("Step advanced: " + response);
        
        // Retrieve the new game state after advancing a step
        StartCoroutine(httpService.GetGameState(OnGameStateReceived));
    }

    // Method to update the UI
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
