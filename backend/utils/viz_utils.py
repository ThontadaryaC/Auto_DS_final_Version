import seaborn as sns
import plotly.graph_objects as go
import plotly.io as pio

def get_seaborn_colors(palette_name="rocket", n_colors=10):
    """Returns a list of HEX colors from a Seaborn palette."""
    palette = sns.color_palette(palette_name, n_colors)
    return palette.as_hex()

# Standard "Premium" Layout for AutoDS
PREMIUM_LAYOUT = {
    "template": "plotly_white",
    "font": {"family": "Inter, sans-serif", "size": 12, "color": "#2c3e50"},
    "title": {"font": {"size": 20, "color": "#1a1a1a"}, "x": 0.5, "xanchor": "center"},
    "margin": {"l": 50, "r": 50, "t": 80, "b": 50},
    "hovermode": "closest",
    "plot_bgcolor": "rgba(240, 242, 246, 0.5)",
    "paper_bgcolor": "white",
    "xaxis": {
        "gridcolor": "#e2e8f0",
        "linecolor": "#cbd5e0",
        "zerolinecolor": "#cbd5e0",
    },
    "yaxis": {
        "gridcolor": "#e2e8f0",
        "linecolor": "#cbd5e0",
        "zerolinecolor": "#cbd5e0",
    }
}

def apply_premium_style(fig):
    """Applies the premium styling to a Plotly figure."""
    fig.update_layout(**PREMIUM_LAYOUT)
    return fig
