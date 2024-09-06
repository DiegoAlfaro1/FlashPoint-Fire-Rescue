using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

public class HTTPService : MonoBehaviour
{
    private const string serverUrl = "http://localhost:5000"; // Base URL for the server

    /// <summary>
    /// Sends a request to the server to start the game.
    /// </summary>
    /// <param name="callback">Callback to handle the server response.</param>
    public IEnumerator StartGame(Action<string> callback)
    {
        WWWForm form = new WWWForm();

        // Create a POST request to start the game
        using (UnityWebRequest www = UnityWebRequest.Post(serverUrl + "/start_game", form))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                // Log errors if the request fails
                Debug.LogError("Error while starting the game: " + www.error);
                Debug.LogError("Response Code: " + www.responseCode);
                Debug.LogError("Response Text: " + www.downloadHandler.text);
            }
            else
            {
                Debug.Log("The game has been correctly initiated: " + www.downloadHandler.text);
                callback?.Invoke(www.downloadHandler.text); // Invoke callback with the response text
            }
        }
    }

    /// <summary>
    /// Sends a request to the server to get the current game state.
    /// </summary>
    /// <param name="callback">Callback to handle the deserialized game state.</param>
    public IEnumerator GetGameState(Action<GameState> callback)
    {
        using (UnityWebRequest request = UnityWebRequest.Get(serverUrl + "/game_state"))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string jsonResponse = request.downloadHandler.text;

                if (!string.IsNullOrEmpty(jsonResponse))
                {
                    try
                    {
                        // Deserialize JSON response to GameState object
                        GameState gameState = JsonConvert.DeserializeObject<GameState>(jsonResponse);

                        if (gameState != null)
                        {
                            callback?.Invoke(gameState); // Invoke callback with the game state
                        }
                        else
                        {
                            Debug.LogError("Failed to parse the game state: The result is null.");
                        }
                    }
                    catch (JsonException e)
                    {
                        // Log errors if JSON parsing fails
                        Debug.LogError("Error while parsing the game state: " + e.Message);
                    }
                }
                else
                {
                    Debug.LogError("Empty response while trying to obtain the game state.");
                }
            }
            else
            {
                Debug.LogError("Error while obtaining the game state: " + request.error);
            }
        }
    }

    /// <summary>
    /// Sends a request to the server to advance a step in the simulation.
    /// </summary>
    /// <param name="callback">Callback to handle the server response.</param>
    public IEnumerator AdvanceStep(Action<string> callback)
    {
        WWWForm form = new WWWForm();

        // Create a POST request to advance a step in the game
        using (UnityWebRequest www = UnityWebRequest.Post(serverUrl + "/step", form))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                // Log errors if the request fails
                Debug.LogError("Error while advancing the game: " + www.error);
                Debug.LogError("Response Code: " + www.responseCode);
                Debug.LogError("Response Text: " + www.downloadHandler.text);
            }
            else
            {
                Debug.Log("The game has been correctly advanced: " + www.downloadHandler.text);
                callback?.Invoke(www.downloadHandler.text); // Invoke callback with the response text
            }
        }
    }
}
