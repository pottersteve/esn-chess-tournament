import tkinter as tk
from tkinter import ttk

class LeaderboardTab:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        
        # Configure modern styles for the data table
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        style.configure("Treeview", font=("Arial", 11), rowheight=25)
        
        # Create the Treeview table optimized for 26 rows
        columns = ("Rank", "Player", "Points", "Played")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings", height=26)
        
        self.tree.heading("Rank", text="Rank")
        self.tree.heading("Player", text="Player")
        self.tree.heading("Points", text="Points")
        self.tree.heading("Played", text="Matches Played")
        
        self.tree.column("Rank", width=60, anchor="center")
        self.tree.column("Player", width=250, anchor="w")
        self.tree.column("Points", width=100, anchor="center")
        self.tree.column("Played", width=120, anchor="center")
        
        # Add a scrollbar just in case the window gets resized
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=20)

    def refresh(self, base_stats, pending_matches):
        """Calculates live scores without permanently saving them to the CSV yet."""
        
        # 1. Copy the base (saved) stats
        live_stats = {}
        for p, stats in base_stats.items():
            live_stats[p] = {"points": stats["points"], "played": stats["matches_played"]}
            
        # 2. Add points from the currently selected radio buttons
        for match in pending_matches:
            p1 = match["p1"]
            p2 = match["p2"]
            res = match["var"].get()
            
            if res != -1 and p1 != "Bye" and p2 != "Bye":
                if p1 in live_stats: live_stats[p1]["played"] += 1
                if p2 in live_stats: live_stats[p2]["played"] += 1
                
                if res == 1:
                    if p1 in live_stats: live_stats[p1]["points"] += 1.0
                elif res == 2:
                    if p2 in live_stats: live_stats[p2]["points"] += 1.0
                elif res == 0:
                    if p1 in live_stats: live_stats[p1]["points"] += 0.5
                    if p2 in live_stats: live_stats[p2]["points"] += 0.5
                    
        # 3. Sort players by points (highest first)
        sorted_players = sorted(live_stats.items(), key=lambda x: x[1]["points"], reverse=True)
        
        # 4. Clear the old table and insert updated data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for rank, (name, stats) in enumerate(sorted_players, start=1):
            self.tree.insert("", "end", values=(rank, name, stats["points"], stats["played"]))