# app.py
import asyncio
import re
import aiohttp
import customtkinter as ctk
from typing import Optional, Set, List, Dict, Any

# Import from our other modules
from config import load_config, save_config
from utils import play_beep
from twitch_api import fetch_followed_streams

REFRESH_INTERVAL_SECONDS = 5

class TwitchMonitorApp(ctk.CTk):
    """The main GUI application class for the Twitch Stream Monitor."""
    
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__()

        self.loop = loop
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.online_streamers: Set[str] = set()
        self.refresh_interval_entry = REFRESH_INTERVAL_SECONDS
        
        self.title("Twitch Stream Monitor")
        self.geometry("500x600")
        ctk.set_appearance_mode("dark")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_widgets()
        self.populate_config()

    def create_widgets(self):
        """Creates and configures all GUI widgets."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Configuration Frame
        config_frame = ctk.CTkFrame(self)
        config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        config_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(config_frame, text="Client ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.client_id_entry = ctk.CTkEntry(config_frame, width=250)
        self.client_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(config_frame, text="Access Token:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.access_token_entry = ctk.CTkEntry(config_frame, width=250, show="*")
        self.access_token_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(config_frame, text="User ID:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.user_id_entry = ctk.CTkEntry(config_frame, width=250)
        self.user_id_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(config_frame, text="Refresh Interval:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.refresh_interval_entry = ctk.CTkEntry(config_frame, width=250)
        self.refresh_interval_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Controls Frame
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        controls_frame.grid_columnconfigure((0, 1), weight=1)

        self.start_button = ctk.CTkButton(controls_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.stop_button = ctk.CTkButton(controls_frame, text="Stop Monitoring", command=self.stop_monitoring, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Streamers List Frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Online Streamers")
        self.scrollable_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Status Bar
        self.status_label = ctk.CTkLabel(self, text="Status: Stopped", anchor="w")
        self.status_label.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
    def populate_config(self):
        """Populates entry fields from saved config."""
        config_data = load_config()
        self.client_id_entry.insert(0, config_data.get('client_id', ''))
        self.access_token_entry.insert(0, config_data.get('access_token', ''))
        self.user_id_entry.insert(0, config_data.get('user_id', ''))

    def start_monitoring(self):
        """Validates input, saves config, and starts the monitoring task."""
        client_id = self.client_id_entry.get()
        access_token = self.access_token_entry.get()
        user_id = self.user_id_entry.get()
        refresh_interval = int(self.refresh_interval_entry.get() or REFRESH_INTERVAL_SECONDS)

        if not all([client_id, access_token, user_id]):
            self.update_status("Error: All fields are required.", "red")
            return
        
        save_config(client_id, access_token, user_id, refresh_interval)
        
        self.is_monitoring = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.update_status("Status: Running...", "green")

        self.monitoring_task = asyncio.run_coroutine_threadsafe(
            self.monitor_loop(client_id, access_token, user_id, refresh_interval), self.loop
        )

    def stop_monitoring(self):
        """Stops the monitoring task and resets the UI."""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            self.monitoring_task = None
        
        self.is_monitoring = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.update_status("Status: Stopped")
        self.clear_streamer_list()
        self.online_streamers.clear()
        self.scrollable_frame.configure(label_text="Online Streamers")

    async def monitor_loop(self, client_id: str, token: str, user_id: str, refresh_interval: int):
        """The main async loop for fetching Twitch data periodically."""
        try:
            async with aiohttp.ClientSession() as session:
                # On the very first run, all online streamers are considered "new" for display purposes
                first_run = True
                while self.is_monitoring:
                    try:
                        data = await fetch_followed_streams(session, client_id, token, user_id)
                        current_streamers = {stream['user_name'] for stream in data}
                        
                        # MODIFICATION: Determine which streamers are newly online
                        newly_online = set()
                        if first_run:
                            newly_online = current_streamers
                            first_run = False
                        else:
                            newly_online = current_streamers - self.online_streamers

                        if newly_online and self.online_streamers: # Play sound only if there were pre-existing streamers
                            play_beep()

                        self.online_streamers = current_streamers
                        
                        # MODIFICATION: Pass the 'newly_online' set to the UI update function
                        self.after(0, self.update_streamer_list, data, newly_online)
                        
                    except Exception as e:
                        self.after(0, self.update_status, f"Error: {e}", "red")
                        await asyncio.sleep(10)
                    
                    await asyncio.sleep(refresh_interval)
        except asyncio.CancelledError:
            print("Monitoring task was cancelled.")
        finally:
            self.after(0, self.stop_monitoring)

    def update_streamer_list(self, streams: List[Dict[str, Any]], newly_online: Set[str]):
        """
        MODIFICATION: Updates the GUI list and highlights new streamers.
        This function now accepts a 'newly_online' set.
        """
        stream_count = len(streams)
        self.scrollable_frame.configure(label_text=f"Online Streamers ({stream_count})", label_font=("Arial", 30))
        self.clear_streamer_list()
        
        if not streams:
            ctk.CTkLabel(self.scrollable_frame, text="No followed streamers are online.", text_color="gray").pack(pady=10)
            return

        for stream in streams:
            user_name = stream.get('user_name', 'N/A')
            game_name = stream.get('game_name', 'No Category')
            viewer_count = stream.get('viewer_count', 0)
            
            # MODIFICATION: Check if the streamer is new and set display properties
            is_new = user_name in newly_online
            prefix = "[NEW] " if is_new else ""
            text_color = "yellow" if is_new else ctk.ThemeManager.theme["CTkLabel"]["text_color"]
            
            info_text = f"{prefix}{user_name} - {viewer_count:,} viewers\nPlaying: {game_name}"
            
            label = ctk.CTkLabel(
                self.scrollable_frame, 
                text=info_text, 
                anchor="w", 
                justify="left",
                text_color=text_color # Apply the conditional color
            )
            label.pack(fill="x", padx=10, pady=5)

    def clear_streamer_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def update_status(self, text: str, color: Optional[str] = None):
        theme_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        self.status_label.configure(text=text, text_color=color or theme_color)

    def on_closing(self):
        """Handles the window close event gracefully."""
        if self.is_monitoring:
            self.stop_monitoring()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.destroy()

if __name__ == "__main__":
    print("This module is intended to be run through main.py.")