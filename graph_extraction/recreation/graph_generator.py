#!/usr/bin/env python3
"""
Graph Generator using Matplotlib
Recreates graphs for exam questions based on descriptions
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json


class GraphGenerator:
    """Generate graphs for exam questions using matplotlib"""
    
    def __init__(self, style: str = 'seaborn-v0_8'):
        """
        Initialize graph generator.
        
        Args:
            style: Matplotlib style to use
        """
        plt.style.use(style)
        self.default_figsize = (8, 6)
    
    def create_supply_demand_graph(
        self,
        supply_data: Optional[Tuple[List[float], List[float]]] = None,
        demand_data: Optional[Tuple[List[float], List[float]]] = None,
        equilibrium: Optional[Tuple[float, float]] = None,
        x_label: str = "Quantity",
        y_label: str = "Price",
        title: Optional[str] = None,
        show_areas: Optional[List[Dict]] = None,
        output_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create a supply and demand graph.
        
        Args:
            supply_data: (x_values, y_values) for supply curve
            demand_data: (x_values, y_values) for demand curve
            equilibrium: (quantity, price) equilibrium point
            x_label: X-axis label
            y_label: Y-axis label
            title: Graph title
            show_areas: List of areas to highlight (consumer surplus, etc.)
            output_path: Path to save figure
            
        Returns:
            matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=self.default_figsize)
        
        # Default supply curve (upward sloping)
        if supply_data is None:
            q_supply = np.linspace(0, 100, 100)
            p_supply = 10 + 0.5 * q_supply  # P = 10 + 0.5Q
        else:
            q_supply, p_supply = supply_data
        
        # Default demand curve (downward sloping)
        if demand_data is None:
            q_demand = np.linspace(0, 100, 100)
            p_demand = 100 - 0.5 * q_demand  # P = 100 - 0.5Q
        else:
            q_demand, p_demand = demand_data
        
        # Plot curves
        ax.plot(q_supply, p_supply, 'b-', linewidth=2, label='Supply')
        ax.plot(q_demand, p_demand, 'r-', linewidth=2, label='Demand')
        
        # Find equilibrium if not provided
        if equilibrium is None:
            # Find intersection
            for i, q in enumerate(q_supply):
                if q in q_demand:
                    idx = np.where(q_demand == q)[0]
                    if len(idx) > 0:
                        p_eq = p_supply[i]
                        equilibrium = (q, p_eq)
                        break
            
            if equilibrium is None:
                # Approximate intersection
                equilibrium = (50, 35)  # Default
        
        q_eq, p_eq = equilibrium
        
        # Mark equilibrium
        ax.plot(q_eq, p_eq, 'ko', markersize=8, label='Equilibrium')
        ax.axhline(y=p_eq, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=q_eq, color='gray', linestyle='--', alpha=0.5)
        
        # Highlight areas if specified
        if show_areas:
            for area in show_areas:
                area_type = area.get('type', 'consumer_surplus')
                if area_type == 'consumer_surplus':
                    # Consumer surplus triangle
                    q_max = max(q_demand)
                    p_max = max(p_demand)
                    triangle = patches.Polygon(
                        [(0, p_max), (0, p_eq), (q_eq, p_eq)],
                        closed=True,
                        facecolor='green',
                        alpha=0.3,
                        label='Consumer Surplus'
                    )
                    ax.add_patch(triangle)
                elif area_type == 'producer_surplus':
                    # Producer surplus triangle
                    p_min = min(p_supply)
                    triangle = patches.Polygon(
                        [(0, p_min), (0, p_eq), (q_eq, p_eq)],
                        closed=True,
                        facecolor='blue',
                        alpha=0.3,
                        label='Producer Surplus'
                    )
                    ax.add_patch(triangle)
        
        # Labels and formatting
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, max(max(q_supply), max(q_demand)) * 1.1)
        ax.set_ylim(0, max(max(p_supply), max(p_demand)) * 1.1)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✅ Graph saved to: {output_path}")
        
        return fig
    
    def create_production_possibilities_graph(
        self,
        points: Optional[List[Tuple[float, float]]] = None,
        x_label: str = "Good X",
        y_label: str = "Good Y",
        title: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> plt.Figure:
        """Create a production possibilities boundary graph"""
        fig, ax = plt.subplots(figsize=self.default_figsize)
        
        if points is None:
            # Default PPF curve (concave)
            x_vals = np.array([0, 2, 4, 6, 8, 10])
            y_vals = np.array([10, 9, 7, 4, 2, 0])
        else:
            x_vals, y_vals = zip(*points)
        
        # Plot PPF
        ax.plot(x_vals, y_vals, 'b-', linewidth=2, marker='o', label='PPF')
        
        # Fill area under curve (feasible region)
        ax.fill_between(x_vals, 0, y_vals, alpha=0.2, color='green', label='Feasible Region')
        
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✅ Graph saved to: {output_path}")
        
        return fig
    
    def create_cost_curves_graph(
        self,
        quantity: Optional[np.ndarray] = None,
        mc_data: Optional[np.ndarray] = None,
        atc_data: Optional[np.ndarray] = None,
        avc_data: Optional[np.ndarray] = None,
        x_label: str = "Quantity",
        y_label: str = "Cost",
        title: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> plt.Figure:
        """Create cost curves graph (MC, ATC, AVC)"""
        fig, ax = plt.subplots(figsize=self.default_figsize)
        
        if quantity is None:
            quantity = np.linspace(1, 100, 100)
        
        if mc_data is None:
            mc_data = 10 + 0.1 * quantity  # MC = 10 + 0.1Q
        
        if atc_data is None:
            atc_data = 100 / quantity + 5 + 0.05 * quantity  # ATC
        
        if avc_data is None:
            avc_data = 5 + 0.05 * quantity  # AVC
        
        ax.plot(quantity, mc_data, 'r-', linewidth=2, label='MC')
        ax.plot(quantity, atc_data, 'b-', linewidth=2, label='ATC')
        ax.plot(quantity, avc_data, 'g-', linewidth=2, label='AVC')
        
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✅ Graph saved to: {output_path}")
        
        return fig
    
    def create_graph_from_description(
        self,
        description: Dict,
        output_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create a graph based on OpenAI's description.
        
        Args:
            description: Dict from GraphAnalyzer with graph description
            output_path: Path to save figure
        """
        graph_type = description.get('graph_type', 'supply_demand')
        
        if graph_type == 'supply_demand':
            return self.create_supply_demand_graph(
                x_label=description.get('x_axis', {}).get('label', 'Quantity'),
                y_label=description.get('y_axis', {}).get('label', 'Price'),
                output_path=output_path
            )
        elif graph_type == 'production_possibilities':
            return self.create_production_possibilities_graph(
                x_label=description.get('x_axis', {}).get('label', 'Good X'),
                y_label=description.get('y_axis', {}).get('label', 'Good Y'),
                output_path=output_path
            )
        elif graph_type == 'cost_curves':
            return self.create_cost_curves_graph(
                x_label=description.get('x_axis', {}).get('label', 'Quantity'),
                y_label=description.get('y_axis', {}).get('label', 'Cost'),
                output_path=output_path
            )
        else:
            # Default to supply/demand
            return self.create_supply_demand_graph(output_path=output_path)


def generate_graph_for_question(
    question: Dict,
    output_dir: str = "generated_graphs"
) -> Optional[str]:
    """
    Generate a graph for a question that references figures.
    
    Args:
        question: Question dict with figure analysis
        output_dir: Directory to save graphs
        
    Returns:
        Path to saved graph file, or None
    """
    if not question.get('has_figures'):
        return None
    
    generator = GraphGenerator()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    question_num = question.get('question_number', 'unknown')
    
    # Get figure analysis
    figure_analyses = question.get('figure_analyses', [])
    if not figure_analyses:
        return None
    
    # Use first analysis
    analysis = figure_analyses[0].get('analysis', {})
    
    if 'error' in analysis:
        return None
    
    # Generate graph
    graph_data = {
        'graph_type': analysis.get('graph_type'),
        'x_axis': analysis.get('x_axis', {}),
        'y_axis': analysis.get('y_axis', {})
    }
    
    output_file = output_path / f"question_{question_num}_graph.png"
    
    try:
        generator.create_graph_from_description(graph_data, str(output_file))
        return str(output_file)
    except Exception as e:
        print(f"⚠️  Error generating graph: {e}")
        return None


if __name__ == "__main__":
    # Test graph generation
    print("Testing Graph Generator...")
    
    generator = GraphGenerator()
    
    # Test supply/demand
    fig1 = generator.create_supply_demand_graph(
        title="Supply and Demand Example",
        show_areas=[{'type': 'consumer_surplus'}, {'type': 'producer_surplus'}]
    )
    plt.savefig("test_supply_demand.png")
    print("✅ Created test_supply_demand.png")
    
    # Test PPF
    fig2 = generator.create_production_possibilities_graph(
        title="Production Possibilities Boundary"
    )
    plt.savefig("test_ppf.png")
    print("✅ Created test_ppf.png")
    
    plt.close('all')

