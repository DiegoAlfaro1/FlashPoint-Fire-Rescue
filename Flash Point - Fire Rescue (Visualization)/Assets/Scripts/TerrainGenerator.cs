using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TerrainGenerator : MonoBehaviour
{
    // Prefabs for game tiles and objects
    public GameObject leftBorderTilePrefab;   // Left side border tile
    public GameObject rightBorderTilePrefab;  // Right side border tile
    public GameObject topBottomBorderTilePrefab;  // Top and bottom border tiles
    public GameObject centerTilePrefab;  // Center tile

    // Grid configuration variables
    public int innerGridX; // Set via Inspector for the inner grid size
    public int innerGridZ; // Set via Inspector for the inner grid size
    private int totalGridX; // Total grid size including the outer space
    private int totalGridZ; // Total grid size including the outer space
    public float gridSpacing = 1f;
    public Vector3 gridOrigin = Vector3.zero;

    void Start()
    {
        // Calculate the total grid size including the outer space
        totalGridX = innerGridX + 2; 
        totalGridZ = innerGridZ + 2;

        if (totalGridX <= 0 || totalGridZ <= 0)
        {
            Debug.LogError("Grid dimensions must be positive.");
            return;
        }

        // Procedural generation by sections
        GenerateTerrain();

    }

    // Generate base terrain
    void GenerateTerrain()
    {
        // Invertir el bucle para z, comenzando desde la parte superior
        for (int z = totalGridZ - 1; z >= 0; z--)
        {
            for (int x = 0; x < totalGridX; x++)
            {
                // Ajustar la posición de generación
                Vector3 spawnPos = new Vector3(x * gridSpacing, 0, (totalGridZ - 1 - z) * gridSpacing) + gridOrigin; 
                GameObject tilePrefab = GetTilePrefab(x, z);
                // Ensure the correct rotation by using Quaternion.Euler
                GameObject tile = Instantiate(tilePrefab, spawnPos, Quaternion.Euler(90, 0, 0)); // Adjust rotation to lie flat
                tile.transform.parent = this.transform;
            }
        }
    }

    // Determine which tile prefab to use for each cell
    GameObject GetTilePrefab(int x, int z)
    {
        if (x == 0) return leftBorderTilePrefab;  // Left border
        if (x == totalGridX - 1) return rightBorderTilePrefab;  // Right border
        if (z == 0 || z == totalGridZ - 1) return topBottomBorderTilePrefab;  // Upper and lower borders

        return centerTilePrefab;  // Center tile
    }

    void Update()
    {
    }
}
