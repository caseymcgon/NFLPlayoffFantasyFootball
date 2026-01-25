## This file should start the playoffs blank. It should only be updated if/when a player has a season-ending injury and is replaced on a roster.


player_swaps_dict = {
    # Structure: {GM: {'orginal_player': 'new_player'}}
    "Kelly McGon": {"George Kittle": "Jauan Jennings"},
    "Caleb Hedin": {"George Kittle": "Christian McCaffrey"},
    "Rick": {"George Kittle": "Christian McCaffrey"},
    "Ben Wemer": {"Zach Charbonnet": "Kenneth Walker III", 
                  "Bo Nix": "Jarrett Stidham"},
    "Michael Walker": {"Zach Charbonnet": "Kenneth Walker III"},
    "Mike Caballero": {"Bo Nix": "Jarrett Stidham"},
    "Maggie Petersen": {"Bo Nix": "Jarrett Stidham"},
    "Anna Petersen": {"Bo Nix": "Jarrett Stidham"},
    "Caleb Hedin": {"Bo Nix": "Jarrett Stidham"}
}

player_healthy_rounds_dict = {
    # Structure: {player_name: ['rounds_list']}
    "George Kittle": ['Wild Card'],
    "Bo Nix": ['Wild Card', 'Divisional'],
    "Zach Charbonnet": ['Wild Card', 'Divisional']
}