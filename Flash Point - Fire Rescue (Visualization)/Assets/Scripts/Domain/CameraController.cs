using UnityEngine;

public class CameraController : MonoBehaviour
{
    public float moveSpeed = 5f; // Camera movement speed
    public Vector3 gridOrigin = Vector3.zero; // Origin of the grid
    public float gridSpacing = 1f; // Spacing between grid cells
    public int innerGridX; // Inner grid size along the X-axis
    public int innerGridZ; // Inner grid size along the Z-axis

    private float minX, maxX, minZ, maxZ;

    void Start()
    {
        // Calculate camera movement bounds based on the grid size
        minX = gridOrigin.x + 1;
        maxX = gridOrigin.x + (innerGridX) * gridSpacing;
        minZ = gridOrigin.z + 1;
        maxZ = gridOrigin.z + (innerGridZ) * gridSpacing;
    }

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
