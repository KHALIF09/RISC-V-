# RISC-V
RISC-V Simulator

How to Install and Run

Follow the steps below to set up and run the RISC-V simulator with GUI.

⸻

Requirements

Make sure you have the following installed on your system:
	•	Python 3.8 or above

⸻

Step 1: Install Required Packages

Open terminal / command prompt and run:

pip install pyqt5
pip install pyqt5-tools

If pip points to Python 2, use:

pip3 install pyqt5 pyqt5-tools


⸻

Step 2: Project Structure

Place the project files in one folder like this:

riscv_simulator/
│── main.py
│── cpu.py
│── memory.py
│── decoder.py
│── gui.py
│── README.md


⸻

Step 3: Run the Simulator

Navigate to the folder in terminal and run:

python main.py

Or on some systems:

python3 main.py


⸻

Usage
	•	The GUI window will open after running the command.
	•	Load a RISC-V machine code program or enter instructions manually.
	•	Step through execution or run continuously.
	•	View registers and memory updates in real time.

⸻

Troubleshooting

Issue	Solution
ModuleNotFoundError: PyQt5	Run pip install pyqt5 again
GUI not opening	Make sure you run python main.py from project directory
Python not found	Install Python from python.org or use python3 command


⸻

Uninstall (Optional)

pip uninstall pyqt5


⸻

You’re Ready!

Now you can start experimenting with custom RISC-V instructions and learn CPU behavior visually.

If you need help improving the design or adding features like pipelines or forwarding, just ask! 🚀
