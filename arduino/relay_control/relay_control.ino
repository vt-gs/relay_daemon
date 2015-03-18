/*
 Remote Relay Control, with ethernet/TCP
 Virginia Tech Ground Station
 for serial only refer to "remote_control_relay_v2.ino"
 Written by Zach Leffke, KJ4QLP
 March, 2015
 */

#include <SPI.h>
#include <Ethernet.h>

// network configuration.  gateway and subnet are optional.
byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};  
byte ip[] = {192, 168, 42, 11};    
byte gateway[] = {192, 168, 42, 1};
byte subnet[] = {255, 255, 255, 0};
unsigned int localport = 2000;
EthernetServer server = EthernetServer(localport);

//Global Variable Definition
String serIn;   // stores incoming serial commands
String netIn;   //stores incoming network commands
String dataIn;
boolean dataSrc; //dataSrc boolean, False = serial, True = network

int spdt_a;        //spdt relay bank A, relays 1 - 8;
int spdt_b;        //spdt relay bank B, relays 9 - 16;
int dpdt_a;        //dpdt relay bank A, relays 1 - 8;
int dpdt_b;        //dpdt relay bank B, relays 9 - 16;

String spdt_a_str; //spdt relay bank A, relays 1 - 8;
String spdt_b_str; //spdt relay bank B, relays 9 - 16;
String dpdt_a_str; //dpdt relay bank A, relays 1 - 8;
String dpdt_b_str; //dpdt relay bank B, relays 9 - 16;

//Relay Pin Configuration
int relay[] = {22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53};

//ADC Pin Configuration
int a_d_c[] = {8,9,10,11,12,13,14,15};

void setup() {
  // initialize the ethernet device
  Ethernet.begin(mac, ip, gateway, subnet);
  // initialize the server
  server.begin();
  
  //Start Serial Connection
  Serial.begin(9600);
  //Configure Pins as output
  for(int index = 0; index < 32; index++){
    pinMode(relay[index], OUTPUT);
  }
  pinMode(A8, OUTPUT);
  pinMode(A9, OUTPUT);
  pinMode(A10, OUTPUT);
  pinMode(A11, OUTPUT);
  pinMode(A12, OUTPUT);
  pinMode(A13, OUTPUT);
  pinMode(A14, OUTPUT);
  pinMode(A15, OUTPUT);
}

void loop(){
  
  // if an incoming client connects, there will be bytes available to read:
  EthernetClient client = server.available();
  if (client==true && client.available()>0) {
    int packetLength = client.available();
    //Serial.print(packetLength);
    for (int i = 0; i < packetLength; i++){
      char c = client.read();          // gets one byte from the network buffer
      netIn += c;
    }
  }
  
  // SERIAL INPUT
  while (Serial.available()) {
    delay(10);
    if (Serial.available()) {
      char c = Serial.read();          // gets one byte from the serial buffer
      serIn += c;                   // appends the byte to the string serIn
    }
  }
  
  //Decide which command to listen too, Serial has higher priority
  if (serIn.length() > 0){
    Parse_Input_Data(serIn, true);
    serIn = "";
  }
  else if (netIn.length() > 0){
    Parse_Input_Data(netIn, false);
    netIn = "";
  }
  delay(500);
    
} 

void Parse_Input_Data(String data, boolean src){
  if ((data.length() > 0) && (data.charAt(0) == '$')) {// if it is a valid string
//    if ((dataIn.length() == 19) && (dataIn.charAt(2) == 'R')) { // Relay Control Command
    if (data.charAt(2) == 'R') { // Relay Control Command       
      
      Parse_Relay(data);
      Write_Relay();
      
      if (src == true){
        Return_Serial_Feedback();
      }
      else if (src == false){
        Return_Network_Feedback();
      }
    }
    else if(data.charAt(2) == 'Q') { // Relay Status Query Command   
      if (src == true){
        Return_Serial_Feedback();
      }
      else if (src == false){
        Return_Network_Feedback();
      }
    }
    else if(data.charAt(2) == 'V'){//ADC Voltage Read Command
    }
  }  
}

void Return_Network_Feedback(){
  server.print("$,");
  server.print(spdt_a, BIN);
  server.print(",");
  server.print(spdt_b, BIN);
  server.print(",");
  server.print(dpdt_a, BIN);
  server.print(",");
  server.println(dpdt_b, BIN);
}

void Return_Serial_Feedback(){
  Serial.print("$,");
  Serial.print(spdt_a, BIN);
  Serial.print(",");
  Serial.print(spdt_b, BIN);
  Serial.print(",");
  Serial.print(dpdt_a, BIN);
  Serial.print(",");
  Serial.println(dpdt_b, BIN);
}

void Parse_Relay(String data){
  //Convert String Relay Bank String Value to Integer
  spdt_a = String_To_Int(data.substring(4, 7));   //SPDT A conversion
  spdt_b = String_To_Int(data.substring(8, 11));  //SPDT B conversion
  dpdt_a = String_To_Int(data.substring(12, 15)); //DPDT A conversion
  dpdt_b = String_To_Int(data.substring(16, 19)); //DPDT B conversion 
}

void Write_Relay(){
  //Write Relay Bank Value to Relay Bank Port
  PORTA = spdt_a;  //Write to SPDT A register
  PORTC = spdt_b;  //Write to SPDT B register
  PORTL = dpdt_a;  //Write to DPDT A register
  PORTK = dpdt_b;  //Write to DPDT B register
}

int String_To_Int(String data_string){
  //Converts Relay Bank String Parameter to Integer
  int val;
  char carray[6];                       // magic needed to convert string to a number 
  data_string.toCharArray(carray, sizeof(carray));
  val = atoi(carray);
  return val;
}


