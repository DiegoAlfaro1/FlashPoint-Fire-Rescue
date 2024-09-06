using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TerrainGenerator : MonoBehaviour
{
    // Prefabs for game tiles and objects
    public GameObject leftBorderTilePrefab;   
    public GameObject rightBorderTilePrefab;  
    public GameObject topBottomBorderTilePrefab;  
    public GameObject centerTilePrefab;  

    // Grid configuration variables
    public int innerGridX;
    public int innerGridZ;
    private int totalGridX;
    private int totalGridZ;
    public float gridSpacing = 1f;
    public Vector3 gridOrigin = Vector3.zero;

    void Start()
    {
        totalGridX = innerGridX + 2; 
        totalGridZ = innerGridZ + 2;

        if (totalGridX <= 0 || totalGridZ <= 0)
        {
            Debug.LogError("Grid dimensions must be positive.");
            return;
        }

        GenerateTerrain();
    }

    void GenerateTerrain()
    {
        for (int z = totalGridZ - 1; z >= 0; z--)
        {
            for (int x = 0; x < totalGridX; x++)
            {
                Vector3 spawnPos = new Vector3(x * gridSpacing, 0, (totalGridZ - 1 - z) * gridSpacing) + gridOrigin; 
                GameObject tilePrefab = GetTilePrefab(x, z);
                GameObject tile = Instantiate(tilePrefab, spawnPos, Quaternion.Euler(90, 0, 0)); 
                tile.transform.parent = this.transform;
            }
        }
    }

    GameObject GetTilePrefab(int x, int z)
    {
        if (x == 0) return leftBorderTilePrefab;  
        if (x == totalGridX - 1) return rightBorderTilePrefab;  
        if (z == 0 || z == totalGridZ - 1) return topBottomBorderTilePrefab;  

        return centerTilePrefab;
    }
}
