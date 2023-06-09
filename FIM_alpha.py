import hashlib
import tkinter as tk
from tkinter import filedialog
from tkinter import *
import os
import xlsxwriter
import datetime
import threading
import json
import requests
import exifread
import time
import winreg
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import moviepy.editor as mp

global path
method_buttons_created = False
threads = []
flag = True

def monitor_gui():
    def stop_all_threads():
        global flag
        flag = False
        for t in threads:
            t.join()
        flag = True
        

    def select_file_folder():
        global path
        path = filedialog.askopenfilename() 
        terminal.config(state='normal')
        terminal.insert(tk.END, f"Selected path: {path}\n")
        terminal.config(state='disabled')
        if os.path.isdir(path):
            creation_button.config(state='normal')
        else:
            creation_button.config(state='disabled')

    def select_folder(): 
        global path
        path = filedialog.askdirectory()  
        terminal.config(state='normal')
        terminal.insert(tk.END, f"Selected path: {path}\n")
        terminal.config(state='disabled')
        if os.path.isdir(path):
            creation_button.config(state='normal')
        else:
            creation_button.config(state='disabled')

    def select_method():
        global method_buttons_created
        if not method_buttons_created:
            method1_button = tk.Button(root, text="Hash Comparison", command=lambda: hash_monitoring())
            method1_button.place(x=420, y=420)
            method2_button = tk.Button(root, text="Directory Monitoring", command=lambda: directory_monitoring())
            method2_button.place(x=560, y=420)
            method3_button = tk.Button(root, text="Virus Total Scan", command=lambda: virustotal_scan())
            method3_button.place(x=875, y=420)
            method4_button = tk.Button(root, text="Metadata Monitoring", command=lambda: metadata_monitoring())
            method4_button.place(x=715, y=420)
            method_buttons_created = True
        else:
            terminal.config(state='normal')
            terminal.insert(tk.END, "Method buttons already created\n")
            terminal.config(state='disabled')

    def hash_monitoring():
        global path
        terminal.config(state='normal')
        terminal.insert(tk.END, "Hash Monitoring Selected\n")
        terminal.insert(tk.END, f"{path} is the path\n")
        thread = threading.Thread(target=hash_loop)
        threads.append(thread)
        thread.start()

    def hash_loop():
        # Calculate the initial hash of the file
        with open(path, 'rb') as f:
            initial_hash = hashlib.sha256(f.read()).hexdigest()
        while flag:
            with open(path, 'rb') as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            if current_hash != initial_hash:
                terminal.insert(tk.END, f"{path} has been modified!\n")
            else:
                terminal.insert(tk.END, f"File Unchanged\n")
            initial_hash = current_hash
            time.sleep(3)  # Wait n seconds before checking again

    def directory_monitoring():
        global path
        terminal.config(state='normal')
        terminal.insert(tk.END, "Directory Monitoring Selected\n")
        terminal.insert(tk.END, f"{path} is the path\n")
        thread = threading.Thread(target=directory_loop, args=(path,))  # Using a thread
        threads.append(thread)
        thread.start()

    class TkinterHandler(logging.Handler):  # custom class to handle tkinter integration for logging+watchdog lib
        def __init__(self, terminal):
            super().__init__()
            self.terminal = terminal

        def emit(self, record):
            msg = self.format(record)
            self.terminal.config(state='normal')
            self.terminal.insert(tk.END, msg + "\n")
            self.terminal.config(state='disabled')

    def directory_loop(path):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        logging.getLogger().addHandler(TkinterHandler(terminal))

        pathi = path
        event_handler = LoggingEventHandler()
        observer = Observer()
        observer.schedule(event_handler, pathi, recursive=True)
        observer.start()
        try:
            while flag:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()

    def virustotal_scan():
        global path
        terminal.config(state='normal')
        terminal.insert(tk.END, "Virus Total Scan Selected\n")
        terminal.insert(tk.END, f"{path} is the path\n")
        thread = threading.Thread(target=check_file_with_virustotal())  # Using a thread
        threads.append(thread)
        thread.start()

    def check_file_with_virustotal():
        # Calculate the hash of the file
        with open(path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        # Send the hash to VirusTotal's API
        params = {'apikey': '254f3d3e6e6d9dd71b87276804e0a3d1b39108176dfae6aabb8141fa6707ad96', 'resource': file_hash}
        response = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params)

        # Save the JSON response to a file
        with open(f"{path}_json", 'w') as json_file:
            json.dump(response.json(), json_file)

        # Print the response in the terminal widget
        terminal.insert(tk.END, f"VirusTotal JSON response for {path}:\n")
        # terminal.insert(tk.END, json.dumps(response.json(), indent=4))

        # Extract the relevant information from the json response
        data = response.json()
        if data['response_code'] == 1:
            positives = data['positives']
            total = data['total']
            permalink = data['permalink']
            if positives > 0:
                terminal.insert(tk.END, f"File is malicious. {positives} out of {total} vendors detected it. \n "
                                        f"Permalink: {permalink}")
            else:
                terminal.insert(tk.END, f"File is not malicious. Only {positives} out of {total} vendors detected it. "
                                        f"\n Permalink: {permalink}")
        else:
            terminal.insert(tk.END, f"File not found on VirusTotal, Not Malicious")

    def metadata_monitoring():
        global path
        terminal.config(state='normal')
        terminal.insert(tk.END, "Metadata Monitoring Selected\n")
        terminal.insert(tk.END, f"{path} is the path\n")
        thread = threading.Thread(target=meta_loop)  # Using a thread
        threads.append(thread)
        thread.start()

    def meta_loop():

        previous_size = 0
        previous_timestamp = 0
        previous_metadata = {}

        while flag:
            current_size = os.path.getsize(path)
            current_timestamp = os.path.getmtime(path)
            if current_size != previous_size:
                terminal.insert(tk.END, f"Changes detected at {time.ctime(current_timestamp)}\n")
                terminal.insert(tk.END, f"Verified File Size was  {previous_size}, current File size is "
                                        f"{current_size}\n")
                previous_size = current_size
            if current_timestamp != previous_timestamp:
                terminal.insert(tk.END, f"Changes detected at {time.ctime(current_timestamp)}\n")
                terminal.insert(tk.END, f"previously last modified at {previous_timestamp}, current modification at "
                                        f"{current_timestamp}\n")
                previous_timestamp = current_timestamp

            if path.endswith('.jpg') or path.endswith('.jpeg') or path.endswith('.png') or path.endswith('.gif'):
                with open(path, 'rb') as f:
                    tags = exifread.process_file(f)
                    for tag in tags.keys():
                        if tag not in previous_metadata.keys() or tags[tag].values != previous_metadata[tag]:
                            terminal.insert(tk.END, f"Metadata {tag} has been changed\n")
                            previous_metadata[tag] = tags[tag].values

            elif path.endswith('.mp4') or path.endswith('.avi') or path.endswith('.mkv') or path.endswith('.webm') \
                    or path.endswith('.mp3'):
                video = mp.VideoFileClip(path)
                video_duration = video.duration
                video_fps = video.fps
                video_size = video.size

                with open(path, 'rb') as f:
                    tags = exifread.process_file(f)
                    for tag in tags.keys():
                        if tag not in previous_metadata.keys() or tags[tag].values != previous_metadata[tag]:
                            terminal.insert(tk.END, f"Metadata {tag} has been changed\n")
                            previous_metadata[tag] = tags[tag].values

                
            time.sleep(3)



    def callback(registry_hive, registry_key, event_type, name, old_data, new_data):
        print("Registry Event:")
        print("Hive:", registry_hive)
        print("Key:", registry_key)
        print("Event Type:", event_type)
        print("Name:", name)
        print("Old Data:", old_data)
        print("New Data:", new_data)


    def win_monitoring():
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE", access=winreg.KEY_NOTIFY)
        winreg.NotifyChangeKeyValue(key, True, winreg.REG_NOTIFY_CHANGE_NAME |
                            winreg.REG_NOTIFY_CHANGE_LAST_SET, callback)


    def save_logs():
        terminal.config(state='normal')
        terminal.insert(tk.END, "save logs\n")
        terminal.config(state='disabled')
        log_text = terminal.get("1.0", tk.END)
        log_list = log_text.split("\n")
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Workbook", "*.xlsx")])
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, "Serial No.")
        worksheet.write(0, 1, "Time")
        worksheet.write(0, 2, "Date")
        worksheet.write(0, 3, "Output")
        for i, log in enumerate(log_list):
            if log != "":
                current_time = str(datetime.datetime.now().time())[:8]
                current_date = str(datetime.date.today())
                worksheet.write(i + 1, 0, i + 1)
                worksheet.write(i + 1, 1, current_time)
                worksheet.write(i + 1, 2, current_date)
                worksheet.write(i + 1, 3, log)
        workbook.close()
        terminal.config(state='normal')
        terminal.insert(tk.END, "Logs saved to logs.xlsx\n")
        terminal.config(state='disabled')

    root = tk.Tk()
    root.geometry("1400x720")
    root.title("File Integrity Monitor")

    browse_button = tk.Button(root, text="Browse(File)", command=select_file_folder)
    browse_button.place(x=260, y=20)
    browse_button.config(height=2, width=14)

    browse_button = tk.Button(root, text="Browse(Directory)", command=select_folder)
    browse_button.place(x=260, y=80)
    browse_button.config(height=2, width=14)

    select_method_button = tk.Button(root, text="Select Method", command=select_method)
    select_method_button.place(x=260, y=140)
    select_method_button.config(height=2, width=14)
    
    save_logs_button = tk.Button(root, text="Save Logs", command=save_logs)
    save_logs_button.place(x=260, y=200)
    save_logs_button.config(height=2, width=14)

    creation_button = tk.Button(root, text="Monitor Creation", state='disabled')
    creation_button.place(x=260, y=260)
    creation_button.config(height=2, width=14)

    kill_thread_button = tk.Button(root, text="Stop Monitoring", command=stop_all_threads)
    kill_thread_button.place(x=260, y=320)
    kill_thread_button.config(height=2, width=14)

    
    

    terminal = tk.Text(root)
    terminal.pack()
    terminal.config(state='disabled')

    root.mainloop()


monitor_gui()

# TO DO
# file permissions/ownership monitoring!
# GUI visual improvements!
