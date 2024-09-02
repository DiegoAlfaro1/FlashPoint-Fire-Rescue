using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WallAndDoorGenerator : MonoBehaviour
{
    // Prefabs for different states of walls and doors
    public GameObject wallIntactPrefab;  
    public GameObject wallDamagedPrefab;
    public GameObject doorClosedPrefab;
    public GameObject doorOpenPrefab;

    // Grid configuration variables
    public float gridSpacing = 1f;
    public Vector3 gridOrigin = Vector3.zero;

    // Matrices to store the state of walls and doors
    private Dictionary<Vector2Int, (Vector2Int, string, GameObject)> wallMatrix = new Dictionary<Vector2Int, (Vector2Int, string, GameObject)>();
    private Dictionary<Vector2Int, (Vector2Int, string, GameObject)> doorMatrix = new Dictionary<Vector2Int, (Vector2Int, string, GameObject)>();

    void Start()
    {

        // Example data for initial wall and door states
        // TODO: Delete when the actual data is available
        InitializeWallAndDoorStates();


        GenerateWallsAndDoors();
    }

    void InitializeWallAndDoorStates()
    {
        // Input string representing the walls in the grid
        string wallString = @"
        1100 1000 1001 1100 1001 1100 1000 1001
        0100 0000 0011 0100 0011 0110 0010 0011
        0100 0001 1100 1000 1000 1001 1100 1001
        0100 0011 0110 0010 0010 0011 0110 0011
        1100 1000 1000 1000 1001 1100 1001 1101
        0110 0010 0010 0010 0011 0110 0011 0111";

        // Clear existing data
        wallMatrix.Clear();
        doorMatrix.Clear();

        // Offset para centrar la cuadrícula
        int offset = 1;

        // Separar la cadena en filas
        string[] rows = wallString.Trim().Split('\n');

        // Iterar sobre cada fila desde la parte superior (invirtiendo el bucle)
        for (int z = rows.Length - 1; z >= 0; z--)
        {
            // Separar cada fila en celdas individuales
            string[] cells = rows[z].Trim().Split(' ');

            for (int x = 0; x < cells.Length; x++)
            {
                // Posición real de la celda considerando el offset
                Vector2Int cell = new Vector2Int(x + offset, (rows.Length - 1 - z) + offset);

                // Celdas adyacentes para la configuración de paredes
                Vector2Int upCell = new Vector2Int(cell.x, cell.y + 1);
                Vector2Int downCell = new Vector2Int(cell.x, cell.y - 1);
                Vector2Int leftCell = new Vector2Int(cell.x - 1, cell.y);
                Vector2Int rightCell = new Vector2Int(cell.x + 1, cell.y);

                // Leer los dígitos de la celda
                string cellData = cells[x].Trim();

                // Asignar cada dígito a una variable que representa una dirección
                char up = cellData[0];      // Primer dígito: arriba
                char left = cellData[1];    // Segundo dígito: izquierda
                char down = cellData[2];    // Tercer dígito: abajo
                char right = cellData[3];   // Cuarto dígito: derecha

                // Configurar paredes basadas en los dígitos
                if (up == '1') // Pared hacia arriba
                    wallMatrix[cell] = (upCell, "intact", null);

                if (left == '1') // Pared hacia la izquierda
                    wallMatrix[cell] = (leftCell, "intact", null);

                if (down == '1') // Pared hacia abajo
                    wallMatrix[cell] = (downCell, "intact", null);

                if (right == '1') // Pared hacia la derecha
                    wallMatrix[cell] = (rightCell, "intact", null);

                // Colocar puertas aleatorias en algunas ubicaciones
                if (Random.value > 0.9f) // 10% de probabilidad para una puerta
                {
                    // Estado aleatorio para la puerta
                    string doorState = Random.value > 0.5f ? "open" : "closed";

                    // Agregar la puerta a doorMatrix
                    doorMatrix[cell] = (rightCell, doorState, null);
                }
            }
        }
    }

    void GenerateWallsAndDoors()
    {
        // Use a temporary list to store keys for modification
        List<Vector2Int> wallKeys = new List<Vector2Int>(wallMatrix.Keys);
        List<Vector2Int> doorKeys = new List<Vector2Int>(doorMatrix.Keys);

        // Generate Walls
        foreach (var key in wallKeys)
        {
            Vector2Int cell1 = key;
            Vector2Int cell2 = wallMatrix[key].Item1;
            string state = wallMatrix[key].Item2;

            if (state != "broken")
            {
                Vector3 position = GetObjectPosition(cell1, cell2);
                Quaternion rotation = GetObjectRotation(cell1, cell2);

                GameObject wallInstance = Instantiate(GetWallPrefab(state), position, rotation);
                wallInstance.transform.parent = this.transform;
                wallMatrix[cell1] = (cell2, state, wallInstance); // Update dictionary outside the loop
            }
        }

        // Generate Doors
        foreach (var key in doorKeys)
        {
            Vector2Int cell1 = key;
            Vector2Int cell2 = doorMatrix[key].Item1;
            string state = doorMatrix[key].Item2;

            if (state != "broken")
            {
                Vector3 position = GetObjectPosition(cell1, cell2);
                Quaternion rotation = GetObjectRotation(cell1, cell2);

                GameObject doorInstance = Instantiate(GetDoorPrefab(state), position, rotation);
                doorInstance.transform.parent = this.transform;
                doorMatrix[cell1] = (cell2, state, doorInstance); // Update dictionary outside the loop
            }
        }
    }
    // Adjusted to ensure the objects are placed at the correct height
    Vector3 GetObjectPosition(Vector2Int cell1, Vector2Int cell2)
    {
        float midX = (cell1.x + cell2.x) / 2f * gridSpacing;
        float midZ = (cell1.y + cell2.y) / 2f * gridSpacing;
        float adjustedHeight = 0.5f; // Use the correct height to place objects on the surface

        return new Vector3(midX, adjustedHeight, midZ) + gridOrigin;
    }

    Quaternion GetObjectRotation(Vector2Int cell1, Vector2Int cell2)
    {
        if (cell1.x == cell2.x) // Vertical alignment
            return Quaternion.identity; 
        else // Horizontal alignment
            return Quaternion.Euler(0, 90, 0); 
    }

    GameObject GetWallPrefab(string state)
    {
        switch (state)
        {
            case "intact": return wallIntactPrefab;
            case "damaged": return wallDamagedPrefab;
            default: return null; // No prefab for "broken"
        }
    }

    GameObject GetDoorPrefab(string state)
    {
        switch (state)
        {
            case "closed": return doorClosedPrefab;
            case "open": return doorOpenPrefab;
            default: return null; // No prefab for "broken"
        }
    }

    public void UpdateState(Vector2Int cell1, Vector2Int cell2, string type, string newState)
    {
        if (type == "Wall" && wallMatrix.ContainsKey(cell1))
        {
            if (wallMatrix[cell1].Item3 != null)
                Destroy(wallMatrix[cell1].Item3);

            if (newState != "broken")
            {
                Vector3 position = GetObjectPosition(cell1, cell2);
                Quaternion rotation = GetObjectRotation(cell1, cell2);
                GameObject newWallInstance = Instantiate(GetWallPrefab(newState), position, rotation);
                newWallInstance.transform.parent = this.transform;

                wallMatrix[cell1] = (cell2, newState, newWallInstance);
            }
            else
            {
                wallMatrix[cell1] = (cell2, newState, null);
            }
        }
        else if (type == "Door" && doorMatrix.ContainsKey(cell1))
        {
            if (doorMatrix[cell1].Item3 != null)
                Destroy(doorMatrix[cell1].Item3);

            if (newState != "broken")
            {
                Vector3 position = GetObjectPosition(cell1, cell2);
                Quaternion rotation = GetObjectRotation(cell1, cell2);
                GameObject newDoorInstance = Instantiate(GetDoorPrefab(newState), position, rotation);
                newDoorInstance.transform.parent = this.transform;

                doorMatrix[cell1] = (cell2, newState, newDoorInstance);
            }
            else
            {
                doorMatrix[cell1] = (cell2, newState, null);
            }
        }
    }

    void Update()
    {
    }
}
