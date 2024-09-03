using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json; // Lifesaver for handling JSON data

public class HTTPService : MonoBehaviour
{
    private const string serverUrl = "http://localhost:5000";

    // Method for starting the game
    public IEnumerator StartGame(Action<string> callback)
    {
        WWWForm form = new WWWForm();

        // Create a simple POST request to start the game
        using (UnityWebRequest www = UnityWebRequest.Post(serverUrl + "/start_game", form))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Error while starting the game: " + www.error);
                Debug.LogError("Response Code: " + www.responseCode);
                Debug.LogError("Response Text: " + www.downloadHandler.text);
            }
            else
            {
                Debug.Log("The game has been correctly initiated: " + www.downloadHandler.text);
                callback?.Invoke(www.downloadHandler.text);
            }
        }
    }

    // Method for getting the game state
    public IEnumerator GetGameState(System.Action<GameState> callback)
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
                        // Use Json.NET to deserialize directly to GameState
                        GameState gameState = JsonConvert.DeserializeObject<GameState>(jsonResponse);
                        callback?.Invoke(gameState);
                    }
                    catch (JsonException e)
                    {
                        Debug.LogError("Error while parsing the game state: " + e.Message);
                    }
                }
                else
                {
                    Debug.LogError("Empty response while trying to get the game state.");
                }
            }
            else
            {
                Debug.LogError("Error while obtaining the game state: " + request.error);
            }
        }
    }

    // Method for advancing a step in the simulation
    public IEnumerator AdvanceStep(Action<String> callback)
    {
        WWWForm form = new WWWForm();

        // Create a simple POST request to start the game
        using (UnityWebRequest www = UnityWebRequest.Post(serverUrl + "/step", form))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Error while starting the game: " + www.error);
                Debug.LogError("Response Code: " + www.responseCode);
                Debug.LogError("Response Text: " + www.downloadHandler.text);
            }
            else
            {
                Debug.Log("The game has been correctly advanced: " + www.downloadHandler.text);
                callback?.Invoke(www.downloadHandler.text);
            }
        }
    }
}
