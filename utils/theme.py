import streamlit as st


THEMES = {
    "Clinical Blue": {
        "app_bg": "#f0f4f8",
        "surface": "#ffffff",
        "primary": "#1a237e",
        "primary_light": "#3949ab",
        "text": "#1f2937",
        "muted": "#667085",
        "accent": "#1565c0",
    },
    "Calm Green": {
        "app_bg": "#eef7f1",
        "surface": "#ffffff",
        "primary": "#14532d",
        "primary_light": "#2e7d32",
        "text": "#183028",
        "muted": "#5c7166",
        "accent": "#16803c",
    },
    "Warm Care": {
        "app_bg": "#fff7ed",
        "surface": "#ffffff",
        "primary": "#7c2d12",
        "primary_light": "#c2410c",
        "text": "#3f2418",
        "muted": "#806b60",
        "accent": "#ea580c",
    },
    "High Contrast": {
        "app_bg": "#f8fafc",
        "surface": "#ffffff",
        "primary": "#111827",
        "primary_light": "#374151",
        "text": "#111827",
        "muted": "#374151",
        "accent": "#005fcc",
    },
    "Dark Night": {
        "app_bg": "#0f172a",
        "surface": "#172033",
        "primary": "#0b1f3a",
        "primary_light": "#164e87",
        "text": "#e5edf8",
        "muted": "#a9b8cc",
        "accent": "#4da3ff",
        "line": "#2b3a52",
        "input": "#111a2b",
    },
}


def render_theme_picker():
    if st.session_state.get("_theme_picker_rendered", False):
        return
    st.session_state._theme_picker_rendered = True
    if "theme_name" not in st.session_state:
        st.session_state.theme_name = "Clinical Blue"
    st.selectbox(
        "🎨 Theme",
        list(THEMES),
        key="global_theme_selector",
        help="Choose the visual theme for the application.",
    )


def theme_css():
    theme = THEMES.get(
        st.session_state.get("global_theme_selector", "Clinical Blue"),
        THEMES["Clinical Blue"],
    )
    return f"""
    <style>
      :root {{
        --app-bg: {theme['app_bg']};
        --surface: {theme['surface']};
        --theme-primary: {theme['primary']};
        --theme-primary-light: {theme['primary_light']};
        --theme-text: {theme['text']};
        --theme-muted: {theme['muted']};
        --theme-accent: {theme['accent']};
        --theme-line: {theme.get('line', '#e2e8f0')};
        --theme-input: {theme.get('input', '#ffffff')};
      }}
      [data-testid="stAppViewContainer"] {{ background: var(--app-bg) !important; }}
      [data-testid="stSidebar"] {{ background: linear-gradient(180deg, var(--theme-primary), var(--theme-primary-light)) !important; }}
      .app-header {{ background: linear-gradient(135deg, var(--theme-primary), var(--theme-primary-light)) !important; }}
      .h-card, .welcome-card, .nav-card, .stat-box, .emer-num-card,
      .first-aid-card, .blood-card, .admin-metric {{ background: var(--surface) !important; }}
      .h-name, .welcome-card h4, .stat-box .val {{ color: var(--theme-primary) !important; }}
      .h-detail, .welcome-card p, .stat-box .lbl, .admin-metric .lbl {{ color: var(--theme-muted) !important; }}
      .btn-dir, .action-btn.btn-dir {{ background: var(--theme-accent) !important; }}
      .stButton > button[kind="primary"], .stDownloadButton > button {{ border-color: var(--theme-accent) !important; }}
      [data-testid="stMetricValue"] {{ color: var(--theme-primary) !important; }}
            [data-testid="stAppViewContainer"] .stMarkdown, [data-testid="stAppViewContainer"] label,
            [data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] {{ color: var(--theme-text); }}
            [data-testid="stAppViewContainer"] input, [data-testid="stAppViewContainer"] textarea,
            [data-testid="stAppViewContainer"] [data-baseweb="select"] > div {{
                background: var(--theme-input) !important; color: var(--theme-text) !important;
                border-color: var(--theme-line) !important;
            }}
            [data-testid="stAppViewContainer"] [data-testid="stMetric"],
            [data-testid="stAppViewContainer"] [data-testid="stExpander"],
            [data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] {{
                background: var(--surface) !important; border-color: var(--theme-line) !important;
            }}
            [data-testid="stAppViewContainer"] [data-testid="stMetricLabel"],
            [data-testid="stAppViewContainer"] [data-testid="stMetricValue"] {{ color: var(--theme-text) !important; }}
            [data-testid="stAppViewContainer"] [data-testid="stTabs"] button {{ color: var(--theme-muted) !important; }}
            [data-testid="stAppViewContainer"] .h-name, [data-testid="stAppViewContainer"] h1,
            [data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3,
            [data-testid="stAppViewContainer"] h4 {{ color: var(--theme-text); }}
            [data-testid="stAppViewContainer"] .h-detail, [data-testid="stAppViewContainer"] p,
            [data-testid="stAppViewContainer"] .results-summary {{ color: var(--theme-muted); }}
            [data-testid="stAppViewContainer"] [data-baseweb="popover"] {{ background: var(--surface); }}
      @media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ animation-duration: 0.01ms !important; }} }}
    </style>
    """
