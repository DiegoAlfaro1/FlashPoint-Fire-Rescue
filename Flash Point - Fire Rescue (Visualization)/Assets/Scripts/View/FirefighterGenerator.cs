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
        Debug.Log("Starting firefighter generation...");

        foreach (var firefighter in firefighterPositions)
        {
            int originalX = firefighter.position[0];
            int originalZ = firefighter.position[1];

            // Adjust the position to Unity coordinates, reflecting Python's axis order
            Vector3 firefighterPosition = new Vector3(
                originalZ * gridSpacing,
                0,
                originalX * gridSpacing
            ) + gridOrigin;

            InstantiateObject(firefighterPosition, Quaternion.identity, firefighterPrefab);
            Debug.Log($"Firefighter generated at Unity position: {firefighterPosition}");
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
