using System.Collections;
using UnityEngine;

public class GameController : MonoBehaviour
{
    private GameState currentGameState;
    private HTTPService httpService;

    void Start()
    {
        httpService = GetComponent<HTTPService>();

        // Start the game
        StartCoroutine(httpService.StartGame("input.txt", 6, OnGameStarted));
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
        // TODO: Add the logic to use the procedural generation of the game state
    }
}
