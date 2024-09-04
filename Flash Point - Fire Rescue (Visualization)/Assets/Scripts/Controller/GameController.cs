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

        // Obtener el componente WallAndDoorGenerator
        WallAndDoorGenerator wallAndDoorGenerator = GetComponent<WallAndDoorGenerator>();
        
        // Verificar si se encontró el componente
        if (wallAndDoorGenerator == null)
        {
            Debug.LogError("WallAndDoorGenerator component not found on the GameObject.");
            return;
        }

        // Verificar si grid_structure no es nulo
        if (currentGameState.grid_structure == null)
        {
            Debug.LogError("grid_structure is null.");
            return;
        }

        // Llamar al método para procesar la estructura de la cuadrícula
        wallAndDoorGenerator.ProcessGridStructure(currentGameState.grid_structure);
    }


}
