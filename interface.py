import csv
import random
import os
import tkinter as tk
from tkinter import ttk, messagebox
from main import generate_schedule
import tracker
import for_printing
import leaderboard

def load_data():
    participants_all = []
    elos = []
    with open('participants.csv', mode='r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2 and row[0].strip() != "" and row[1].strip() != "":
                participants_all.append(row[0].strip())
                elos.append(int(row[1].strip()))
    return participants_all, elos

def load_existing_schedule(filename="arbiter_schedule.csv"):
    tournament_data = []
    current_round = None
    
    with open(filename, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader) 
        
        for row in reader:
            if not row or not row[0].strip():
                continue
                
            if str(row[0]).startswith("--- ROUND"):
                round_num = int(row[0].replace("--- ROUND", "").replace("---", "").strip())
                current_round = {"round": round_num, "matches": [], "sitting_out": []}
                tournament_data.append(current_round)
                continue
                
            if len(row) > 1 and "Sitting Out:" in str(row[1]):
                sitting_str = row[2]
                if sitting_str:
                    current_round["sitting_out"] = [p.strip() for p in sitting_str.split(",")]
                continue
                
            if len(row) >= 8 and str(row[1]).isdigit():
                current_round["matches"].append({
                    "table": int(row[1]),
                    "p1": row[2], "p1_color": row[3], "p1_rating": int(row[4]),
                    "p2": row[5], "p2_color": row[6], "p2_rating": int(row[7])
                })
                
    return tournament_data

class TournamentApp:
    def __init__(self, root, participants, tournament_data):
        self.root = root
        
        self.stage = 1
        self.current_round_index = 0
        self.tournament_data = tournament_data
        self.player_stats = tracker.init_stats(participants)
        
        self.tracked_matches = []
        self.live_standings = []
        self.knockout_matches = []
        self.current_knockout_round_name = ""
        
        # 1. SETUP BOTTOM FRAME FIRST (So the button claims its space at the bottom)
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        self.save_btn = tk.Button(
            self.bottom_frame, text="Save & Next Round", 
            font=("Arial", 12, "bold"), bg="#27ae60", fg="white", 
            command=self.save_and_next, height=2
        )
        self.save_btn.pack(fill="x")

        # 2. SETUP TAB SYSTEM SECOND (So it safely fills the remaining space)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.matches_tab = tk.Frame(self.notebook)
        self.leaderboard_tab = tk.Frame(self.notebook)
        
        self.notebook.add(self.matches_tab, text="🏟️ Match Tracker")
        self.notebook.add(self.leaderboard_tab, text="🏆 Live Leaderboard")
        
        self.leaderboard_ui = leaderboard.LeaderboardTab(self.leaderboard_tab)

        # 3. SETUP SCROLLABLE UI INSIDE THE MATCHES TAB
        self.container = tk.Frame(self.matches_tab)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.container, borderwidth=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.main_frame = tk.Frame(self.canvas)
        
        self.main_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.render_round()

    def update_live_leaderboard(self):
        """Fired automatically every time a radio button is pressed."""
        self.leaderboard_ui.refresh(self.player_stats, self.tracked_matches)

    def render_round(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # ---------- STAGE 1: ROUND ROBIN ----------
        if self.stage == 1:
            if self.current_round_index >= len(self.tournament_data):
                self.transition_to_stage_2()
                return
                
            r = self.tournament_data[self.current_round_index]
            self.tracked_matches = []
            
            tk.Label(self.main_frame, text=f"STAGE 1 - ROUND {r['round']}", font=("Arial", 16, "bold"), fg="#2c3e50").grid(row=0, column=0, columnspan=6, pady=(0, 20))
            
            current_row = 1
            for m in r["matches"]:
                result_var = tk.IntVar(value=-1)
                self.tracked_matches.append({"p1": m["p1"], "p2": m["p2"], "var": result_var})
                
                tk.Label(self.main_frame, text=f"Table {m['table']}:", font=("Arial", 11, "bold")).grid(row=current_row, column=0, padx=10, pady=8, sticky="e")
                tk.Label(self.main_frame, text=f"{m['p1']} ({m['p1_color']})", font=("Arial", 11)).grid(row=current_row, column=1, padx=5, pady=8, sticky="e")
                
                # Added command to trigger live leaderboard update
                tk.Radiobutton(self.main_frame, text="Win", variable=result_var, value=1, fg="green", command=self.update_live_leaderboard).grid(row=current_row, column=2, padx=5)
                tk.Radiobutton(self.main_frame, text="Draw", variable=result_var, value=0, fg="blue", command=self.update_live_leaderboard).grid(row=current_row, column=3, padx=5)
                tk.Radiobutton(self.main_frame, text="Win", variable=result_var, value=2, fg="green", command=self.update_live_leaderboard).grid(row=current_row, column=4, padx=5)
                
                tk.Label(self.main_frame, text=f"{m['p2']} ({m['p2_color']})", font=("Arial", 11)).grid(row=current_row, column=5, padx=5, pady=8, sticky="w")
                current_row += 1
                
            if r["sitting_out"]:
                tk.Label(self.main_frame, text=f"Sitting out: {', '.join(r['sitting_out'])}", fg="#d35400", font=("Arial", 10, "italic")).grid(row=current_row, column=0, columnspan=6, pady=20)

        # ---------- STAGE 2: KNOCKOUT ----------
        elif self.stage == 2:
            if not self.knockout_matches:
                tk.Label(self.main_frame, text=f"🏆 {self.winner} Wins! 🏆", font=("Arial", 22, "bold"), fg="#f39c12").pack(pady=50)
                self.save_btn.config(state="disabled", text="Finished", bg="gray")
                return
                
            num_matches = len(self.knockout_matches)
            round_name = {8: "Round of 16", 4: "Quarterfinals", 2: "Semifinals", 1: "Final"}.get(num_matches, f"Knockout ({num_matches} Matches)")
            self.current_knockout_round_name = round_name

            tk.Label(self.main_frame, text=f"STAGE 2 - {round_name.upper()}", font=("Arial", 16, "bold"), fg="#e74c3c").grid(row=0, column=0, columnspan=5, pady=(0, 20))

            self.tracked_matches = []
            current_row = 1
            
            for i, match in enumerate(self.knockout_matches):
                p1, p2 = match["p1"], match["p2"]
                result_var = tk.IntVar(value=-1)
                self.tracked_matches.append({"p1": p1, "p2": p2, "var": result_var})
                
                tk.Label(self.main_frame, text=f"Match {i+1}:", font=("Arial", 11, "bold")).grid(row=current_row, column=0, padx=10, pady=8, sticky="e")
                tk.Label(self.main_frame, text=f"{p1} ({match['p1_color']})", font=("Arial", 11)).grid(row=current_row, column=1, padx=5, pady=8, sticky="e")
                
                # Added command to trigger live leaderboard update
                tk.Radiobutton(self.main_frame, text="Win P1", variable=result_var, value=1, fg="green", command=self.update_live_leaderboard).grid(row=current_row, column=2, padx=5)
                tk.Radiobutton(self.main_frame, text="Win P2", variable=result_var, value=2, fg="green", command=self.update_live_leaderboard).grid(row=current_row, column=3, padx=5)
                
                tk.Label(self.main_frame, text=f"{p2} ({match['p2_color']})", font=("Arial", 11)).grid(row=current_row, column=4, padx=5, pady=8, sticky="w")
                current_row += 1
                
        self.canvas.yview_moveto(0)
        
        # Ensure the leaderboard reflects the new blank round instantly
        self.update_live_leaderboard()

    def transition_to_stage_2(self):
        top_players = [name for name, stats in self.live_standings[:16]]
        while len(top_players) < 16:
            top_players.append("Bye")
            
        seeds = [0, 15, 7, 8, 3, 12, 4, 11, 1, 14, 6, 9, 2, 13, 5, 10]
        
        self.knockout_matches = []
        for i in range(0, 16, 2):
            colors = ["White", "Black"]
            random.shuffle(colors)
            self.knockout_matches.append({
                "p1": top_players[seeds[i]], 
                "p2": top_players[seeds[i+1]],
                "p1_color": colors[0],
                "p2_color": colors[1]
            })
            
        self.stage = 2
        tracker.clear_knockout_file() 
        messagebox.showinfo("Knockout Stage", "Stage 1 complete! Generating the Knockout Bracket based on highest points.")
        self.render_round()

    def save_and_next(self):
        unscored = sum(1 for m in self.tracked_matches if m["var"].get() == -1)
        if unscored > 0:
            if not messagebox.askyesno("Missing Scores", f"{unscored} match(es) missing results. Proceed anyway?"):
                return
                
        if self.stage == 1:
            saved_file, self.live_standings = tracker.update_and_save(self.player_stats, self.tracked_matches)
            self.current_round_index += 1
            self.render_round()
            
        elif self.stage == 2:
            tracker.save_knockout_round(self.current_knockout_round_name, self.tracked_matches)
            
            winners = []
            for m in self.tracked_matches:
                if m["var"].get() == 1:
                    winners.append(m["p1"])
                elif m["var"].get() == 2:
                    winners.append(m["p2"])
                else:
                    winners.append(m["p1"])
                    
            if len(winners) == 1:
                self.winner = winners[0]
                self.knockout_matches = []
            else:
                new_matches = []
                for i in range(0, len(winners), 2):
                    colors = ["White", "Black"]
                    random.shuffle(colors)
                    new_matches.append({
                        "p1": winners[i], 
                        "p2": winners[i+1],
                        "p1_color": colors[0],
                        "p2_color": colors[1]
                    })
                self.knockout_matches = new_matches
                
            self.render_round()

def launch_app():
    MATCHES_STAGE_1 = 6
    TABLES = 13
    
    root = tk.Tk()
    root.withdraw() 
    
    participants, elos = load_data()
    
    if os.path.exists("arbiter_schedule.csv"):
        recover = messagebox.askyesno(
            "Existing Schedule Found", 
            "A generated schedule (arbiter_schedule.csv) was found in this folder.\n\n"
            "Do you want to RECOVER this schedule? (Click Yes)\n"
            "Or generate a completely NEW tournament? (Click No)"
        )
    else:
        recover = False

    if recover:
        tournament_data = load_existing_schedule("arbiter_schedule.csv")
    else:
        tournament_data, _ = generate_schedule(participants, elos, MATCHES_STAGE_1, TABLES)
        for_printing.export_schedules_to_csv(participants, tournament_data)
        
    root.deiconify()
    root.title("Tournament Tracker")
    root.geometry("800x800") 
    
    app = TournamentApp(root, participants, tournament_data)
    root.mainloop()

if __name__ == "__main__":
    launch_app()