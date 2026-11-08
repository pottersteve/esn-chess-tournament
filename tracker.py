import csv

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
            
    # Return both the filename and the sorted list for Stage 2 logic
    return filename, sorted_players