using System.Collections.Generic;
using UnityEngine;

public class WallAndDoorGenerator : MonoBehaviour
{
    public GameObject wallPrefab;
    public GameObject doorPrefab;
    public float gridSpacing = 1f;
    public Vector3 gridOrigin = Vector3.zero;
    
    public int innerGridX = 8;
    public int innerGridZ = 6;

    private int totalGridX;
    private int totalGridZ;

    public void Start()
    {
        totalGridX = innerGridX + 2;
        totalGridZ = innerGridZ + 2;
    }

    public void ProcessGridStructure(Dictionary<string, List<List<object>>> gridStructure)
    {
        int counterX = 1;
        int counterZ = 1;

        for (int z = totalGridZ - 2; z > 0; z--)
        {
            counterX = 1;

            for (int x = 1; x < totalGridX - 1; x++)
            {
                string cellKey = $"({counterZ}, {counterX})";

                if (gridStructure.ContainsKey(cellKey))
                {
                    List<List<object>> neighbors = gridStructure[cellKey];
                    Debug.Log($"Processing cell {cellKey} with {neighbors.Count} neighbors.");

                    int expectedNeighbors = 4;
                    List<string> validDirections = new List<string> { "up", "left", "down", "right" };

                    if (counterX == 1)
                    {
                        expectedNeighbors--;
                        validDirections.Remove("left");
                    }
                    if (counterX == innerGridX)
                    {
                        expectedNeighbors--;
                        validDirections.Remove("right");
                    }
                    if (counterZ == 1)
                    {
                        expectedNeighbors--;
                        validDirections.Remove("up");
                    }
                    if (counterZ == innerGridZ)
                    {
                        expectedNeighbors--;
                        validDirections.Remove("down");
                    }

                    if (neighbors.Count != expectedNeighbors)
                    {
                        Debug.LogWarning($"Cell {cellKey} has {neighbors.Count} neighbors, but {expectedNeighbors} expected.");
                        continue;
                    }

                    for (int i = 0; i < neighbors.Count; i++)
                    {
                        List<object> neighborInfo = neighbors[i];

                        if (neighborInfo.Count == 2)
                        {
                            int connectionType = (int)(long)neighborInfo[1];
                            string direction = validDirections[i];

                            Debug.Log($"Cell {cellKey} has neighbor in direction {direction} with connection type: {connectionType}");

                            // Determine object type and calculate position accordingly
                            if (connectionType == 5)
                            {
                                Vector3 objectPosition = CalculatePosition(counterX, counterZ, direction, "Wall");
                                Quaternion rotation = (direction == "left" || direction == "right") ? Quaternion.Euler(0, 90, 0) : Quaternion.identity;
                                InstantiateObject(objectPosition, rotation, wallPrefab);
                            }
                            else if (connectionType == 2)
                            {
                                Vector3 objectPosition = CalculatePosition(counterX, counterZ, direction, "Door");
                                Quaternion rotation = (direction == "left" || direction == "right") ? Quaternion.Euler(0, 90, 0) : Quaternion.identity;
                                InstantiateObject(objectPosition, rotation, doorPrefab);
                            }
                        }
                    }
                }
                else
                {
                    Debug.LogWarning($"Cell {cellKey} not found in gridStructure.");
                }

                counterX++;
            }

            counterZ++;
        }
    }

    private void InstantiateObject(Vector3 position, Quaternion rotation, GameObject prefab)
    {
        if (prefab == null)
        {
            Debug.LogError("Prefab is null, cannot instantiate.");
            return;
        }

        GameObject instance = Instantiate(prefab, position, rotation);
        instance.transform.parent = this.transform;

        Debug.Log($"Instantiated {prefab.name} at position {position} with rotation {rotation}.");
    }

    private Vector3 CalculatePosition(int cellX, int cellZ, string direction, string objectType)
    {
        float x = cellX * gridSpacing;
        float z = cellZ * gridSpacing;
        float y = (objectType == "Wall") ? 0.5f : 0f; // Apply elevation only to walls

        switch (direction)
        {
            case "right":
                x += gridSpacing / 2;
                break;
            case "left":
                x -= gridSpacing / 2;
                break;
            case "up":
                z += gridSpacing / 2;
                break;
            case "down":
                z -= gridSpacing / 2;
                break;
        }

        return new Vector3(x, y, z);
    }
}
