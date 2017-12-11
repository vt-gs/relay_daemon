/*
 Remote Relay Control, with ethernet
 for serial only refer to "remote_control_relay_v2.ino"
 Written by Zach Leffke, KJ4QLP
 June, 2012
 */

#include <SPI.h>
#include <Ethernet.h>
// network configuration.  gateway and subnet are optional.
byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};  
byte ip[] = {10, 10, 10, 100};    
byte gateway[] = {10, 10, 10, 1};
byte subnet[] = {255, 255, 255, 0};
EthernetServer server = EthernetServer(195);

//Global Variable Definition
String data_in; // stores incoming commands

int spdt_a = 0;  //spdt relay bank A, relays 1 - 8;
int spdt_b = 0;  //spdt relay bank B, relays 9 - 16;
int dpdt_a = 0;  //dpdt relay bank A, relays 1 - 8;
int dpdt_b = 0;  //dpdt relay bank B, relays 9 - 16;

String spdt_a_str;  //spdt relay bank A, relays 1 - 8;
String spdt_b_str;  //spdt relay bank B, relays 9 - 16;
String dpdt_a_str;  //dpdt relay bank A, relays 1 - 8;
String dpdt_b_str;  //dpdt relay bank B, relays 9 - 16;

//Relay Pin Configuration
int relay[] = {22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53};

//ADC Pin Configuration
int a_d_c[] = {8,9,10,11,12,13,14,15};

void setup() {
  // initialize the ethernet device
  Ethernet.begin(mac, ip, gateway, subnet);
  // start listening for clients
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
  delay(10);
  if (client){
    Serial.println("new client");
    while(client.connected()){
      Serial.println("connected");
      while(client.available()){
        char c = client.read();          // gets one byte from the serial buffer
        data_in += c;
      }
      Serial.print("Client Entered: ");
      Serial.println(data_in);
      
      delay(1000);     
    }
    Serial.println("client disconnected");
  }

} 
  /*if(client) {  //ethernet connection
    while (client.available()) {
      
    } 
    //IF ETHERNET DATA IS ENTERED
    if ((data_in.length() > 0) && (data_in.charAt(0) == '$')) { // if it is a valid string
      if (data_in.charAt(2) == 'R') {//Relay Assignment Command
        //Parse Relay Bank Values and Convert to Integer
        Parse_Relay(data_in);
        //Write Relay Value to PORTS
        Write_Relay(); 
        //Return Feedback
        Return_Network_Feedback();
      }
      else if(data_in.charAt(2) == 'S'){//Return Relay Status
        Return_Network_Feedback();
      }
      else if(data_in.charAt(2) == 'V'){//ADC Voltage Read Command
      }
      data_in = "";  //Clear Input String
    }
  }
  else{ //if(Serial.available()){ //SERIAL CONNECTION
    while (Serial.available()) {
      delay(10);
      if (Serial.available()) {
        char c = Serial.read();          // gets one byte from the serial buffer
        data_in += c;                   // appends the byte to the string serialIn
      }
    }
    //IF SERIAL DATA IS ENTERED
    if ((data_in.length() > 0) && (data_in.charAt(0) == '$')) { // if it is a valid string
      if (data_in.charAt(2) == 'R') {//Relay Assignment Command
        //Parse Relay Bank Values and Convert to Integer
        Parse_Relay(data_in);
        //Write Relay Value to PORTS
        Write_Relay();
        //Return Feedback
        Return_Serial_Feedback();
      }
      else if(data_in.charAt(2) == 'S'){//Return Relay Status
        Return_Serial_Feedback();
      }
      else if(data_in.charAt(2) == 'V'){//ADC Voltage Read Command
      }
      data_in = "";  //Clear Input String
    }
  }
  //RETURN FEEDBACK
  
  delay(500);
  
}*/







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


