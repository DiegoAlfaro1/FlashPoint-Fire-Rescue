using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System;

public class HTTPService : MonoBehaviour
{
    private const string serverUrl = "http://localhost:5000";

    // Method for starting the game
    public IEnumerator StartGame(string filePath, int nAgents, Action<string> callback)
    {
        // Create the JSON data for the request
        string jsonData = JsonUtility.ToJson(new
        {
            file_path = filePath,
            n_agents = nAgents
        });

        // Create the request
        // TODO: Evaluate if it's necessary to use PostWwwForm
        using (UnityWebRequest request = UnityWebRequest.Post(serverUrl + "/start_game", jsonData))
        {
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string responseText = request.downloadHandler.text;
                callback?.Invoke(responseText);
            }
            else
            {
                Debug.LogError("Error at initializing the game: " + request.error);
            }
        }
    }

    // Method for getting the game state
    public IEnumerator GetGameState(Action<GameState> callback)
    {
        using (UnityWebRequest request = UnityWebRequest.Get(serverUrl + "/game_state"))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string jsonResponse = request.downloadHandler.text;
                GameState gameState = JsonUtility.FromJson<GameState>(jsonResponse);
                callback?.Invoke(gameState);
            }
            else
            {
                Debug.LogError("Error at obtaining the game's state: " + request.error);
            }
        }
    }
}
