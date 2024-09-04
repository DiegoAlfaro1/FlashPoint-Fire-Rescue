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

    public void Start()
    {
        totalGridX = innerGridX + 2;
        totalGridZ = innerGridZ + 2;
    }

    public void GeneratePOIs(List<POI> poiLocations)
    {
        int counterX = 1;
        int counterZ = 1;

        Debug.Log("Starting POI generation...");

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
                        Debug.Log($"POI generated at Unity position: {poiPosition}");
                    }
                }

                counterX++;
            }

            counterZ++;
        }

        Debug.Log("POI generation complete.");
    }

    public void GenerateFire(List<List<int>> fireLocations)
    {
        int counterX = 1;
        int counterZ = 1;

        Debug.Log("Starting fire generation...");

        for (int z = totalGridZ - 2; z > 0; z--)
        {
            counterX = 1;

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
                        Debug.Log($"Fire generated at Unity position: {firePosition}");
                    }
                }

                counterX++;
            }

            counterZ++;
        }

        Debug.Log("Fire generation complete.");
    }

    public void GenerateSmoke(List<List<int>> smokeLocations)
    {
        int counterX = 1;
        int counterZ = 1;

        Debug.Log("Starting smoke generation...");

        for (int z = totalGridZ - 2; z > 0; z--)
        {
            counterX = 1;

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
                        Debug.Log($"Smoke generated at Unity position: {smokePosition}");
                    }
                }

                counterX++;
            }

            counterZ++;
        }

        Debug.Log("Smoke generation complete.");
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
