#include <WiFi.h>
#include <HTTPClient.h>

const char *ssid = "Foodpedia Margonda Raya LT2";
const char *password = "nasigorenghongkong";
const char *serverAddress = "http://192.168.0.136:5000/state_iot"; // Replace with your server IP address

const int LED_PIN = 2; // Assuming built-in LED pin is GPIO 2

void setup()
{
    Serial.begin(115200);
    delay(1000);

    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    Serial.println("Connecting to Wi-Fi...");
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to Wi-Fi");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Initialize LED pin as output
    pinMode(LED_PIN, OUTPUT);

    // Start checking state every 10 seconds
    setInterval(10);
}

void loop()
{
    static unsigned long lastCheckTime = 0;
    unsigned long currentTime = millis();

    // Check if it's time to check the state
    if (currentTime - lastCheckTime >= 10000)
    {
        lastCheckTime = currentTime;

        // Send request to server and get the state
        HTTPClient http;
        http.begin(serverAddress);
        int httpCode = http.GET();
        if (httpCode > 0)
        {
            if (httpCode == HTTP_CODE_OK)
            {
                String response = http.getString();
                Serial.println("Received state: " + response);
                // Parse the response and control LED based on the state
                if (response.indexOf("\"state\":\"ON\"") != -1)
                {
                    digitalWrite(LED_PIN, HIGH); // Turn on LED
                }
                else if (response.indexOf("\"state\":\"OFF\"") != -1)
                {
                    digitalWrite(LED_PIN, LOW); // Turn off LED
                }
            }
            else
            {
                Serial.println("Error getting state: " + httpCode);
            }
        }
        else
        {
            Serial.println("Connection failed");
        }
        http.end();
    }

    delay(100); // Delay to avoid excessive requests
}

void setInterval(unsigned long interval)
{
    static unsigned long lastInterval = 0;
    lastInterval = millis();
    while (millis() - lastInterval < interval * 1000)
    {
        delay(1);
    }
}
