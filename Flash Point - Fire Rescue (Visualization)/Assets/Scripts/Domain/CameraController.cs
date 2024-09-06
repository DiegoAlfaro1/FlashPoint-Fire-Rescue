using UnityEngine;

public class CameraController : MonoBehaviour
{
    public float moveSpeed = 5f; 
    public Vector3 gridOrigin = Vector3.zero; 
    public float gridSpacing = 1f; 
    public int innerGridX; 
    public int innerGridZ; 

    private float minX, maxX, minZ, maxZ;

    /// <summary>
    /// Initializes camera movement bounds based on the grid size.
    /// </summary>
    void Start()
    {
        // Calculate camera movement bounds based on the grid size
        minX = gridOrigin.x + 1;
        maxX = gridOrigin.x + (innerGridX) * gridSpacing;
        minZ = gridOrigin.z + 1;
        maxZ = gridOrigin.z + (innerGridZ) * gridSpacing;
    }

    /// <summary>
    /// Handles camera movement and restricts it within the defined boundaries.
    /// </summary>
    void Update()
    {
        // Get keyboard input for camera movement
        float horizontalInput = Input.GetAxis("Horizontal");
        float verticalInput = Input.GetAxis("Vertical");

        // Calculate the movement vector
        Vector3 movement = new Vector3(horizontalInput, 0, verticalInput) * moveSpeed * Time.deltaTime;

        // Apply the movement to the current camera position
        transform.position += movement;

        // Clamp the camera's position within the calculated bounds
        float clampedX = Mathf.Clamp(transform.position.x, minX, maxX);
        float clampedZ = Mathf.Clamp(transform.position.z, minZ, maxZ);

        // Update the camera's position with clamped values
        transform.position = new Vector3(clampedX, transform.position.y, clampedZ);
    }
}
