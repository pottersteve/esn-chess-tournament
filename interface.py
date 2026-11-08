import csv
import tkinter as tk
from tkinter import messagebox
from main import generate_schedule
import tracker

def load_data():
    participants_all = []
    elos = []
    with open('participants.csv', mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2:
                participants_all.append(row[0].strip())
                elos.append(int(row[1].strip()))
    return participants_all, elos

class TournamentApp:
    def __init__(self, root, participants, tournament_data):
        self.root = root
        self.participants = participants
        self.tournament_data = tournament_data
        
        # Application State
        self.current_round_index = 0
        self.player_stats = tracker.init_stats(participants)
        self.tracked_matches = []
        
        # Setup Bottom Frame (Button)
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        self.save_btn = tk.Button(
            self.bottom_frame, text="Save & Next Round", 
            font=("Arial", 12, "bold"), bg="#27ae60", fg="white", 
            command=self.save_and_next, height=2
        )
        self.save_btn.pack(fill="x")

        # Setup Scrollable UI Area
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
        
        # Draw the first round
        self.render_round()

    def render_round(self):
        # Clear out previous round's widgets
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Check if the tournament is over
        if self.current_round_index >= len(self.tournament_data):
            tk.Label(self.main_frame, text="🏆 Tournament Complete! 🏆", font=("Arial", 18, "bold"), fg="#f39c12").pack(pady=50)
            tk.Label(self.main_frame, text="All results are saved in tournament_results.csv", font=("Arial", 12)).pack()
            self.save_btn.config(state="disabled", text="Finished", bg="gray")
            return
            
        # Get data for the current round
        r = self.tournament_data[self.current_round_index]
        self.tracked_matches = []
        
        # Render Header
        tk.Label(self.main_frame, text=f"--- ROUND {r['round']} ---", font=("Arial", 16, "bold"), fg="#2c3e50").grid(row=0, column=0, columnspan=6, pady=(0, 20))
        
        current_row = 1
        for m in r["matches"]:
            result_var = tk.IntVar(value=-1)
            self.tracked_matches.append({
                "p1": m["p1"], "p2": m["p2"], "var": result_var
            })
            
            # Render Table and Players
            tk.Label(self.main_frame, text=f"Table {m['table']}:", font=("Arial", 11, "bold")).grid(row=current_row, column=0, padx=10, pady=8, sticky="e")
            tk.Label(self.main_frame, text=f"{m['p1']} ({m['p1_elo']})", font=("Arial", 11)).grid(row=current_row, column=1, padx=5, pady=8, sticky="e")
            
            # Interactive Buttons
            tk.Radiobutton(self.main_frame, text="Win", variable=result_var, value=1, fg="green").grid(row=current_row, column=2, padx=5)
            tk.Radiobutton(self.main_frame, text="Draw", variable=result_var, value=0, fg="blue").grid(row=current_row, column=3, padx=5)
            tk.Radiobutton(self.main_frame, text="Win", variable=result_var, value=2, fg="green").grid(row=current_row, column=4, padx=5)
            
            tk.Label(self.main_frame, text=f"{m['p2']} ({m['p2_elo']})", font=("Arial", 11)).grid(row=current_row, column=5, padx=5, pady=8, sticky="w")
            current_row += 1
            
        # Render Sitting Out
        if r["sitting_out"]:
            tk.Label(self.main_frame, text=f"Sitting out: {', '.join(r['sitting_out'])}", fg="#d35400", font=("Arial", 10, "italic")).grid(row=current_row, column=0, columnspan=6, pady=20)
            
        # Reset scroll position to top for the new round
        self.canvas.yview_moveto(0)

    def save_and_next(self):
        # Optional UX check: Warn if a match doesn't have a result selected
        unscored = sum(1 for m in self.tracked_matches if m["var"].get() == -1)
        if unscored > 0:
            if not messagebox.askyesno("Missing Scores", f"{unscored} match(es) missing results. Proceed anyway?"):
                return
                
        # Save results to CSV
        saved_file = tracker.update_and_save(self.player_stats, self.tracked_matches)
        
        # Confirm and increment round
        messagebox.showinfo("Round Saved", f"Round {self.current_round_index + 1} scores updated in {saved_file}!")
        self.current_round_index += 1
        
        # Redraw UI with next round
        self.render_round()

def launch_app():
    participants, elos = load_data()
    matches = 5
    tables = 18
    
    # Pre-calculate all rounds logic from main.py
    tournament_data, _ = generate_schedule(participants, elos, matches, tables)
    
    root = tk.Tk()
    root.title("Tournament Match Tracker")
    root.geometry("650x700")
    
    # Boot up the interactive application
    app = TournamentApp(root, participants, tournament_data)
    root.mainloop()

if __name__ == "__main__":
    launch_app()