using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System;

public class HTTPService : MonoBehaviour
{
    private const string serverUrl = "http://localhost:5000";

    // Method for starting the game
    public IEnumerator StartGame(string filePath, int numAgents, System.Action<string> callback)
    {
        // Creates a WWWForm to build the POST request
        WWWForm form = new WWWForm();
        form.AddField("filePath", filePath);
        form.AddField("numAgents", numAgents);

        // Crea la solicitud POST usando UnityWebRequest.PostWwwForm
        using (UnityWebRequest www = UnityWebRequest.Post(serverUrl + "/start_game", form))
        {
            Debug.Log(www.url);
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Error at initializing the game: " + www.error);
                Debug.LogError("Response Code: " + www.responseCode);
                Debug.LogError("Response Text: " + www.downloadHandler.text);
            }
            else
            {
                Debug.Log("Game started successfully: " + www.downloadHandler.text);
                callback?.Invoke(www.downloadHandler.text);
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
