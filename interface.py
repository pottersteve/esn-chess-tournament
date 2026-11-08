import csv
import tkinter as tk
from tkinter import scrolledtext
from main import generate_schedule

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

def launch_app():
    # Load data and run the pairing algorithm
    participants, elos = load_data()
    matches = 5
    tables = 18
    tournament_data, summary = generate_schedule(participants, elos, matches, tables)
    
    # Create the main application window
    root = tk.Tk()
    root.title("Tournament Schedule")
    root.geometry("600x700")
    root.configure(bg="#f0f0f0")
    
    # Create a scrollable text widget
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 11), bg="white")
    text_area.pack(expand=True, fill='both', padx=20, pady=20)
    
    # Define text styles
    text_area.tag_config("header", font=("Consolas", 14, "bold"), foreground="#2c3e50")
    text_area.tag_config("alert", foreground="#d35400", font=("Consolas", 11, "italic"))
    text_area.tag_config("summary_head", font=("Consolas", 14, "bold"), foreground="#27ae60")
    
    # Populate the interface with the match data
    for r in tournament_data:
        text_area.insert(tk.END, f"\n{'='*15} ROUND {r['round']} {'='*15}\n\n", "header")
        
        for m in r["matches"]:
            line = f"Table {m['table']:<2}: {m['p1']:<15} ({m['p1_elo']})  VS  {m['p2']:<15} ({m['p2_elo']})\n"
            text_area.insert(tk.END, line)
            
        if r["sitting_out"]:
            text_area.insert(tk.END, f"\nSitting out: {', '.join(r['sitting_out'])}\n", "alert")
            
        text_area.insert(tk.END, "\n")
        
    # Populate summary
    text_area.insert(tk.END, f"{'='*10} TOURNAMENT SUMMARY {'='*10}\n\n", "summary_head")
    for s in summary:
        text_area.insert(tk.END, f"{s['name']:<15}: Played {s['games']} matches\n")
        
    # Disable editing so it acts like a display interface
    text_area.configure(state='disabled')
    
    # Run the application
    root.mainloop()

if __name__ == "__main__":
    launch_app()