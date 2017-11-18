class MotionManager 
{
	private ArduinoController arduino;
	private ActionSequence sequence;
	private int bins;

	MotionManager (ArduinoController arduino, String inputFile, int totBins) 
	{
		if (arduino==null) throw new IllegalArgumentException();
		this.arduino= arduino;
		sequence= new ActionSequence();
		bins= totBins;

		println(inputFile);
		loadFile(inputFile);
	}

	void startMotions()
	{
		arduino.attachMotor();
		arduino.servoUp();
		sequence.play();
	}

	void stopMotions()
	{
		sequence.stop();
		arduino.servoUp();
		arduino.detachMotor();
	}

	private void loadFile (String inputFile)
	{
		String[] lines = loadStrings (inputFile);
		for (String s : lines) 
		{
			String [] tokens= splitTokens(s,",");
			if (tokens.length != 2) continue;
			int start= parseInt(tokens[0]);
			int end= parseInt(tokens[1]);
			int stepsRight= (end-start+bins) % bins;	
			int stepsLeft= (start-end+bins) % bins;
			Direction dir= Direction.RIGHT;
			if(stepsLeft <= stepsRight) dir= Direction.LEFT;
			int steps= min (stepsRight, stepsLeft);
			addToSequence(sequence, dir, steps);
		}
	}

	private void addToSequence (ActionSequence seq, Direction dir, int steps)
	{
		// println("Motion "+steps +" to " + dir);
		seq.add(new PrintAction("Motion "+steps +" to " + dir));
		seq.add(new RotationAction (ardu, steps, dir));
		seq.add (new ServoAction (ardu));
		seq.add(new ActionPause (500));
	}
}