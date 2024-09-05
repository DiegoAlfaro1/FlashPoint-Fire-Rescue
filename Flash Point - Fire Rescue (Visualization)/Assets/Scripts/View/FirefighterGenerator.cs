using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FirefighterGenerator : MonoBehaviour
{
    public GameObject firefighterPrefab;
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

    public void GenerateFirefighters(List<Firefighter> firefighterPositions)
    {
        int counterX = 1;
        int counterZ = 1;

        Debug.Log("Starting firefighter generation...");

        // Iterate through the grid rows
        for (int z = totalGridZ - 2; z > 0; z--)
        {
            counterX = 1;

            // Iterate through the grid columns
            for (int x = 1; x < totalGridX - 1; x++)
            {
                // Compare with the firefighter positions to place them in the correct location
                foreach (var firefighter in firefighterPositions)
                {
                    if (firefighter.position[0] == counterZ && firefighter.position[1] == counterX)
                    {
                        // Calculate the position to place the firefighter at the center of the cell
                        Vector3 firefighterPosition = new Vector3(
                            x * gridSpacing,
                            0,
                            z * gridSpacing
                        ) + gridOrigin;

                        // Instantiate the firefighter object at the calculated position
                        InstantiateObject(firefighterPosition, Quaternion.identity, firefighterPrefab);
                        Debug.Log($"Firefighter generated at Unity position: {firefighterPosition}");
                    }
                }

                counterX++;
            }

            counterZ++;
        }

        Debug.Log("Firefighter generation complete.");
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
    }
}
