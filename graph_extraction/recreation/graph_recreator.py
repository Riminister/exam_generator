#!/usr/bin/env python3
"""
Graph Recreator - Recreate graphs from descriptions using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple, List


class GraphRecreator:
    """Recreate graphs from descriptions using matplotlib"""
    
    def __init__(self):
        """Initialize graph recreator"""
        plt.style.use('seaborn-v0_8-darkgrid')
        self.figsize = (8, 6)
    
    def create_supply_demand_graph(
        self,
        x_label: str = "Quantity",
        y_label: str = "Price",
        x_range: Tuple[float, float] = (0, 100),
        y_range: Tuple[float, float] = (0, 50),
        equilibrium: Optional[Tuple[float, float]] = None,
        output_path: Optional[str] = None
    ) -> plt.Figure:
        """Create a supply and demand graph"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Generate quantity range
        q = np.linspace(x_range[0], x_range[1], 100)
        
        # Default equilibrium if not provided
        if equilibrium is None:
            eq_q, eq_p = 50, 25
        else:
            eq_q, eq_p = equilibrium
        
        # Demand curve: P = a - b*Q (downward sloping)
        # Through equilibrium point
        b = eq_p / eq_q if eq_q > 0 else 0.5
        a = eq_p + b * eq_q
        demand = a - b * q
        demand = np.clip(demand, y_range[0], y_range[1])
        
        # Supply curve: P = c + d*Q (upward sloping)
        # Through equilibrium point
        d = eq_p / eq_q if eq_q > 0 else 0.5
        c = eq_p - d * eq_q
        supply = c + d * q
        supply = np.clip(supply, y_range[0], y_range[1])
        
        # Plot curves
        ax.plot(q, demand, 'b-', linewidth=2, label='Demand')
        ax.plot(q, supply, 'r-', linewidth=2, label='Supply')
        
        # Mark equilibrium
        ax.plot(eq_q, eq_p, 'ko', markersize=8, label='Equilibrium')
        ax.axvline(eq_q, color='gray', linestyle='--', alpha=0.5)
        ax.axhline(eq_p, color='gray', linestyle='--', alpha=0.5)
        
        # Labels
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.set_xlim(x_range)
        ax.set_ylim(y_range)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_title('Supply and Demand', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✅ Graph saved to: {output_path}")
        
        return fig
    
    def create_production_possibilities_graph(
        self,
        x_label: str = "Good X",
        y_label: str = "Good Y",
        points: Optional[List[Tuple[float, float]]] = None,
        output_path: Optional[str] = None
    ) -> plt.Figure:
        """Create a production possibilities boundary graph"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if points is None:
            # Default PPF curve (concave)
            x_vals = np.array([0, 20, 40, 60, 80, 100])
            y_vals = np.array([100, 90, 70, 45, 20, 0])
        else:
            x_vals = np.array([p[0] for p in points])
            y_vals = np.array([p[1] for p in points])
        
        # Plot PPF
        ax.plot(x_vals, y_vals, 'b-', linewidth=2, label='Production Possibilities Boundary')
        ax.fill_between(x_vals, 0, y_vals, alpha=0.2, color='green', label='Attainable')
        
        # Mark points
        ax.plot(x_vals, y_vals, 'bo', markersize=6)
        
        # Labels
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_title('Production Possibilities Boundary', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✅ Graph saved to: {output_path}")
        
        return fig
    
    def create_cost_curves_graph(
        self,
        x_label: str = "Quantity",
        y_label: str = "Cost",
        output_path: Optional[str] = None
    ) -> plt.Figure:
        """Create cost curves graph (ATC, AVC, MC)"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        q = np.linspace(1, 100, 100)
        
        # Typical cost curves
        # ATC (U-shaped)
        atc = 1000/q + 0.1*q + 5
        # AVC (U-shaped, lower than ATC)
        avc = 500/q + 0.08*q + 3
        # MC (U-shaped, intersects at minimum of ATC and AVC)
        mc = 0.15*q + 2
        
        ax.plot(q, atc, 'b-', linewidth=2, label='ATC')
        ax.plot(q, avc, 'g-', linewidth=2, label='AVC')
        ax.plot(q, mc, 'r-', linewidth=2, label='MC')
        
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_title('Cost Curves', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✅ Graph saved to: {output_path}")
        
        return fig
    
    def create_from_description(
        self,
        description: Dict,
        output_path: Optional[str] = None
    ) -> Optional[plt.Figure]:
        """
        Create graph from OpenAI description.
        
        Args:
            description: Dict with graph_type, axes, curves, etc.
            output_path: Where to save the graph
            
        Returns:
            matplotlib Figure object
        """
        graph_type = description.get('graph_type', '').lower()
        
        if 'supply' in graph_type or 'demand' in graph_type:
            x_axis = description.get('x_axis', {})
            y_axis = description.get('y_axis', {})
            return self.create_supply_demand_graph(
                x_label=x_axis.get('label', 'Quantity'),
                y_label=y_axis.get('label', 'Price'),
                x_range=tuple(x_axis.get('range', [0, 100])),
                y_range=tuple(y_axis.get('range', [0, 50])),
                output_path=output_path
            )
        
        elif 'production' in graph_type or 'possibilities' in graph_type:
            return self.create_production_possibilities_graph(
                x_label=description.get('x_axis', {}).get('label', 'Good X'),
                y_label=description.get('y_axis', {}).get('label', 'Good Y'),
                output_path=output_path
            )
        
        elif 'cost' in graph_type:
            return self.create_cost_curves_graph(
                x_label=description.get('x_axis', {}).get('label', 'Quantity'),
                y_label=description.get('y_axis', {}).get('label', 'Cost'),
                output_path=output_path
            )
        
        else:
            # Default to supply/demand
            print(f"⚠️  Unknown graph type: {graph_type}, using default supply/demand")
            return self.create_supply_demand_graph(output_path=output_path)


def recreate_graph_for_question(
    question: Dict,
    output_dir: str = "generated_graphs"
) -> Optional[str]:
    """
    Recreate graph for a question that has a graph description.
    
    Args:
        question: Question dict with graph_description
        output_dir: Directory to save graphs
        
    Returns:
        Path to saved graph, or None
    """
    if not question.get('graph_description'):
        return None
    
    graph_desc = question['graph_description']
    
    if 'error' in graph_desc:
        return None
    
    recreator = GraphRecreator()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    question_num = question.get('question_number', 'unknown')
    figure_num = question.get('figure_references', [{}])[0].get('figure_number', '1') if question.get('figure_references') else '1'
    
    output_file = output_path / f"question_{question_num}_figure_{figure_num}.png"
    
    try:
        recreator.create_from_description(graph_desc, str(output_file))
        return str(output_file)
    except Exception as e:
        print(f"⚠️  Error recreating graph: {e}")
        return None


if __name__ == "__main__":
    # Test graph recreation
    print("Testing Graph Recreator...")
    
    test_desc = {
        "graph_type": "supply_demand",
        "x_axis": {"label": "Quantity", "range": [0, 100]},
        "y_axis": {"label": "Price", "range": [0, 50]},
        "curves": [
            {"name": "Demand", "type": "line", "slope": "negative"},
            {"name": "Supply", "type": "line", "slope": "positive"}
        ]
    }
    
    recreator = GraphRecreator()
    fig = recreator.create_from_description(test_desc, "test_graph.png")
    print("✅ Test graph created: test_graph.png")
    plt.show()

