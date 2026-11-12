import csv
import tkinter as tk
from tkinter import messagebox
from main import generate_schedule
import tracker

def load_data():
    participants_all = []
    elos = []
    with open('participants.csv', mode='r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            # Only process rows that have 2 columns AND actually contain text
            if len(row) >= 2 and row[0].strip() != "" and row[1].strip() != "":
                participants_all.append(row[0].strip())
                elos.append(int(row[1].strip()))
    return participants_all, elos

class TournamentApp:
    def __init__(self, root, participants, tournament_data, tables, cutoff, stage2_matches):
        self.root = root
        self.tables = tables
        self.cutoff = cutoff
        self.stage2_matches = stage2_matches
        
        # State variables
        self.stage = 1
        self.current_round_index = 0
        self.tournament_data = tournament_data
        self.player_stats = tracker.init_stats(participants)
        self.tracked_matches = []
        self.live_standings = []
        
        # UI Setup
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        self.save_btn = tk.Button(
            self.bottom_frame, text="Save & Next Round", 
            font=("Arial", 12, "bold"), bg="#27ae60", fg="white", 
            command=self.save_and_next, height=2
        )
        self.save_btn.pack(fill="x")

        self.container = tk.Frame(root)
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

    def render_round(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Check if current stage is over
        if self.current_round_index >= len(self.tournament_data):
            if self.stage == 1:
                self.transition_to_stage_2()
                return
            else:
                tk.Label(self.main_frame, text="🏆 Tournament Complete! 🏆", font=("Arial", 18, "bold"), fg="#f39c12").pack(pady=50)
                tk.Label(self.main_frame, text="Final results are saved in tournament_results.csv", font=("Arial", 12)).pack()
                self.save_btn.config(state="disabled", text="Finished", bg="gray")
                return
            
        r = self.tournament_data[self.current_round_index]
        self.tracked_matches = []
        
        # Header
        stage_title = f"STAGE {self.stage} - ROUND {r['round']}"
        tk.Label(self.main_frame, text=stage_title, font=("Arial", 16, "bold"), fg="#2c3e50").grid(row=0, column=0, columnspan=6, pady=(0, 20))
        
        current_row = 1
        for m in r["matches"]:
            result_var = tk.IntVar(value=-1)
            self.tracked_matches.append({
                "p1": m["p1"], "p2": m["p2"], "var": result_var
            })
            
            # Subtext changes based on stage (Elo vs Points)
            val_type = "Elo" if self.stage == 1 else "Pts"
            rating1 = m['p1_rating'] if self.stage == 1 else m['p1_rating']/100
            rating2 = m['p2_rating'] if self.stage == 1 else m['p2_rating']/100
            
            tk.Label(self.main_frame, text=f"Table {m['table']}:", font=("Arial", 11, "bold")).grid(row=current_row, column=0, padx=10, pady=8, sticky="e")
            tk.Label(self.main_frame, text=f"{m['p1']} ({val_type}: {rating1})", font=("Arial", 11)).grid(row=current_row, column=1, padx=5, pady=8, sticky="e")
            
            tk.Radiobutton(self.main_frame, text="Win", variable=result_var, value=1, fg="green").grid(row=current_row, column=2, padx=5)
            tk.Radiobutton(self.main_frame, text="Draw", variable=result_var, value=0, fg="blue").grid(row=current_row, column=3, padx=5)
            tk.Radiobutton(self.main_frame, text="Win", variable=result_var, value=2, fg="green").grid(row=current_row, column=4, padx=5)
            
            tk.Label(self.main_frame, text=f"{m['p2']} ({val_type}: {rating2})", font=("Arial", 11)).grid(row=current_row, column=5, padx=5, pady=8, sticky="w")
            current_row += 1
            
        if r["sitting_out"]:
            tk.Label(self.main_frame, text=f"Sitting out: {', '.join(r['sitting_out'])}", fg="#d35400", font=("Arial", 10, "italic")).grid(row=current_row, column=0, columnspan=6, pady=20)
            
        self.canvas.yview_moveto(0)

    def transition_to_stage_2(self):
        # Calculate limit based on cutoff variable
        if isinstance(self.cutoff, float) and 0.0 < self.cutoff < 1.0:
            limit = int(len(self.live_standings) * self.cutoff)
        else:
            limit = int(self.cutoff)
            
        top_players = self.live_standings[:limit]
        
        stage2_participants = []
        stage2_metrics = []
        
        for name, stats in top_players:
            stage2_participants.append(name)
            # Multiply points by 100 to make the weight math work well in main.py 
            # (e.g., a score of 4.5 becomes 450)
            stage2_metrics.append(int(stats["points"] * 100))
            
        # Generate Stage 2 Schedule based on points
        self.tournament_data, _ = generate_schedule(stage2_participants, stage2_metrics, self.stage2_matches, self.tables)
        
        self.stage = 2
        self.current_round_index = 0
        messagebox.showinfo("Stage 2 Started", f"Stage 1 complete! Generating Stage 2 for the top {limit} players.")
        
        self.render_round()

    def save_and_next(self):
        unscored = sum(1 for m in self.tracked_matches if m["var"].get() == -1)
        if unscored > 0:
            if not messagebox.askyesno("Missing Scores", f"{unscored} match(es) missing results. Proceed anyway?"):
                return
                
        # Save results and fetch the updated standings
        saved_file, self.live_standings = tracker.update_and_save(self.player_stats, self.tracked_matches)
        
        self.current_round_index += 1
        self.render_round()

def launch_app():
    # --- CONFIGURABLE TOURNAMENT VARIABLES ---
    MATCHES_STAGE_1 = 6
    TABLES = 13
    
    # 0.5 = Top 50% advance. If you change this to an integer (e.g. 8), the top 8 players advance.
    CUTOFF = 0.5
    
    MATCHES_STAGE_2 = 3
    # -----------------------------------------
    
    participants, elos = load_data()
    tournament_data, _ = generate_schedule(participants, elos, MATCHES_STAGE_1, TABLES)
    
    root = tk.Tk()
    root.title("Multi-Stage Tournament Tracker")
    root.geometry("700x750")
    
    app = TournamentApp(root, participants, tournament_data, TABLES, CUTOFF, MATCHES_STAGE_2)
    root.mainloop()

if __name__ == "__main__":
    launch_app()