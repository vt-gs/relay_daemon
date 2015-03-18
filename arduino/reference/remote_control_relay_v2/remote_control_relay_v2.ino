/*
 Remote Relay Control v1
 Written by Zach Leffke, KJ4QLP
 January 18, 2010
 */

//Global Variable Definition
String serialIn;             // stores incoming serial commands
int spdt_a;  //spdt relay bank A, relays 1 - 8;
int spdt_b;  //spdt relay bank B, relays 9 - 16;
int dpdt_a;  //dpdt relay bank A, relays 1 - 8;
int dpdt_b;  //dpdt relay bank B, relays 9 - 16;
String spdt_a_str;  //spdt relay bank A, relays 1 - 8;
String spdt_b_str;  //spdt relay bank B, relays 9 - 16;
String dpdt_a_str;  //dpdt relay bank A, relays 1 - 8;
String dpdt_b_str;  //dpdt relay bank B, relays 9 - 16;
//Relay Pin Configuration
int relay[] = {22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53};
/*
relay[0] = spdt relay 1
relay[15] = spdt relay 16
relay[16] = dpdt relay 1
relay[31] = dpdt relay 16
*/

//ADC Pin Configuration
int a_d_c[] = {8,9,10,11,12,13,14,15};
//ADC[0] = ADC 1
//ADC[7] = ADC 8

void setup() {
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
  /*digitalWrite(relay[16], LOW);
  delay(2000);
  digitalWrite(relay[16], LOW);
  delay(2000);
  */
  
  // beginning of section to get values from serial port
  while (Serial.available()) {
    delay(10);
    if (Serial.available()) {
      char c = Serial.read();          // gets one byte from the serial buffer
      serialIn += c;                   // appends the byte to the string serialIn
    }
  }
  
  //IF SERIAL DATA IS ENTERED
  if ((serialIn.length() > 0) && (serialIn.charAt(0) == '$')) {          // if it is a valid string
//    if ((serialIn.length() == 19) && (serialIn.charAt(2) == 'R')) { // Relay Control Command
    if (serialIn.charAt(2) == 'R') { // Relay Control Command       
      spdt_a_str = serialIn.substring(4, 7);
      char carray1[6];                       // magic needed to convert string to a number 
      spdt_a_str.toCharArray(carray1, sizeof(carray1));
      spdt_a = atoi(carray1);
      
      spdt_b_str = serialIn.substring(8, 11);
      char carray2[6];                       // magic needed to convert string to a number 
      spdt_b_str.toCharArray(carray2, sizeof(carray2));
      spdt_b = atoi(carray2);
      
      dpdt_a_str = serialIn.substring(12, 15);
      char carray3[6];                       // magic needed to convert string to a number 
      dpdt_a_str.toCharArray(carray3, sizeof(carray3));
      dpdt_a = atoi(carray3);
      
      dpdt_b_str = serialIn.substring(16, 19);
      char carray4[6];                       // magic needed to convert string to a number 
      dpdt_b_str.toCharArray(carray4, sizeof(carray4));
      dpdt_b = atoi(carray4);
      
      //SPDT Relay Control
      PORTA = spdt_a;  //Write to SPDT A register
      PORTC = spdt_b;  //Write to SPDT B register
      //DPDT Relay Control
      PORTL = dpdt_a;  //Write to DPDT A register
      PORTK = dpdt_b;  //Write to DPDT B register 
      
      Serial.print("spdt_a: ");
      Serial.println(spdt_a, BIN);
      Serial.print("spdt_b: ");
      Serial.println(spdt_b, BIN);
      Serial.print("dpdt_a: ");
      Serial.println(dpdt_a, BIN);
      Serial.print("dpdt_b: ");
      Serial.println(dpdt_b, BIN);
      
    }
    else if(serialIn.charAt(2) == 'V'){//ADC Voltage Read Command
    }
    serialIn = "";  //Clear Serial Input String
  }
  //RETURN FEEDBACK
  delay(500);
}




