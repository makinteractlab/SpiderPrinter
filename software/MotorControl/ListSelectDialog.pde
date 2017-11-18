import controlP5.*;
import processing.serial.*;
import javax.swing.*;



interface SelectionAction
{
  void onSelection (String selection);
}


public class ListSelectDialog extends PApplet {

  private ControlP5 controlP5;
  private ListBox list;
  private String [] listOptions;
  private SelectionAction onSelectionAction;


  ListSelectDialog (String listName, String [] listOptions, SelectionAction action) {
    super();
    this.listOptions = listOptions;
    onSelectionAction= action;

    // init
    PApplet.runSketch(new String[] {this.getClass().getName()}, this);
  }

  public void setup() {
    controlP5 = new ControlP5(this);
    list = controlP5.addListBox("listSelection", 0, 0, width, height);
    list.setItemHeight(23);
    for (int i = 0; i < listOptions.length; i++)
      list.addItem (listOptions[i], i);
  }
 
  void draw() {
    background(200);
  }

  void listSelection (int theValue) 
  {
    this.surface.setVisible(false);
    onSelectionAction.onSelection (listOptions[theValue]);
  }

  public void settings() {
    size(600, 300);
  }
}