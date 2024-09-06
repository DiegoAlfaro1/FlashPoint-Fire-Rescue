using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameElementsGenerator : MonoBehaviour
{
    public GameObject poiPrefab;
    public GameObject firePrefab;
    public GameObject smokePrefab;
    public float gridSpacing = 1f;
    public Vector3 gridOrigin = Vector3.zero;
    public int innerGridX = 8;
    public int innerGridZ = 6;

    private int totalGridX;
    private int totalGridZ;

    /// <summary>
    /// Initializes the grid size.
    /// </summary>
    public void Start()
    {
        totalGridX = innerGridX + 2;
        totalGridZ = innerGridZ + 2;
    }

    /// <summary>
    /// Generates Points of Interest (POIs) on the grid.
    /// </summary>
    /// <param name="poiLocations">List of POI positions.</param>
    public void GeneratePOIs(List<POI> poiLocations)
    {
        int counterX = 1;
        int counterZ = 1;

        // Iterate through the grid rows
        for (int z = totalGridZ - 2; z > 0; z--)
        {
            counterX = 1;

            // Iterate through the grid columns
            for (int x = 1; x < totalGridX - 1; x++)
            {
                // Compare with the POI positions to place them in the correct location
                foreach (var poi in poiLocations)
                {
                    if (poi.position[0] == counterZ && poi.position[1] == counterX)
                    {
                        // Calculate the position to place the POI at the center of the cell
                        Vector3 poiPosition = new Vector3(
                            x * gridSpacing,
                            0,
                            z * gridSpacing
                        ) + gridOrigin;

                        // Instantiate the POI object at the calculated position
                        InstantiateObject(poiPosition, Quaternion.identity, poiPrefab);
                    }
                }

                counterX++;
            }

            counterZ++;
        }
    }

    /// <summary>
    /// Generates fire objects on the grid.
    /// </summary>
    /// <param name="fireLocations">List of fire positions.</param>
    public void GenerateFire(List<List<int>> fireLocations)
    {
        int counterX = 1;
        int counterZ = 1;

        // Iterate through the grid rows
        for (int z = totalGridZ - 2; z > 0; z--)
        {
            counterX = 1;

            // Iterate through the grid columns
            for (int x = 1; x < totalGridX - 1; x++)
            {
                foreach (var fire in fireLocations)
                {
                    if (fire[0] == counterZ && fire[1] == counterX)
                    {
                        Vector3 firePosition = new Vector3(
                            x * gridSpacing,
                            0,
                            z * gridSpacing
                        ) + gridOrigin;

                        InstantiateObject(firePosition, Quaternion.identity, firePrefab);
                    }
                }

                counterX++;
            }

            counterZ++;
        }
    }

    /// <summary>
    /// Generates smoke objects on the grid.
    /// </summary>
    /// <param name="smokeLocations">List of smoke positions.</param>
    public void GenerateSmoke(List<List<int>> smokeLocations)
    {
        int counterX = 1;
        int counterZ = 1;

        // Iterate through the grid rows
        for (int z = totalGridZ - 2; z > 0; z--)
        {
            counterX = 1;

            // Iterate through the grid columns
            for (int x = 1; x < totalGridX - 1; x++)
            {
                foreach (var smoke in smokeLocations)
                {
                    if (smoke[0] == counterZ && smoke[1] == counterX)
                    {
                        Vector3 smokePosition = new Vector3(
                            x * gridSpacing,
                            0,
                            z * gridSpacing
                        ) + gridOrigin;

                        InstantiateObject(smokePosition, Quaternion.identity, smokePrefab);
                    }
                }

                counterX++;
            }

            counterZ++;
        }
    }

    /// <summary>
    /// Instantiates a new game object at the given position.
    /// </summary>
    /// <param name="position">Position where the object will be placed.</param>
    /// <param name="rotation">Rotation of the object.</param>
    /// <param name="prefab">The prefab to instantiate.</param>
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
