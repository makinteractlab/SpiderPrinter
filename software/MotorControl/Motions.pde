import java.util.*;

abstract class Action extends Observable implements Runnable {
	void actionCompleted () {
		setChanged();
		notifyObservers();
	}
}


class RotationAction extends Action {
	ArduinoController controller;
	int steps;
	Direction direction;

	RotationAction (ArduinoController controller, int steps, Direction direction) {
		this.controller = controller;
		this.steps = steps;
		this.direction = direction;
	}

	void run() {
		controller.rotatePlatform (steps, direction);
		actionCompleted();
	}
}


class ServoAction extends Action {
	ArduinoController controller;

	ServoAction (ArduinoController controller) {
		this.controller = controller;
	}

	void run() {
		controller.toggleServo();
		actionCompleted();
	}
}

class PrintAction extends Action {
	private String message;

	PrintAction (String message) {
		this.message = message;
	}

	void run() {
		println(message);
		actionCompleted();
	}
}




class ActionPause extends Action {
	int ms;

	ActionPause (int duration) {
		ms = duration;
	}

	void run() {
		try {
			Thread.sleep (ms);
		} catch (Exception e) {}

		actionCompleted();
	}
}





class ActionSequence implements Observer {
	ArrayList<Action> q;
	int current;
	boolean isDone;
	int totalInstructions;
	Thread currentAction;

	ActionSequence() {
		q = new ArrayList<Action>();
		current = 0;
		isDone = false;
	}

	void add (Action m) {
		if (m == null) return;
		q.add (m);
		m.addObserver(this);
		totalInstructions++;
	}

	int getInstructionsLeft()
	{
		return totalInstructions;
	}

	int getTotalInstructions()
	{
		return totalInstructions;
	}

	void stop()
	{
		q.clear();
	}

	void pause()
	{
		if (currentAction==null) return;
		currentAction.suspend();
	}

	void resume()
	{
		if (currentAction==null) return;
		currentAction.resume();	
	}

	void play() {
		current=0;
		isDone= false;
		currentAction= new Thread(q.get(current++));
		currentAction.start();
		totalInstructions--;
	}


	public void update (Observable obs, Object obj) {
		if (current < q.size())
		{
			currentAction= new Thread(q.get(current++));
			currentAction.start();
		}
		else isDone= true;
		totalInstructions--;
	}

	public boolean isDone() {
		return isDone;
	}
}
