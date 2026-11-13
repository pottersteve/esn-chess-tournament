import csv
import random
import networkx as nx

def generate_schedule(participants, ratings, matches, tables):
    players = []
    for i in range(len(participants)):
        players.append({
            "id": i,
            "name": participants[i],
            "rating": ratings[i],
            "played": set()
        })

    if len(players) % 2 != 0:
        players.append({"id": len(players), "name": "Bye", "rating": 0, "played": set()})

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
                    # Square the rating difference to penalize massive skill gaps
                    rating_score = 10000000 - ((p1["rating"] - p2["rating"]) ** 2)
                    games_played_penalty = (len(p1["played"]) + len(p2["played"])) * 100000000
                    weight = rating_score - games_played_penalty
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
                # Randomly assign pieces for this table
                colors = ["White", "Black"]
                random.shuffle(colors)
                
                round_matches.append({
                    "table": table_count,
                    "p1": p1["name"], "p1_rating": p1["rating"], "p1_color": colors[0],
                    "p2": p2["name"], "p2_rating": p2["rating"], "p2_color": colors[1]
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

    players.sort(key=lambda x: -x['rating'])
    summary = [{"name": p["name"], "games": len(p["played"])} for p in players if p["name"] != "Bye"]

    return tournament_data, summary