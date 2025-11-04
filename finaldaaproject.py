import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import heapq


# EV City Map and Graph Setup

G = nx.Graph()

edges = [
    ("Mumbai", "Nashik", 180),
    ("Mumbai", "Goa", 580),
    ("Nashik", "Pune", 300),
    ("Pune", "Satara", 120),
    ("Satara", "Kolhapur", 180),
    ("Kolhapur", "Goa", 200),
    ("Goa", "Hyderabad", 610),
    ("Hyderabad", "Kolhapur", 300),
]

for u, v, dist in edges:
    G.add_edge(u, v, distance=dist)

# Charging prices per unit (₹)
charging_prices = {
    "Mumbai": 1.8,
    "Nashik": 1.5,
    "Pune": 1.2,
    "Satara": 1.5,
    "Kolhapur": 1.8,
    "Goa": 2.0,
    "Hyderabad": 2.2,
}


# Dijkstra’s Algorithm

def dijkstra(graph, start, end):
    pq = [(0, start, [])]
    visited = set()
    while pq:
        (cost, node, path) = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]
        if node == end:
            return cost, path
        for neighbor, data in graph[node].items():
            if neighbor not in visited:
                heapq.heappush(pq, (cost + data["distance"], neighbor, path))
    return float("inf"), []


# Path and Charging Logic

def calculate_path(start, end, battery_capacity):
    total_distance, path = dijkstra(G, start, end)
    if not path:
        messagebox.showerror("Error", "No path found between selected cities!")
        return None, None, None, None

    remaining_battery = battery_capacity
    total_cost = 0
    charging_plan = []

    for i in range(len(path) - 1):
        dist = G[path[i]][path[i + 1]]["distance"]
        if dist > remaining_battery:
            # Not enough battery to reach next city -> charge fully here
            cost = (battery_capacity - remaining_battery) * charging_prices[path[i]]
            total_cost += cost
            charging_plan.append(f"{path[i]}: {battery_capacity - remaining_battery:.1f} units @ ₹{charging_prices[path[i]]}/unit")
            remaining_battery = battery_capacity

        remaining_battery -= dist

    # Check at destination if charging is needed
    if remaining_battery < 0:
        total_cost += abs(remaining_battery) * charging_prices[end]
        charging_plan.append(f"{end}: {abs(remaining_battery):.1f} units @ ₹{charging_prices[end]}/unit")

    return path, total_distance, total_cost, charging_plan


# Visualization Function

def draw_graph(path=None):
    plt.clf()
    pos = nx.circular_layout(G)
    plt.figure("EV Route Map & Charging Costs", figsize=(6, 6))
    plt.title("EV Route Map & Charging Costs", fontsize=14, fontweight="bold")

    # Draw base graph
    nx.draw(
        G, pos, with_labels=True, node_color="#5bc0de",
        node_size=2200, font_size=11, font_weight="bold", font_color="white"
    )

    # Draw edges and labels
    nx.draw_networkx_edge_labels(G, pos,
        edge_labels={(u, v): f"{d['distance']}" for u, v, d in G.edges(data=True)},
        font_color="black", font_size=9, label_pos=0.5
    )

    # Highlight the selected route in green
    if path:
        route_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=route_edges, width=3, edge_color="green")

    # Show charging prices on nodes
    for city, (x, y) in pos.items():
        plt.text(x, y - 0.08, f"₹{charging_prices[city]}/unit", fontsize=9, color="black", ha="center")

    plt.tight_layout()
    plt.show(block=False)


# Main GUI Window

def find_route():
    start = start_var.get()
    end = end_var.get()
    try:
        battery_capacity = float(battery_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid battery capacity (number).")
        return

    if start == end:
        messagebox.showerror("Invalid Input", "Start and destination cities cannot be the same.")
        return

    path, total_distance, total_cost, charging_plan = calculate_path(start, end, battery_capacity)
    if not path:
        return

    draw_graph(path)

    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f" Optimal Route: {' ➜ '.join(path)}\n")
    result_text.insert(tk.END, f" Total Distance: {total_distance} km\n")
    result_text.insert(tk.END, f" Total Charging Cost: ₹{total_cost:.2f}\n\n")

    if charging_plan:
        result_text.insert(tk.END, " Charging Plan:\n")
        for charge in charging_plan:
            result_text.insert(tk.END, f" • {charge}\n")
    else:
        result_text.insert(tk.END, "Battery capacity sufficient — no charging needed!\n")

# GUI setup
root = tk.Tk()
root.title("EV Route Optimization System")
root.configure(bg="#e6f2ff")

frame = tk.Frame(root, bg="#e6f2ff")
frame.pack(padx=20, pady=20)

tk.Label(frame, text="Start City:", bg="#e6f2ff", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="e")
tk.Label(frame, text="Destination City:", bg="#e6f2ff", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="e")
tk.Label(frame, text="Battery Capacity (units):", bg="#e6f2ff", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky="e")

start_var = tk.StringVar()
end_var = tk.StringVar()
city_list = list(G.nodes)

ttk.Combobox(frame, textvariable=start_var, values=city_list, width=15, state="readonly").grid(row=0, column=1, padx=10, pady=5)
ttk.Combobox(frame, textvariable=end_var, values=city_list, width=15, state="readonly").grid(row=1, column=1, padx=10, pady=5)
battery_entry = tk.Entry(frame, width=18)
battery_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Button(frame, text="Find Optimal Route", bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
          relief="raised", command=find_route).grid(row=3, column=0, columnspan=2, pady=10)

result_text = tk.Text(frame, width=60, height=12, bg="#d9eaff", fg="black", font=("Courier New", 10))
result_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
