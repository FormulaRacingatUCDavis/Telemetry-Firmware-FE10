#include "Packet.h"

int canid;
int id;
short data[4];
byte fill[4];
unsigned long timer = 0;
unsigned long startTime = 0;

// for simulation
int canidvals[] = {0x470, 0x471, 0x472, 0x473, 0x475};
int canidindex = 0;

void setup() 
{
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1);
  startTime = micros();
  reset();
}

void loop() 
{
  for(short modulator = 0; modulator < 50; modulator++)
  {
    canid = canidvals[canidindex % 5];
    if (canid >= 0x470 && canid <= 0x473) {
      id = 0;  // wheel speed
      data[canid - 0x470] = modulator;
      fill[canid - 0x470] = 1;
    } else if (id == -1 && canid == 0x475) {
      id = 1; // steering
      data[0] = modulator;
    }
    if (id == 1 || (fill[0] && fill[1] && fill[2] && fill[3])) {
      timer = micros() - startTime;
      Packet p(id, data, timer);
      send(&p);
      reset();
    }
    canidindex++;
  } 
}

void reset() {
  id = -1;
  fill[0] = 0;
  fill[1] = 0;
  fill[2] = 0;
  fill[3] = 0;
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
