using TMPro;
using UnityEngine;

public class GameStatsUI : MonoBehaviour
{
    // Variables como placeholders
    public int damageMarkers = 0;  // Marcadores de daño
    public int savedVictims = 0;   // Víctimas salvadas
    public int deadVictims = 0;    // Víctimas muertas

    // Referencias a los textos de la UI
    public TMP_Text damageMarkersText;
    public TMP_Text savedVictimsText;
    public TMP_Text deadVictimsText;

    // Actualizar la UI con los valores actuales
    void UpdateUI()
    {
        damageMarkersText.text = "Marcadores de Daño: " + damageMarkers;
        savedVictimsText.text = "Víctimas Salvadas: " + savedVictims;
        deadVictimsText.text = "Víctimas Muertas: " + deadVictims;
    }

    // Llamar cuando se actualicen los valores (puedes llamar a esto en otro script)
    public void UpdateStats(int newDamageMarkers, int newSavedVictims, int newDeadVictims)
    {
        damageMarkers = newDamageMarkers;
        savedVictims = newSavedVictims;
        deadVictims = newDeadVictims;

        UpdateUI(); // Reflejar los nuevos valores en la UI
    }

    // Ejemplo de cómo probar la actualización
    void Start()
    {
        // Llamar a la función de actualización con valores de prueba
        UpdateStats(3, 2, 1); // Aquí puedes probar diferentes valores
    }
}
