import csv

def export_schedules_to_csv(participants, tournament_data):
    """Generates the printable schedules for players and arbiters."""
    
    # 1. Player Schedules (Grouped by Player)
    with open("player_schedules.csv", mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["Player", "Round", "Table", "Piece Color", "Opponent"])
        
        # Sort players alphabetically for easy handout distribution
        for player in sorted(participants):
            if player == "Bye": 
                continue
                
            played_rounds = 0
            for r in tournament_data:
                for m in r["matches"]:
                    if m["p1"] == player:
                        writer.writerow([player, r["round"], m["table"], m["p1_color"], m["p2"]])
                        played_rounds += 1
                    elif m["p2"] == player:
                        writer.writerow([player, r["round"], m["table"], m["p2_color"], m["p1"]])
                        played_rounds += 1
                        
            # If a player has fewer matches than rounds, they sat out some rounds
            if played_rounds < len(tournament_data):
                writer.writerow([player, "Various", "N/A", "N/A", "Sitting Out"])
                
            # Blank line between players for easy cutting/reading
            writer.writerow([]) 

    # 2. Arbiter Master Schedule (Grouped by Round)
    with open("arbiter_schedule.csv", mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["Round", "Table", "Player 1", "P1 Color", "P1 Elo", "Player 2", "P2 Color", "P2 Elo"])
        
        for r in tournament_data:
            writer.writerow([f"--- ROUND {r['round']} ---", "", "", "", "", "", "", ""])
            for m in r["matches"]:
                writer.writerow([
                    r["round"], 
                    m["table"], 
                    m["p1"], m["p1_color"], m["p1_rating"],
                    m["p2"], m["p2_color"], m["p2_rating"]
                ])
                
            if r["sitting_out"]:
                writer.writerow([r["round"], "Sitting Out:", ", ".join(r["sitting_out"]), "", "", "", "", ""])
            writer.writerow([]) # Blank line between rounds