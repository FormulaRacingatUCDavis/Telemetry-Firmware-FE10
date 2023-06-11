#include "Packet.h"

int canId;
int id = -1;
short data[2][4];
byte wheelUpdated[4] = {0, 0, 0, 0};
unsigned long time;
unsigned long startTime;

// for simulation
int canIdVals[] = {0x470, 0x471, 0x472, 0x473, 0x475};
int canIdIndex = 0;

void setup() {
  Serial.begin(115200);  // for debugging
  Serial2.begin(9600, SERIAL_8N1);  // for UART
  startTime = micros();
}

void loop() {
  // currently simulating can messages, replace with real can access code
  for(short fakeData = 0; fakeData < 50; fakeData++)
  {
    canId = canIdVals[canIdIndex++ % 5];

    if (canId >= 0x470 && canId <= 0x473) {
      // wheel speed data
      id = 0;
      // could include math here to convert sensor data to speed
      data[id][canId - 0x470] = fakeData;
      wheelUpdated[canId - 0x470] = 1;
    } else if (canId == 0x475) {
      // steering data
      id = 1;
      data[id][0] = fakeData;
    }

    if (id == 1 || (id == 0 && wheelUpdated[0] && wheelUpdated[1] && wheelUpdated[2] && wheelUpdated[3])) {
      // enough data received to send a packet
      time = micros() - startTime;
      Packet p(id, data[id], time);
      send(&p);
      reset();
    }
  } 
}

void reset() {
  if (id == 0) {
    wheelUpdated[0] = 0;
    wheelUpdated[1] = 0;
    wheelUpdated[2] = 0;
    wheelUpdated[3] = 0;
  }
  id = -1;
}

void send(Packet* p) {
  byte* byteId = (byte*)(&(p->data_id));
  byte* byteData = (byte*)(p->data);
  byte* byteTime = (byte*)(&(p->time));
  byte buf[Packet::length] = {byteId[0], byteId[1],
                  byteData[0], byteData[1], byteData[2], byteData[3],
                  byteData[4], byteData[5], byteData[6], byteData[7],
                  byteTime[0], byteTime[1], byteTime[2], byteTime[3]};
  Serial2.write(buf, Packet::length);
}
