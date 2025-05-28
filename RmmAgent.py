import tkinter as tk
import platform
import socket
import psutil
import requests
import threading

API_URL_REPORT = "http://backend-alb-482943522.us-east-1.elb.amazonaws.com/api/report"
API_URL_MANUAL_INVENTORY = "http://backend-alb-482943522.us-east-1.elb.amazonaws.com/api/manual_inventory"

class RMMAgent:
    def __init__(self, root):
        self.root = root
        root.title("NerdAgent")
        root.geometry("400x400")
        root.resizable(False, False)

        self.user_id = None
        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.show_user_input()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_user_input(self):
        self.clear_frame()
        tk.Label(self.frame, text="Enter your User Name:", anchor="w").pack(fill="x", pady=(0, 5))
        self.user_entry = tk.Entry(self.frame)
        self.user_entry.pack(fill="x", pady=(0, 10))

        tk.Button(self.frame, text="Submit", command=self.submit_user_id).pack()

        self.status_label = tk.Label(self.frame, text="", fg="red")
        self.status_label.pack(pady=(10, 0))

    def submit_user_id(self):
        uid = self.user_entry.get().strip()
        if not uid:
            self.status_label.config(text="User Name cannot be empty.")
            return
        self.user_id = uid
        self.show_main_tabs()

    def show_main_tabs(self):
        self.clear_frame()

        tab_frame = tk.Frame(self.frame)
        tab_frame.pack(fill="x", pady=(0, 10))

        tk.Button(tab_frame, text="My Computer", command=self.start_reporting).pack(side="left", padx=5)
        tk.Button(tab_frame, text="Add Inventory", command=self.show_manual_inventory).pack(side="left", padx=5)
        tk.Button(tab_frame, text="Change User", command=self.show_user_input).pack(side="left", padx=5)

        self.content_frame = tk.Frame(self.frame)
        self.content_frame.pack(fill="both", expand=True)

        self.start_reporting()

    def collect_data(self):
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except:
            ip = "N/A"
        data = {
            "user_id": self.user_id,
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "os_version": platform.version(),
            "cpu": platform.processor(),
            "memory_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
            "ip": ip,
        }
        return data

    def update_gui(self):
        data = self.collect_data()
        display = (
            f"User Name: {self.user_id}\n\n"
            f"Hostname: {data['hostname']}\n"
            f"OS: {data['os']} {data['os_version'][:15]}\n"
            f"CPU: {data['cpu'][:20]}\n"
            f"Memory: {data['memory_gb']} GB\n"
            f"IP: {data['ip']}"
        )
        self.info_label.config(text=display)

    def send_data(self):
        def _send():
            data = self.collect_data()
            try:
                response = requests.post(API_URL_REPORT, json=data, timeout=5)
                print(f"Sent data, status code: {response.status_code}")
            except Exception as e:
                print(f"Failed to send data: {e}")
        threading.Thread(target=_send, daemon=True).start()

    def update_and_send(self):
        self.update_gui()
        self.send_data()

    def schedule_refresh(self):
        self.update_and_send()
        self.root.after(60000, self.schedule_refresh)  # every 60 seconds

    def start_reporting(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.info_label = tk.Label(self.content_frame, text="", justify="left", anchor="w", font=("Courier", 10))
        self.info_label.pack(fill="both", expand=True)
        self.schedule_refresh()

    def show_manual_inventory(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="Add Manual Inventory Item", font=("Arial", 12, "bold")).pack(pady=(0,10))

        self.manual_fields = {}

        fields = ["Hostname", "OS", "CPU", "RAM (GB)", "Storage (GB)", "MAC Address"]
        for field in fields:
            frame = tk.Frame(self.content_frame)
            frame.pack(fill="x", pady=2)
            tk.Label(frame, text=field + ":", width=15, anchor="w").pack(side="left")
            entry = tk.Entry(frame)
            entry.pack(side="left", fill="x", expand=True)
            self.manual_fields[field] = entry

        tk.Button(self.content_frame, text="Submit", command=self.submit_manual_inventory).pack(pady=10)

        self.inventory_status = tk.Label(self.content_frame, text="", fg="green")
        self.inventory_status.pack()

    def submit_manual_inventory(self):
        payload = {
            "user_id": self.user_id,
            "hostname": self.manual_fields["Hostname"].get(),
            "os": self.manual_fields["OS"].get(),
            "cpu": self.manual_fields["CPU"].get(),
            "ram_gb": self.manual_fields["RAM (GB)"].get(),
            "storage_gb": self.manual_fields["Storage (GB)"].get(),
            "mac_address": self.manual_fields["MAC Address"].get()
        }

        try:
            response = requests.post(API_URL_MANUAL_INVENTORY, json=payload, timeout=5)
            if response.status_code == 200:
                self.inventory_status.config(text="Inventory saved successfully.", fg="green")
            else:
                self.inventory_status.config(text="Error saving inventory.", fg="red")
        except Exception as e:
            print(f"Error submitting manual inventory: {e}")
            self.inventory_status.config(text="Failed to connect to API.", fg="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = RMMAgent(root)
    root.mainloop()
