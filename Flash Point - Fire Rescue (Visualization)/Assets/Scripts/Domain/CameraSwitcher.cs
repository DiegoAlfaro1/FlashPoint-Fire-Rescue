using UnityEngine;

public class CameraSwitcher : MonoBehaviour
{
    public Camera camera1; // Reference to the first camera
    public Camera camera2; // Reference to the second camera

    void Start()
    {
        // Ensure only one camera is active at the start
        camera1.enabled = true;
        camera2.enabled = false;
    }

    void Update()
    {
        // Check if the "C" key is pressed
        if (Input.GetKeyDown(KeyCode.C))
        {
            // Toggle the state of the cameras
            camera1.enabled = !camera1.enabled;
            camera2.enabled = !camera2.enabled;
        }
    }
}
