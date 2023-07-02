// BEATRIX firmware 1.0
// Author: Uriel Martinez-Hernandez
// date: 12-06-2023

// Multimodal Interaction and Robot Active Perception (inte-R-action) Lab
// University of Bath

// BEATRIX firmware - beta version 1.0
// Bath opEn humAnoid for Teaching and Research in robotICS(X)

#include <AccelStepper.h>
#include <MultiStepper.h>

// Define pins for stepper motor of robot neck
// motor X
#define X_STEP_PIN 2          
#define X_DIR_PIN 5
// motor Y
#define Y_STEP_PIN 3
#define Y_DIR_PIN 6
// motor Z
#define Z_STEP_PIN 4
#define Z_DIR_PIN 7
// pin to enable/disable all motors
#define ENABLE_PIN 8

// maximum number of characters for commands
#define MAX_SIZE_COMMAND 20
// maximum number of paramater for each command
#define MAX_NUM_PARAMETERS 20
// maximum motor speed
#define MAX_SPEED 200
// maximum motor acceleration
#define MAX_ACCEL 200

// creates object for motor X
AccelStepper stepperX(1, X_STEP_PIN, X_DIR_PIN); // (num. of motor, dir, step)
// creates object for motor Y
AccelStepper stepperY(1, Y_STEP_PIN, Y_DIR_PIN); // (num. of motor, dir, step)
// creates object for motor Z
AccelStepper stepperZ(1, Z_STEP_PIN, Z_DIR_PIN); // (num. of motor, dir, step)
// creates object to handle multiple motors
MultiStepper steppers;

// define the number of motors to handle simultaneously
long multiStepperPositions[3];

// array to store commands received
char commands_char[MAX_NUM_PARAMETERS][MAX_SIZE_COMMAND];
// counter for commands
int ncommand = 0;
// counter for parameters
int count = 0;
// gets characters
char current_char;
// stores the current status of a command
bool commandStatus = false;
// stores calibration status of the robot
int calibrationStatus = 0;

// temporary used for @MOVALL command
boolean inPositionX = false;
boolean inPositionY = false;   
boolean inPositionZ = false;


void setup()
{
    // initialise motors to move zero steps
    stepperX.move(0);
    stepperY.move(0);
    stepperZ.move(0);

    // initialise speed and acceleration for motor X
    stepperX.setMaxSpeed(MAX_SPEED);
    stepperX.setAcceleration(MAX_ACCEL);

    // initialise speed and acceleration for motor Y
    stepperY.setMaxSpeed(MAX_SPEED);
    stepperY.setAcceleration(MAX_ACCEL);

    // initialise speed and acceleration for motor Z
    stepperZ.setMaxSpeed(MAX_SPEED);
    stepperZ.setAcceleration(MAX_ACCEL);
  
    // Allocates all motors to MultiStepper to manage in corresponding commands
    steppers.addStepper(stepperX);
    steppers.addStepper(stepperY);
    steppers.addStepper(stepperZ);

    // set baudrate for communication with Arduino board
    Serial.begin(9600);
    // configures the enable_pin as output
    pinMode(ENABLE_PIN, OUTPUT);
    // initialise enable_pin as HIGH to disable the motors
    // HIGH: disable robot motors
    // LOW: enable robot motors
    digitalWrite(ENABLE_PIN, HIGH);
}


void loop()
{
    // if data is received, then it is stored in commands_char
    if( Serial.available() > 0 )
    {      
        for( int i = 0; i < MAX_NUM_PARAMETERS; i++ )
        {
            for( int j = 0; j < MAX_SIZE_COMMAND; j++ )
                commands_char[i][j] = '\0';
        }

        count = 0;
        ncommand = 0;

        // stores commmands and parameters in commands_char
        do
        {
            current_char = Serial.read();
            
            delay(3);

            if( current_char != ' ' )
            {
                commands_char[ncommand][count] = current_char;
                count++;
            }
            else
            {
                commands_char[ncommand][count] = '\0';
                count = 0;
                ncommand++;                
            }            
        }while( current_char != '\r' );

        // check if the command received is correct
        commandStatus = commandList(commands_char[0]);
        replyAcknowledge(commandStatus);

        // if the command is correct, then it is executed by the corresponding function
        if( commandStatus == true )
            replyAcknowledge(executeCommand(commands_char));

        // cleans the serial pipe
        Serial.flush();
    }

}    

/* Function for execution of commands */
bool executeCommand(char cmdReceived[][MAX_SIZE_COMMAND])
{
    int step_size_int[20];
    int abs_step_size_int[20];
    int speed_int[20];
    int xMotorPos = 0;
    int yMotorPos = 0;
    int zMotorPos = 0;

    /* Enable/disable motors */
    if( !strcmp(cmdReceived[0],"@ENMOTORS") )
    {
      if( !strcmp(cmdReceived[1],"ON\r") )
        digitalWrite(ENABLE_PIN, LOW);
      else if( !strcmp(cmdReceived[1],"OFF\r") )
        digitalWrite(ENABLE_PIN, HIGH);
      else
        return false;

      calibrationStatus = 0;

      return true;
    }
    /* Calibration of X axis */
    if( !strcmp(cmdReceived[0],"@CALX") )
    {
      return true;

/*        if( strcmp(cmdReceived[1]," ") )
        {
            step_size_int[0] = atoi(cmdReceived[1]);
             
            stepperX.move(step_size_int[0]);
            stepperX.setSpeed(MAX_SPEED);
      
            while( stepperX.distanceToGo() != 0 )
                stepperX.runSpeedToPosition();
                
            stepperX.move(0);
            stepperX.setSpeed(MAX_SPEED);
            stepperX.runSpeedToPosition();                
  
            return true;
        }
        else       
            return false;
*/
    }
    /* Calibration of Y axis */
    else if( !strcmp(cmdReceived[0],"@CALY") )
    {
      return true;
/*
        if( strcmp(cmdReceived[1]," ") )
        {
            step_size_int[0] = atoi(cmdReceived[1]);
              
            stepperY.move(step_size_int[0]);
            stepperY.setSpeed(MAX_SPEED);
      
            while( stepperY.distanceToGo() != 0 )
                stepperY.runSpeedToPosition();
                
            stepperY.move(0);
            stepperY.setSpeed(MAX_SPEED);
            stepperY.runSpeedToPosition();                
            
            return true;            
        }
        else
            return false;
*/
    }
    /* Calibration of Z axis */
    else if( !strcmp(cmdReceived[0],"@CALZ") )
    {
      return true;
/*
        if( strcmp(cmdReceived[1]," ") )
        {
            step_size_int[0] = atoi(cmdReceived[1]);
              
            stepperZ.move(step_size_int[0]);
            stepperZ.setSpeed(MAX_SPEED);
      
            while( stepperZ.distanceToGo() != 0 )
                stepperZ.runSpeedToPosition();
                
            stepperZ.move(0);
            stepperZ.setSpeed(MAX_SPEED);
            stepperZ.runSpeedToPosition();                

            return true;
        }
        else
            return false;
*/
    }
    /* Calibration - OK*/ 
    else if( !strcmp(cmdReceived[0],"@CALNOW\r") )
    {
        stepperX.setCurrentPosition(0);        
        stepperY.setCurrentPosition(0);        
        stepperZ.setCurrentPosition(0);
            
        calibrationStatus = 1;

        return true;
    }
    /* Move all axes to home position - OK*/
    else if( !strcmp(cmdReceived[0], "@MOVHOME\r") )
    {
        if( calibrationStatus == 1 )
        {
            multiStepperPositions[0] = 0;
            multiStepperPositions[1] = 0;
            multiStepperPositions[2] = 0;

            steppers.moveTo(multiStepperPositions);
//            steppers.run();
            steppers.runSpeedToPosition();
            delay(1000);

            stepperX.setCurrentPosition(stepperX.currentPosition());
            stepperY.setCurrentPosition(stepperY.currentPosition());
            stepperZ.setCurrentPosition(stepperZ.currentPosition());

            return true;
        }
        else
            return false;    
    }
    /* Stop all motors - OK*/
    else if( !strcmp(cmdReceived[0],"@STOPALL\r") )
    {
        stepperX.stop();
        stepperY.stop();
        stepperZ.stop();
    }
    /* Get position from X axis - OK*/
    else if( !strcmp(cmdReceived[0],"@GETXPOS\r") )
    {
        Serial.println(stepperX.currentPosition());
    }
    /* Get position from Y axis - OK*/
    else if( !strcmp(cmdReceived[0],"@GETYPOS\r") )
    {
        Serial.println(stepperY.currentPosition());
    }
    /* Get position from Z axis - OK*/
    else if( !strcmp(cmdReceived[0],"@GETZPOS\r") )
    {
        Serial.println(stepperZ.currentPosition());
    }
    /* Get position from all axis - OK*/
    else if( !strcmp(cmdReceived[0],"@GETALLPOS\r") )
    {
        xMotorPos = stepperX.currentPosition();
        yMotorPos = stepperY.currentPosition();
        zMotorPos = stepperZ.currentPosition();
        Serial.print("\n");
        Serial.print(xMotorPos);
        Serial.print(" ");
        Serial.print(yMotorPos);
        Serial.print(" ");
        Serial.print(zMotorPos);
        Serial.print("\n");

    }
    /* Relative movement of X axis - OK*/
    else if( !strcmp(cmdReceived[0],"@MOVRX") )
    {
        if( calibrationStatus == 1 )
        {
          if( strcmp(cmdReceived[1]," ") && strcmp(cmdReceived[2]," ") )
          {
              step_size_int[0] = atoi(cmdReceived[1]);           
              speed_int[0] = atoi(cmdReceived[2]);
                              
              if( speed_int[0] > MAX_SPEED )
                  speed_int[0] = MAX_SPEED;
                  
              stepperX.move(step_size_int[0]);
        
              while( stepperX.distanceToGo() != 0 )
                  stepperX.run();
                  
              stepperX.stop();
              stepperX.runToPosition();

              return true;
          }
          else
              return false;       
        }
        else       
            return false;
    }
    /* Relative movement of Y axis - OK*/
    else if( !strcmp(cmdReceived[0],"@MOVRY") )
    {
        if( calibrationStatus == 1 )
        {
          if( strcmp(cmdReceived[1]," ") && strcmp(cmdReceived[2]," ") )
          {
              step_size_int[0] = atoi(cmdReceived[1]);
              speed_int[0] = atoi(cmdReceived[2]);
               
              if( speed_int[0] > MAX_SPEED )
                  speed_int[0] = MAX_SPEED;

              stepperY.move(step_size_int[0]);
        
              while( stepperY.distanceToGo() != 0 )
                  stepperY.run();
                  
              stepperY.stop();
              stepperY.runToPosition();
    
              return true;
          }
          else
              return false;       
        }
        else       
            return false;
    }
    /* Relative movement of Z axis - OK*/
    else if( !strcmp(cmdReceived[0],"@MOVRZ") )
    {
        if( calibrationStatus == 1 )
        {
          if( strcmp(cmdReceived[1]," ") && strcmp(cmdReceived[2]," ") )
          {
              step_size_int[0] = atoi(cmdReceived[1]);
              speed_int[0] = atoi(cmdReceived[2]);
               
              if( speed_int[0] > MAX_SPEED )
                  speed_int[0] = MAX_SPEED;

              stepperZ.move(step_size_int[0]);
        
              while( stepperZ.distanceToGo() != 0 )
                  stepperZ.run();
                  
              stepperZ.stop();
              stepperZ.runToPosition();
    
              return true;
          }
          else
              return false;       
        }
        else       
            return false;
    }
    /* Absolute movement of X axis - OK */
    else if( !strcmp(cmdReceived[0],"@MOVAX") )
    {
        if( calibrationStatus == 1 )
        {
          if( strcmp(cmdReceived[1]," ") && strcmp(cmdReceived[2]," ") )
          {
              step_size_int[0] = atoi(cmdReceived[1]);
              speed_int[0] = atoi(cmdReceived[2]);
              
              if( speed_int[0] > MAX_SPEED )
                  speed_int[0] = MAX_SPEED;

              stepperX.moveTo(step_size_int[0]);

              while( stepperX.currentPosition() != step_size_int[0] )
                  stepperX.run();
                  
              stepperX.stop();
              stepperX.runToPosition();
    
              return true;
          }
          else
              return false;       
        }
        else       
            return false;
    }
    /* Absolute movement of Y axis - OK */
    else if( !strcmp(cmdReceived[0],"@MOVAY") )
    {
        if( calibrationStatus == 1 )
        {
          if( strcmp(cmdReceived[1]," ") && strcmp(cmdReceived[2]," ") )
          {
              step_size_int[0] = atoi(cmdReceived[1]);
              speed_int[0] = atoi(cmdReceived[2]);
              
              if( speed_int[0] > MAX_SPEED )
                  speed_int[0] = MAX_SPEED;

              stepperY.moveTo(step_size_int[0]);

              while( stepperY.currentPosition() != step_size_int[0] )
                  stepperY.run();
                  
              stepperY.stop();
              stepperY.runToPosition();
    
              return true;
          }
          else
              return false;       
        }
        else       
            return false;
    }
    /* Absolute movement of Z axis - OK */
    else if( !strcmp(cmdReceived[0],"@MOVAZ") )
    {
        if( calibrationStatus == 1 )
        {
          if( strcmp(cmdReceived[1]," ") && strcmp(cmdReceived[2]," ") )
          {
              step_size_int[0] = atoi(cmdReceived[1]);
              speed_int[0] = atoi(cmdReceived[2]);
              
              if( speed_int[0] > MAX_SPEED )
                  speed_int[0] = MAX_SPEED;

              stepperZ.moveTo(step_size_int[0]);

              while( stepperZ.currentPosition() != step_size_int[0] )
                  stepperZ.run();
                  
              stepperZ.stop();
              stepperZ.runToPosition();
    
              return true;
          }
          else
              return false;       
        }
        else       
            return false;
    }
    /* Relative movement of all axes - OK*/
    else if( !strcmp(cmdReceived[0],"@MOVRALL") )
    {
        if( calibrationStatus == 1 )
        {
          if( strcmp(cmdReceived[1]," ") && strcmp(cmdReceived[2]," ") && strcmp(cmdReceived[3]," ") && strcmp(cmdReceived[4]," ") && 
              strcmp(cmdReceived[5]," ") && strcmp(cmdReceived[6]," ") && strcmp(cmdReceived[7]," ") && strcmp(cmdReceived[8]," "))
          {

              inPositionX = false;
              inPositionY = false;   
              inPositionZ = false;

              step_size_int[0] = atoi(cmdReceived[1]);
              step_size_int[1] = atoi(cmdReceived[2]);
              step_size_int[2] = atoi(cmdReceived[3]);
              speed_int[0] = atoi(cmdReceived[5]);
              speed_int[1] = atoi(cmdReceived[6]);
              speed_int[2] = atoi(cmdReceived[7]);
               
              if( speed_int[0] > MAX_SPEED )
                  speed_int[0] = MAX_SPEED;

              if( speed_int[1] > MAX_SPEED )
                  speed_int[1] = MAX_SPEED;

              if( speed_int[2] > MAX_SPEED )
                  speed_int[2] = MAX_SPEED;

              stepperX.move(step_size_int[0]);
              stepperY.move(step_size_int[1]);
              stepperZ.move(step_size_int[2]);
        
              do
              {          
                  if( stepperX.distanceToGo() != 0 )
                    stepperX.run();
                  else
                  {
                    stepperX.stop();
                    stepperX.runToPosition();
                    inPositionX = true;
                  }
        
                  if( stepperY.distanceToGo() != 0 )
                    stepperY.run();
                  else
                  {
                    stepperY.stop();
                    stepperY.runToPosition();
                    inPositionY = true;
                  }
    
                  if( stepperZ.distanceToGo() != 0 )
                    stepperZ.run();
                  else
                  {
                    stepperZ.stop();
                    stepperZ.runToPosition();
                    inPositionZ = true;
                  }

              }while( ( inPositionX != true ) || ( inPositionY != true ) || ( inPositionZ != true ) );

              delay(1000);

              stepperX.setCurrentPosition(stepperX.currentPosition());
              stepperY.setCurrentPosition(stepperY.currentPosition());
              stepperZ.setCurrentPosition(stepperZ.currentPosition());

              return true;
          }
          else
              return false;       
        }
        else       
            return false;
    }
    /* Absolute movement of all axes - OK*/
    else if( !strcmp(cmdReceived[0],"@MOVAALL") )
    {
        if( calibrationStatus == 1 )
        {
          if( strcmp(cmdReceived[1]," ") && strcmp(cmdReceived[2]," ") && strcmp(cmdReceived[3]," ") && strcmp(cmdReceived[4]," ") && 
              strcmp(cmdReceived[5]," ") && strcmp(cmdReceived[6]," ") && strcmp(cmdReceived[7]," ") && strcmp(cmdReceived[8]," "))
          {
              step_size_int[0] = atoi(cmdReceived[1]);
              step_size_int[1] = atoi(cmdReceived[2]);
              step_size_int[2] = atoi(cmdReceived[3]);
              speed_int[0] = atoi(cmdReceived[5]);
              speed_int[1] = atoi(cmdReceived[6]);
              speed_int[2] = atoi(cmdReceived[7]);
               
              if( speed_int[0] > MAX_SPEED )
                  speed_int[0] = MAX_SPEED;

              if( speed_int[1] > MAX_SPEED )
                  speed_int[1] = MAX_SPEED;

              if( speed_int[2] > MAX_SPEED )
                  speed_int[2] = MAX_SPEED;

              if( speed_int[3] > MAX_SPEED )
                  speed_int[3] = MAX_SPEED;

              multiStepperPositions[0] = step_size_int[0];
              multiStepperPositions[1] = step_size_int[1];
              multiStepperPositions[2] = step_size_int[2];

              steppers.moveTo(multiStepperPositions);
//              steppers.run();
              steppers.runSpeedToPosition();
              delay(1000);

              stepperX.setCurrentPosition(stepperX.currentPosition());
              stepperY.setCurrentPosition(stepperY.currentPosition());
              stepperZ.setCurrentPosition(stepperZ.currentPosition());
    
              return true;
          }
          else
              return false;       
        }
        else       
            return false;
    }
    else if( !strcmp(cmdReceived[0],"@COMSTATUS\r") )
    {
        //if( Serial )
        //    return true;
        //else
        //    return false;
        return true;
    }
    else if( !strcmp(cmdReceived[0],"@CALSTATUS\r") )
    {
        if( calibrationStatus == 1 )
            return true;
        else
            return false;
    }
    else
        return false;
}

/* Send reply ACK/NACK to client */
void replyAcknowledge(bool cmdStatus)
{
    if( cmdStatus == true )
        sendACK();
    else
        sendNACK();

    Serial.flush();
}

/* Print ACK message */
void sendACK()
{
    Serial.print("ACK\n");
}

/* Print NACK message */
void sendNACK()
{
    Serial.print("NACK\n");
}

/* Check the command received */
bool commandList(char *cmdReceived)
{
    char *commandArray[] = {"@CALSTART\r","@CALX\r","@CALY\r","@CALZ\r","@CALSTATUS\r","@CALNOW\r","@CALEND\r","@MOVHOME\r","@MOVRX","@MOVRY",
                            "@MOVRZ","@MOVAX","@MOVAY","@MOVAZ","@MOVRALL","@MOVAALL","@STOPALL\r","@GETALLPOS\r","@GETXPOS\r","@GETYPOS\r","@GETZPOS\r","@COMSTATUS\r", "@ENMOTORS"};
    int ncommands = 23;
    
    for( int i = 0; i < ncommands; i++ )
    {
        if( !strcmp(commandArray[i], cmdReceived) )
            return true;
    }
    
    return false;
}

