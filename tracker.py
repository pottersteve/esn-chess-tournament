import csv
import os

def init_stats(participants):
    return {p: {"points": 0.0, "matches_played": 0} for p in participants if p != "Bye"}

def update_and_save(player_stats, match_data, filename="tournament_results.csv"):
    for match in match_data:
        p1 = match["p1"]
        p2 = match["p2"]
        result = match["var"].get()
        
        if result != -1 and p1 != "Bye" and p2 != "Bye":
            player_stats[p1]["matches_played"] += 1
            player_stats[p2]["matches_played"] += 1
            
            if result == 1:
                player_stats[p1]["points"] += 1.0
            elif result == 2:
                player_stats[p2]["points"] += 1.0
            elif result == 0:
                player_stats[p1]["points"] += 0.5
                player_stats[p2]["points"] += 0.5

    # Sort players by points (highest first)
    sorted_players = sorted(player_stats.items(), key=lambda x: x[1]['points'], reverse=True)
    
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Player", "Points", "Matches Played"])
        for rank, (name, stats) in enumerate(sorted_players, start=1):
            writer.writerow([rank, name, stats["points"], stats["matches_played"]])
            
    return filename, sorted_players

def clear_knockout_file(filename="knockout_results.csv"):
    """Resets the knockout CSV at the start of Stage 2 so old tournaments don't mix."""
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Bracket Stage", "Player 1", "Player 2", "Winner Advancing"])

def save_knockout_round(round_name, match_data, filename="knockout_results.csv"):
    """Appends the results of 16, 8, 4, and 2 directly into the file as they happen."""
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for match in match_data:
            p1 = match["p1"]
            p2 = match["p2"]
            res = match["var"].get()
            
            if res == 1:
                winner = p1
            elif res == 2:
                winner = p2
            else:
                winner = "Unresolved (Default P1)"
                
            writer.writerow([round_name, p1, p2, winner])