#include <esp_now.h>
#include <WiFi.h>
#include "Packet.h"
#define RXD2 17
#define TXD2 16

//must be global
esp_now_peer_info_t peerInfo;

// REPLACE WITH YOUR RECEIVER MAC Address
uint8_t broadcastAddress[] = {0x24, 0x6F, 0x28, 0x7A, 0x93, 0x44};
// 24:0A:C4:61:50:C8 transceiver
// 24:6F:28:7A:93:44 test esp32

// Set values to send
uint8_t data[Packet::length];

// callback when data is sent
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

void setup() {

  Serial.begin(115200); //Serial for debugging
  
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2); //Serial for over wire transfer

  // Set device as a Wi-Fi Station
  WiFi.mode(WIFI_STA);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  // Once ESPNow is successfully Init, we will register for Send CB to
  // get the status of Trasnmitted packet
  esp_now_register_send_cb(OnDataSent);
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;

  // Add peer        
  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Failed to add peer");
    return;
  }
}

void loop() 
{
//Receiving data from the serial
  if (Serial2.available() >= Packet::length) 
  {
    Serial2.readBytes(data, Packet::length);
    esp_err_t result = esp_now_send(broadcastAddress, data, Packet::length);
    
    if (result == ESP_OK) {
      Serial.println("Sent with success");
    }
    else {
      Serial.println("Error sending the data");
    }
  }
}
