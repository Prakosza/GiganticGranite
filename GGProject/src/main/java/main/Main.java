package main;

import gui.simpleWindow.RunSimpleWindow;
import transmission.Client;
import gui.tray.TrayGUI;
import keylistener.GlobalKeyListener;

public class Main {
	public static void main(String args[]) {
		//TODO show logo or sth
		new RunSimpleWindow();
		new GlobalKeyListener().start();
		new TrayGUI();
		new Client();
		TrayGUI.showTooltipBalloon("Ready to work :)");
	}
}
