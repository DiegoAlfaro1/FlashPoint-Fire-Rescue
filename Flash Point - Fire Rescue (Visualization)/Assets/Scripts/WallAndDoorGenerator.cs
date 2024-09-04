using System.Collections.Generic;
using UnityEngine;

public class WallAndDoorGenerator : MonoBehaviour
{
    public GameObject wallPrefab;
    public GameObject doorPrefab;
    public float gridSpacing = 1f;
    public Vector3 gridOrigin = Vector3.zero;

    public void ProcessGridStructure(Dictionary<string, List<List<object>>> gridStructure)
    {
        foreach (var cellEntry in gridStructure)
        {
            string cellKey = cellEntry.Key;
            List<List<object>> neighbors = cellEntry.Value;

            Debug.Log($"Processing cell {cellKey}");

            // Iterate through the list of neighbors for each cell
            for (int i = 0; i < neighbors.Count; i++)
            {
                List<object> neighborInfo = neighbors[i];

                if (neighborInfo.Count == 2)
                {
                    List<object> position = neighborInfo[0] as List<object>;
                    int connectionType = (int)(long)neighborInfo[1]; // Convert to integer

                    // Determine the direction based on the index
                    string direction = GetDirection(gridStructure, cellKey, i);

                    Debug.Log($"Cell {cellKey} has a neighbor in direction {direction} with connection type: {connectionType}");

                    // Instantiate objects according to the connection type
                    if (connectionType == 5)
                    {
                        Debug.Log($"Instantiate a wall towards {direction}.");
                        InstantiateObject(cellKey, direction, "Wall");
                    }
                    else if (connectionType == 2)
                    {
                        Debug.Log($"Instantiate a door towards {direction}.");
                        InstantiateObject(cellKey, direction, "Door");
                    }
                }
                else
                {
                    Debug.LogError("Neighbor information is invalid or does not contain 2 elements.");
                }
            }
        }
    }

    // Method to determine the direction based on the cell, index, and grid structure
    string GetDirection(Dictionary<string, List<List<object>>> gridStructure, string cellKey, int index)
    {
        // Get the position of the current cell
        string[] parts = cellKey.Trim('(', ')').Split(',');
        int x = int.Parse(parts[0].Trim());
        int y = int.Parse(parts[1].Trim());

        // Determine the direction based on the index and cell position
        int totalRows = gridStructure.Count; // Total number of rows
        int totalColumns = gridStructure[cellKey].Count; // Total number of columns

        if (index == 0) return (x == 1) ? "down" : "up";
        else if (index == 1) return (y == 1) ? "right" : "left";
        else if (index == 2) return (x == totalRows) ? "up" : "down";
        else if (index == 3) return (y == totalColumns) ? "left" : "right";

        return "";
    }

    // Method to instantiate an object (wall or door)
    GameObject InstantiateObject(string cellPositionKey, string direction, string type)
    {
        Vector3 objectPosition = CalculatePosition(cellPositionKey, direction);
        
        // Determine the object's rotation based on the direction
        Quaternion rotation;
        if (direction == "right" || direction == "left")
        {
            rotation = Quaternion.Euler(0, 90, 0); // Rotation for horizontal walls
        }
        else
        {
            rotation = Quaternion.identity; // No additional rotation for vertical walls
        }

        // Select the appropriate prefab
        GameObject prefab = type == "Wall" ? wallPrefab : doorPrefab;
        if (prefab == null) return null;

        // Instantiate the object with the calculated position and rotation
        GameObject instance = Instantiate(prefab, objectPosition, rotation);
        instance.transform.parent = this.transform;
        return instance;
    }

    // Method to calculate the object's position based on the cell and direction
    private Vector3 CalculatePosition(string cellPositionKey, string direction)
    {
        // Convert cell position from string to Vector2Int
        string[] positionParts = cellPositionKey.Trim('(', ')').Split(',');
        int cellX = int.Parse(positionParts[0].Trim());
        int cellZ = int.Parse(positionParts[1].Trim());

        // Calculate the base position of the cell in 3D space
        float x = (cellX - 1) * gridSpacing; // -1 because cells start from 1
        float z = (cellZ - 1) * gridSpacing; // -1 because cells start from 1
        float y = 0.5f; // Raise the object 0.5 units above the ground

        // Adjust coordinates according to the direction
        switch (direction)
        {
            case "right":
                x += gridSpacing / 2; // Adjustment to the right
                break;
            case "left":
                x -= gridSpacing / 2; // Adjustment to the left
                break;
            case "up":
                z += gridSpacing / 2; // Adjustment upwards
                break;
            case "down":
                z -= gridSpacing / 2; // Adjustment downwards
                break;
        }

        // Return the calculated position
        return new Vector3(x, y, z);
    }
}
