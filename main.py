import csv
import networkx as nx

def generate_schedule(participants, elos, matches, tables):
    # We add a unique 'id' to each player to avoid bugs if two people have the same name
    players = []
    for i in range(len(participants)):
        players.append({
            "id": i,
            "name": participants[i],
            "elo": elos[i],
            "played": set()
        })

    if len(players) % 2 != 0:
        players.append({"id": len(players), "name": "Bye", "elo": 0, "played": set()})

    tournament_data = []

    for round_num in range(1, matches + 1):
        G = nx.Graph()
        
        for p in players:
            G.add_node(p["id"])
            
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                p1 = players[i]
                p2 = players[j]
                
                if p2["id"] not in p1["played"]:
                    elo_score = 10000 - abs(p1["elo"] - p2["elo"])
                    games_played_penalty = (len(p1["played"]) + len(p2["played"])) * 100000
                    weight = elo_score - games_played_penalty
                    G.add_edge(p1["id"], p2["id"], weight=weight)
                    
        best_pairings_set = nx.max_weight_matching(G, maxcardinality=True)
        
        player_map = {p["id"]: p for p in players}
        proposed_tables = []
        
        for id1, id2 in best_pairings_set:
            p1 = player_map[id1]
            p2 = player_map[id2]
            combined_games = len(p1["played"]) + len(p2["played"])
            proposed_tables.append((combined_games, p1, p2))
            
        proposed_tables.sort(key=lambda x: x[0])
        
        table_count = 1
        paired_this_round = set()
        round_matches = []
        
        for combined_games, p1, p2 in proposed_tables:
            if table_count > tables:
                break 
                
            if p1["name"] != "Bye" and p2["name"] != "Bye":
                round_matches.append({
                    "table": table_count,
                    "p1": p1["name"], "p1_elo": p1["elo"],
                    "p2": p2["name"], "p2_elo": p2["elo"]
                })
                table_count += 1
            
            p1["played"].add(p2["id"])
            p2["played"].add(p1["id"])
            paired_this_round.add(p1["id"])
            paired_this_round.add(p2["id"])
            
        sitting_out = []
        for p in players:
            if p["id"] not in paired_this_round and p["name"] != "Bye":
                sitting_out.append(f"{p['name']} (Games: {len(p['played'])})")
                
        tournament_data.append({
            "round": round_num,
            "matches": round_matches,
            "sitting_out": sitting_out
        })

    # Summary data
    players.sort(key=lambda x: -x['elo'])
    summary = [{"name": p["name"], "games": len(p["played"])} for p in players if p["name"] != "Bye"]

    return tournament_data, summary

def main():
    # If run directly, behave exactly like the old script by printing to console
    participants_all = []
    elos = []

    with open('participants.csv', mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2:
                participants_all.append(row[0].strip())
                elos.append(int(row[1].strip()))

    matches = 5
    tables = 18

    tournament_data, summary = generate_schedule(participants_all, elos, matches, tables)

    for r in tournament_data:
        print(f"------- Round number {r['round']} -------")
        for m in r["matches"]:
            print(f"Table {m['table']}: {m['p1']} ({m['p1_elo']}) vs {m['p2']} ({m['p2_elo']})")
        if r["sitting_out"]:
            print(f"Sitting out: {', '.join(r['sitting_out'])}")
        print()
    
    print("------- TOURNAMENT SUMMARY -------")
    for s in summary:
        print(f"{s['name']}: Played {s['games']} matches")

if __name__ == "__main__":
    main()