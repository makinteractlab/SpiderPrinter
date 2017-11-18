import g4p_controls.*;

ArduinoController ardu;
MotionManager mm;
ListSelectDialog ld;
public final int MICROSTEPS = 5000;
public final int BINS = 200;
public final boolean ONE_DIVISIONS= false;
public final boolean TWO_DIVISIONS= !ONE_DIVISIONS;


void setup() {
	createGUI();
	selectPort();
}

void settings() {
	size(550, 300);
}


void draw() {
	background(230);
}





void init(String serialPort) {
	ardu = new ArduinoController(this, serialPort, BINS, MICROSTEPS, TWO_DIVISIONS);
}

void fileSelected(File selection) {
	if (selection == null) {
		println("Window was closed or the user hit cancel.");
	} else {
		mm = new MotionManager(ardu, selection.getAbsolutePath(), BINS);
	}
}

void selectPort() {
	new ListSelectDialog("Serial ports", Serial.list(), new SelectionAction() {
		public void onSelection (String selection) {
			init (selection);
		}
	});
}


void keyPressed() {
	if (ardu == null || mm == null) return;

	if (key == 's' || key=='S')  mm.startMotions();
	else if (key == 'x' || key=='X')  mm.stopMotions();
	else if (key == 'l' || key=='L')  ardu.stepOnceLeft();
	else if (key == 'r' || key=='R')  ardu.stepOnceRight();
	else if (key == 'u' || key=='U')  ardu.servoUp();
	else if (key == 'd' || key=='D')  ardu.servoDown();
	else if (key == '1')  ardu.rotatePlatform(1, Direction.LEFT);
	else if (key == '2')  ardu.rotatePlatform(1, Direction.RIGHT);
}