import customtkinter as ctk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Dark luxury theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class GreedyBFSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Greedy Best-First Search")
        self.geometry("1100x700")

        self.graph = {}
        self.heuristics = {}

        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Left Panel (Controls)
        self.left_frame = ctk.CTkFrame(self, corner_radius=15)
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Right Panel (Graph)
        self.right_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#2b2b2b")
        self.right_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Embedded Matplotlib
        self.figure, self.ax = plt.subplots(figsize=(6, 5))
        self.figure.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # ----------------- Controls -----------------
        ctk.CTkLabel(self.left_frame, text="Graph Configuration", font=("Arial", 22, "bold")).pack(pady=15)

        # Load Example Button
        ctk.CTkButton(self.left_frame, text="Load Example Graph", fg_color="#8B8000", hover_color="#B8860B", 
                      font=("Arial", 14, "bold"), corner_radius=8, command=self.load_example).pack(pady=5, padx=20, fill="x")

        # Add Nodes
        self.node_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Node Heuristic (e.g., A 10)", justify="center")
        self.node_entry.pack(pady=(15, 5), padx=20, fill="x", ipady=5)
        ctk.CTkButton(self.left_frame, text="Add Node", corner_radius=8, command=self.add_node).pack(pady=5, padx=20, fill="x")

        # Add Edges
        self.edge_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Node1 Node2 (e.g., A B)", justify="center")
        self.edge_entry.pack(pady=(15, 5), padx=20, fill="x", ipady=5)
        ctk.CTkButton(self.left_frame, text="Add Edge", corner_radius=8, command=self.add_edge).pack(pady=5, padx=20, fill="x")

        # Start and Goal
        self.start_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Start Node", justify="center")
        self.start_entry.pack(pady=(15, 5), padx=20, fill="x", ipady=5)
        self.goal_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Goal Node", justify="center")
        self.goal_entry.pack(pady=5, padx=20, fill="x", ipady=5)

        # Run Algorithm
        ctk.CTkButton(self.left_frame, text="▶ Run Algorithm", fg_color="#1E90FF", hover_color="#0000CD", 
                      font=("Arial", 16, "bold"), corner_radius=10, command=self.run_algorithm).pack(pady=15, padx=20, fill="x", ipady=8)

        # Result Log
        ctk.CTkLabel(self.left_frame, text="Execution Log:", font=("Arial", 16, "bold")).pack(anchor="w", padx=20)
        self.result_text = ctk.CTkTextbox(self.left_frame, height=150, font=("Cascadia Code", 13), 
                                          fg_color="#1a1a1a", text_color="#00FFAA")
        self.result_text.pack(pady=10, padx=20, fill="both", expand=True)

        self.draw_graph()

    def load_example(self):
        self.graph.clear()
        self.heuristics.clear()
        
        nodes = {'S': 10, 'A': 6, 'B': 5, 'C': 2, 'D': 4, 'G': 0}
        self.heuristics = nodes.copy()
        
        edges = [('S', 'A'), ('S', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'D'), ('C', 'G'), ('D', 'G')]
        for u, v in edges:
            if u not in self.graph: self.graph[u] = []
            if v not in self.graph: self.graph[v] = []
            self.graph[u].append(v)
            
        self.start_entry.delete(0, ctk.END)
        self.start_entry.insert(0, 'S')
        
        self.goal_entry.delete(0, ctk.END)
        self.goal_entry.insert(0, 'G')

        self.draw_graph()

    def add_node(self):
        data = self.node_entry.get().split()
        if len(data) == 2:
            node, heuristic = data[0], int(data[1])
            self.heuristics[node] = heuristic
            if node not in self.graph:
                self.graph[node] = []
            self.node_entry.delete(0, ctk.END)
            self.draw_graph()
        else:
            messagebox.showerror("Error", "Invalid format! Use: Node Value (e.g. A 10)")

    def add_edge(self):
        data = self.edge_entry.get().split()
        if len(data) == 2:
            u, v = data[0], data[1]
            if u in self.graph and v in self.graph:
                self.graph[u].append(v)
                self.edge_entry.delete(0, ctk.END)
                self.draw_graph()
            else:
                messagebox.showerror("Error", "Both nodes must be added first!")
        else:
            messagebox.showerror("Error", "Invalid format! Use: Node1 Node2 (e.g. A B)")

    def draw_graph(self, final_path=None):
        self.ax.clear()
        
        if not self.graph:
            self.ax.text(0.5, 0.5, "Add nodes or click 'Load Example'\nto start generating a graph...", 
                         color="white", fontsize=12, ha='center', va='center')
            self.ax.set_axis_off()
            self.canvas.draw()
            return

        G = nx.DiGraph()
        for node in list(self.heuristics.keys()) + list(self.graph.keys()):
             G.add_node(node)

        for node in self.graph:
            for neighbor in self.graph[node]:
                G.add_edge(node, neighbor)
        
        pos = nx.spring_layout(G, seed=42)
        labels = {node: f"{node}\nh={self.heuristics.get(node, '?')}" for node in G.nodes()}

        node_colors = []
        for node in G.nodes():
            if final_path and node in final_path:
                node_colors.append("#00FFAA")
            else:
                node_colors.append("#1f538d")

        edge_colors = []
        for u, v in G.edges():
            if final_path and u in final_path and v in final_path and final_path.index(v) == final_path.index(u) + 1:
                edge_colors.append("#00FFAA")
            else:
                edge_colors.append("#555555")
        
        nx.draw(G, pos, ax=self.ax, with_labels=True, labels=labels, 
                node_size=1600, node_color=node_colors, edge_color=edge_colors, 
                font_size=11, font_weight="bold", font_color="white", arrows=True, width=2)

        self.ax.set_axis_off()
        self.canvas.draw()

    def run_algorithm(self):
        start = self.start_entry.get().strip()
        goal = self.goal_entry.get().strip()

        if not start or not goal:
             messagebox.showerror("Error", "Please specify start and goal nodes!")
             return

        if start not in self.graph or goal not in self.graph and goal not in self.heuristics:
            messagebox.showerror("Error", "Start or Goal node not found in the graph!")
            return

        self.result_text.delete(1.0, ctk.END)
        
        open_list = [start]
        closed_list = []
        path = []

        step = 1
        while open_list:
            open_list.sort(key=lambda x: self.heuristics.get(x, float('inf')))
            
            current_node = open_list.pop(0)
            path.append(current_node)
            closed_list.append(current_node)

            self.result_text.insert(ctk.END, f"--- Step {step} ---\n")
            self.result_text.insert(ctk.END, f"OPEN List: {open_list}\n")
            self.result_text.insert(ctk.END, f"Chosen Node: {current_node} (h={self.heuristics.get(current_node, '?')})\n\n")

            if current_node == goal:
                self.result_text.insert(ctk.END, f"✅ Goal Reached!\n")
                self.result_text.insert(ctk.END, f"Final Path: {' -> '.join(path)}\n")
                self.draw_graph(final_path=path)
                return

            if current_node in self.graph:
                for neighbor in self.graph[current_node]:
                    if neighbor not in closed_list and neighbor not in open_list:
                        open_list.append(neighbor)
            
            step += 1

        self.result_text.insert(ctk.END, "❌ Path to goal not found.\n")
        self.draw_graph()

if __name__ == "__main__":
    app = GreedyBFSApp()
    app.mainloop()