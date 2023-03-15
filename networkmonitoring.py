import tkinter as tk
import subprocess

def check_network_settings():
    # Get the current network settings
    result = subprocess.check_output(["ipconfig"])
    current_settings = result.decode("utf-8")

    # Compare the current settings with the previous settings
    try:
        with open("previous_settings.txt", "r") as file:
            previous_settings = file.read()
    except FileNotFoundError:
        previous_settings = ""

    if current_settings != previous_settings:
        # Update the previous settings
        with open("previous_settings.txt", "w") as file:
            file.write(current_settings)

        # Show the changes in the terminal
        changes = "Network settings changed:\n" + current_settings
        text.delete("1.0", tk.END)
        text.insert(tk.END, changes)

# Create the Tkinter GUI
root = tk.Tk()
root.title("File Integrity Monitor")

text = tk.Text(root, height=20, width=80)
text.pack()

check_network_settings_button = tk.Button(root, text="Check Network Settings", command=check_network_settings)
check_network_settings_button.pack()

root.mainloop()
