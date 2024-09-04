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

            Debug.Log($"Procesando la celda {cellKey}");

            // Recorrer la lista de vecinos de cada celda
            for (int i = 0; i < neighbors.Count; i++)
            {
                List<object> neighborInfo = neighbors[i];

                if (neighborInfo.Count == 2)
                {
                    List<object> position = neighborInfo[0] as List<object>;
                    int connectionType = (int)(long)neighborInfo[1]; // Convertir a entero

                    // Determinar la dirección basada en el índice
                    string direction = GetDirection(gridStructure, cellKey, i);

                    Debug.Log($"Celda {cellKey} tiene un vecino en dirección {direction} con tipo de conexión: {connectionType}");

                    // Instanciar objetos según el tipo de conexión
                    if (connectionType == 5)
                    {
                        Debug.Log($"Instanciar un muro hacia {direction}.");
                        InstantiateObject(cellKey, direction, "Wall");
                    }
                    else if (connectionType == 2)
                    {
                        Debug.Log($"Instanciar una puerta hacia {direction}.");
                        InstantiateObject(cellKey, direction, "Door");
                    }
                }
                else
                {
                    Debug.LogError("La información del vecino no es válida o no contiene 2 elementos.");
                }
            }
        }
    }

    // Método para determinar la dirección basada en la celda, el índice y la estructura de la cuadrícula
    string GetDirection(Dictionary<string, List<List<object>>> gridStructure, string cellKey, int index)
    {
        // Obtener la posición de la celda actual
        string[] parts = cellKey.Trim('(', ')').Split(',');
        int x = int.Parse(parts[0].Trim());
        int y = int.Parse(parts[1].Trim());

        // Determinar la dirección basada en el índice y la posición de la celda
        int totalRows = gridStructure.Count; // Número total de filas
        int totalColumns = gridStructure[cellKey].Count; // Número total de columnas

        if (index == 0) return (x == 1) ? "abajo" : "arriba";
        else if (index == 1) return (y == 1) ? "derecha" : "izquierda";
        else if (index == 2) return (x == totalRows) ? "arriba" : "abajo";
        else if (index == 3) return (y == totalColumns) ? "izquierda" : "derecha";

        return "";
    }

    // Método para instanciar un objeto (muro o puerta)
    void InstantiateObject(string cellKey, string direction, string type)
    {
        Vector3 position = CalculatePosition(cellKey, direction);
        Quaternion rotation = Quaternion.identity; // Ajustar rotación según sea necesario

        GameObject prefab = type == "Wall" ? wallPrefab : doorPrefab;
        if (prefab == null)
        {
            Debug.LogError("Prefab no asignado.");
            return;
        }

        GameObject instance = Instantiate(prefab, position, rotation);
        instance.transform.parent = this.transform;
        Debug.Log($"{type} instanciado en dirección {direction} para la celda {cellKey}.");
    }

    // Método para calcular la posición del objeto basado en la celda y la dirección
    private Vector3 CalculatePosition(string cellPositionKey, string direction)
    {
        // Convertir la posición de celda de string a Vector2Int
        string[] positionParts = cellPositionKey.Trim('(', ')').Split(',');
        int cellX = int.Parse(positionParts[0].Trim());
        int cellZ = int.Parse(positionParts[1].Trim());

        // Calcular la posición base de la celda en el espacio 3D
        float x = (cellX - 1) * gridSpacing; // -1 porque las celdas empiezan desde 1
        float z = (cellZ - 1) * gridSpacing; // -1 porque las celdas empiezan desde 1
        float y = 0.5f; // Elevar el objeto 0.5 unidades por encima del suelo

        // Ajustar las coordenadas según la dirección
        if (direction == "derecha") x += gridSpacing / 2;
        if (direction == "izquierda") x -= gridSpacing / 2;
        if (direction == "arriba") z += gridSpacing / 2;
        if (direction == "abajo") z -= gridSpacing / 2;

        return new Vector3(x, y, z);
    }

}
