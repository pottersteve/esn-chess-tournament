import csv
import networkx as nx

def round_robin_graph(participants, elos, matches, tables):
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

    for round_num in range(1, matches + 1):
        print(f"------- Round number {round_num} -------")
        
        # 1. Initialize an empty Graph for this round
        G = nx.Graph()
        
        # 2. Add all players as nodes
        for p in players:
            G.add_node(p["id"])
            
        # 3. Draw edges (connections) between everyone who HAS NOT played each other yet
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                p1 = players[i]
                p2 = players[j]
                
                # Strict no-rematch rule
                if p2["id"] not in p1["played"]:
                    
                    # Calculate weight (higher weight = better match)
                    # We subtract the Elo difference from 10,000 so smaller differences result in bigger weights.
                    elo_score = 10000 - abs(p1["elo"] - p2["elo"])
                    
                    # To ensure fairness, we heavily prioritize players who have played fewer games
                    games_played_penalty = (len(p1["played"]) + len(p2["played"])) * 100000
                    
                    # Final edge weight
                    weight = elo_score - games_played_penalty
                    
                    G.add_edge(p1["id"], p2["id"], weight=weight)
                    
        # 4. The Algorithm: Find the absolute best combination of pairs for the whole room
        # maxcardinality=True forces it to pair as many people as mathematically possible
        best_pairings_set = nx.max_weight_matching(G, maxcardinality=True)
        
        # 5. Convert the results back into player data and sort them to prioritize people who need games
        player_map = {p["id"]: p for p in players}
        proposed_tables = []
        
        for id1, id2 in best_pairings_set:
            p1 = player_map[id1]
            p2 = player_map[id2]
            combined_games = len(p1["played"]) + len(p2["played"])
            proposed_tables.append((combined_games, p1, p2))
            
        # Sort so pairs with the LEAST amount of games played get tables first
        proposed_tables.sort(key=lambda x: x[0])
        
        # 6. Assign tables
        table_count = 1
        paired_this_round = set()
        
        for combined_games, p1, p2 in proposed_tables:
            if table_count > tables:
                break # We ran out of physical tables
                
            if p1["name"] != "Bye" and p2["name"] != "Bye":
                print(f"Table {table_count}: {p1['name']} ({p1['elo']}) vs {p2['name']} ({p2['elo']})")
                table_count += 1
            
            # Record the history using their unique IDs
            p1["played"].add(p2["id"])
            p2["played"].add(p1["id"])
            
            paired_this_round.add(p1["id"])
            paired_this_round.add(p2["id"])
            
        # Show who is sitting out
        sitting_out = []
        for p in players:
            if p["id"] not in paired_this_round and p["name"] != "Bye":
                sitting_out.append(f"{p['name']} (Games: {len(p['played'])})")
                
        if sitting_out:
            print(f"Sitting out: {', '.join(sitting_out)}")

        print() 

    # --- TOURNAMENT SUMMARY ---
    print("------- TOURNAMENT SUMMARY -------")
    players.sort(key=lambda x: -x['elo']) 
    for p in players:
        if p["name"] != "Bye":
            print(f"{p['name']}: Played {len(p['played'])} matches")


if __name__ == "__main__":
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

    round_robin_graph(participants_all, elos, matches, tables)
    