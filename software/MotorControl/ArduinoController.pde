import processing.serial.*;
import cc.arduino.*;

public enum Direction {LEFT, RIGHT};
public enum ServoState {UP, DOWN};

class ArduinoController 
{
	Arduino arduino;
	Direction direction;
	ServoState servoState;
	volatile int delayMs;
	int stepMultiplier;

	public final int HOLDOFF_PIN = 9;
	public final int DIRECTION_PIN = 8;
	public final int PULSE_PIN = 7;
	public final int SERVO_PIN= 4;
	public final int DEFAULT_DELAY= 20;


	ArduinoController (PApplet app, String portName, int bins, int microsteps, boolean twoDivisions)
	{
		println (Arduino.list());
		try {
			arduino = new Arduino(app, portName, 57600);
			arduino.pinMode(HOLDOFF_PIN, Arduino.OUTPUT);
			arduino.pinMode(DIRECTION_PIN, Arduino.OUTPUT);
			arduino.pinMode(PULSE_PIN, Arduino.OUTPUT);
		
			arduino.pinMode(SERVO_PIN, Arduino.SERVO);
			servoUp();

			setLeftDirection();
			delayMs= 1 ; //DEFAULT_DELAY;

			stepMultiplier= microsteps/bins;
			if(twoDivisions) stepMultiplier*= 2;
			println("Ready");

		}catch (Exception e)
		{
			println ("Port occupied");
			System.exit(0);
		}
	}

	void detachMotor()
	{
		arduino.digitalWrite(HOLDOFF_PIN, Arduino.HIGH);
	}

	void attachMotor()
	{
		arduino.digitalWrite(HOLDOFF_PIN, Arduino.LOW);
	}

	void setSpeed(int ms)
	{
		//delayMs= ms;
	}

	void setLeftDirection()
	{
		if (direction == Direction.LEFT) return;
		direction= Direction.LEFT;
		arduino.digitalWrite (DIRECTION_PIN, Arduino.LOW);
	}

	void setRightDirection()
	{
		if (direction == Direction.RIGHT) return;
		direction= Direction.RIGHT;
		arduino.digitalWrite (DIRECTION_PIN, Arduino.HIGH);
	}

	void toggleDirection()
	{
		if (direction == Direction.LEFT) setRightDirection();
		else setLeftDirection();
	}

	void setDirection (Direction dir)
	{
		if (dir == Direction.LEFT) setLeftDirection();
		else setRightDirection();
	}

	void stepOnceLeft()
	{
		setDirection (Direction.LEFT);
		rotatePlatformRawStep (1);
	}

	void stepOnceRight()
	{
		setDirection (Direction.RIGHT);
		rotatePlatformRawStep(1);
	}

	void rotatePlatform (final int steps, Direction direction)
	{
		setDirection (direction);
		rotatePlatform (abs(steps));
	}

	void actuateServoToAngle (int angle)
	{
		arduino.servoWrite(SERVO_PIN, angle);
	}

	void servoUp()
	{
		servoState= ServoState.UP;
		actuateServoToAngle(135);
	}

	void servoDown()
	{
		servoState= ServoState.DOWN;
		actuateServoToAngle(45);
	}

	void toggleServo ()
	{
		if (servoState == ServoState.UP) servoDown();
		else servoUp();
	}


	private void rotatePlatform (final int steps)
	{
		try
		{
			Thread t= new Thread (new Runnable() { 
				public void run ()
				{
					arduino.digitalWrite(HOLDOFF_PIN, Arduino.LOW);
					for (int i=0; i<abs(steps)*stepMultiplier; i++) step();
				}});

			t.start();
			t.join();

		}catch (Exception e){}	
	}


	private void rotatePlatformRawStep (final int steps)
	{
		try
		{
			Thread t= new Thread (new Runnable() { 
				public void run ()
				{
					arduino.digitalWrite(HOLDOFF_PIN, Arduino.LOW);
					for (int i=0; i<abs(steps); i++) step();
				}});

			t.start();
			t.join();

		}catch (Exception e){}	
	}

	private void step()
	{
		arduino.digitalWrite(PULSE_PIN, Arduino.HIGH);
		waitms (delayMs);
		arduino.digitalWrite(PULSE_PIN, Arduino.LOW);
		waitms (delayMs);
	}

	private void waitms (int msDuration)
	{
		try
		{
			Thread.sleep(msDuration);
		} catch (Exception e){}
	}
}
