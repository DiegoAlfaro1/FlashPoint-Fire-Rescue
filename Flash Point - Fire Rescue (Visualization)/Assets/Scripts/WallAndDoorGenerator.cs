using System.Collections.Generic;
using UnityEngine;

public class WallAndDoorGenerator : MonoBehaviour
{
    public GameObject wallPrefab;
    public GameObject doorPrefab;
    public float gridSpacing = 1f;
    public Vector3 gridOrigin = Vector3.zero;
    
    // Define inner grid size
    public int innerGridX = 8; // Set via Inspector for the inner grid size
    public int innerGridZ = 6; // Set via Inspector for the inner grid size

    private int totalGridX; // Total grid size including outer space
    private int totalGridZ; // Total grid size including outer space

    public void Start()
    {
        // Calculate the total grid size including the outer space
        totalGridX = innerGridX + 2;
        totalGridZ = innerGridZ + 2;
    }

    public void ProcessGridStructure(Dictionary<string, List<List<object>>> gridStructure)
    {
        // Contadores para las celdas en gridStructure
        int counterX = 1;
        int counterZ = 1; // Empezamos desde 1

        // Iterar sobre cada celda de la cuadrícula interna
        for (int z = totalGridZ - 2; z > 0; z--)
        {
            // Reiniciar el contador de X en cada nueva fila Z
            counterX = 1;

            for (int x = 1; x < totalGridX - 1; x++)
            {
                // Crear la clave de la celda actual utilizando los contadores
                string cellKey = $"({counterZ}, {counterX})";

                // Verificar si la celda existe en gridStructure
                if (gridStructure.ContainsKey(cellKey))
                {
                    List<List<object>> neighbors = gridStructure[cellKey];

                    Debug.Log($"Processing cell {cellKey} with {neighbors.Count} neighbors.");

                    // Iterar sobre los vecinos de la celda
                    for (int i = 0; i < neighbors.Count; i++)
                    {
                        List<object> neighborInfo = neighbors[i];

                        // Verificar si la información del vecino es válida
                        if (neighborInfo.Count == 2)
                        {
                            // Extraer el tipo de conexión del vecino
                            int connectionType = (int)(long)neighborInfo[1]; // Convertir a entero
                            
                            // Mostrar información sobre el vecino
                            Debug.Log($"Cell {cellKey} has neighbor with connection type: {connectionType}");
                        }
                        else
                        {
                            Debug.LogError($"Neighbor information for cell {cellKey} is invalid or does not contain 2 elements.");
                        }
                    }
                }
                else
                {
                    Debug.LogWarning($"Cell {cellKey} not found in gridStructure.");
                }

                // Incrementar el contador de X
                counterX++;
            }

            // Incrementar el contador de Z después de procesar cada fila
            counterZ++;
        }
    }

}
