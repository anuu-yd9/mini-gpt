"""Mini-GPT: a small language model written from scratch (Streamlit dashboard)."""
import html
import json
import math
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Mini-GPT", page_icon="🍂", layout="wide")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))   # so `from model import ...` works anywhere
GITHUB = "https://github.com/anuu-yd9/mini-gpt"

# Autumn palette
INK, MUTED = "#3a2417", "#7a6350"
ORANGE, RUST, MUSTARD, OLIVE, WINE = "#c8561f", "#9c3d1b", "#d9962b", "#7b8a3c", "#7a2e3a"
GRID = "#eddcc3"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,600&family=DM+Sans:wght@400;500;600;700&display=swap');
:root{--ease:cubic-bezier(.22,1,.36,1);--bg:#fbf4e9;--card:rgba(255,250,242,.86);--solid:#fffaf2;--line:#ecd9bd;--line2:#dcc3a0;
--ink:#3a2417;--muted:#7a6350;--soft:#a48b73;--orange:#c8561f;--rust:#9c3d1b;--mustard:#d9962b;--olive:#7b8a3c;--wine:#7a2e3a;--cream:#f3e6d2;
--serif:'Fraunces','Playfair Display',Georgia,'Times New Roman',serif;--sans:'DM Sans','Segoe UI',system-ui,sans-serif}
html,body,.stApp{font-family:var(--sans);color:var(--ink)}
.stApp{background:radial-gradient(900px 520px at 88% -8%,rgba(217,150,43,.24),transparent 62%),
radial-gradient(800px 520px at -5% 6%,rgba(200,86,31,.13),transparent 62%),
radial-gradient(700px 500px at 50% 112%,rgba(122,46,58,.08),transparent 60%),var(--bg)}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{visibility:hidden;height:0}
.block-container{max-width:1120px;padding-top:1.2rem;padding-bottom:3.5rem;position:relative;z-index:1}
h1,h2,h3,p,li,label{letter-spacing:-.005em}
a{color:var(--rust);text-decoration:none;border-bottom:1px solid rgba(156,61,27,.3)} a:hover{color:var(--orange)}

@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes grow{to{width:var(--w)}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes fall{0%{transform:translate3d(0,-6vh,0) rotate(0deg);opacity:0}8%{opacity:.55}50%{transform:translate3d(70px,52vh,0) rotate(210deg)}
92%{opacity:.4}100%{transform:translate3d(-40px,108vh,0) rotate(420deg);opacity:0}}
@keyframes qfade{0%{opacity:0;transform:translateY(10px)}4%,22%{opacity:1;transform:none}27%,100%{opacity:0}}
.fade{opacity:0;animation:up .8s var(--ease) forwards;animation-delay:calc(var(--i,0)*80ms)}

/* falling leaves */
.leaf{position:fixed;top:-40px;left:var(--x);width:var(--s);height:var(--s);background:var(--c);border-radius:0 88% 0 88%;opacity:0;
animation:fall var(--t) linear infinite;animation-delay:var(--d);pointer-events:none;z-index:0}
.leaf::after{content:"";position:absolute;left:12%;top:49%;width:76%;height:1px;background:rgba(255,248,235,.45);transform:rotate(-45deg);transform-origin:center}

/* tabs as pills */
.stTabs [role="tablist"]{gap:.4rem;border-bottom:0;position:sticky;top:0;z-index:50;background:rgba(251,244,233,.88);
backdrop-filter:blur(12px);padding:.45rem 0 .6rem;margin-bottom:.8rem}
.stTabs [role="tab"]{height:40px;padding:0 22px !important;font-weight:600;font-size:.92rem;color:var(--muted);border-radius:999px !important;background:transparent;
border:1px solid transparent;transition:all .3s var(--ease)}
.stTabs [role="tab"]:hover{color:var(--rust);background:rgba(200,86,31,.07)}
.stTabs [aria-selected="true"]{color:#fff8ee !important;background:linear-gradient(100deg,var(--orange),#d9772b) !important;box-shadow:0 8px 22px rgba(200,86,31,.28)}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"],.react-aria-SelectionIndicator{display:none !important}
.stTabs [role="tablist"]>div[aria-hidden="true"],.stTabs [role="tablist"]>div:not([role="tab"]){display:none}

/* brand */
.brand{display:flex;justify-content:space-between;align-items:center;padding:.3rem 0 .6rem}
.logo{font-family:var(--serif);font-size:1.4rem;font-weight:700;display:flex;align-items:center;gap:.65rem;color:var(--ink)}
.logo i{width:26px;height:26px;border-radius:0 88% 0 88%;background:linear-gradient(135deg,var(--mustard),var(--orange) 60%,var(--rust));display:inline-block;transform:rotate(-8deg);box-shadow:0 6px 16px rgba(200,86,31,.3)}
.brand-r{display:flex;gap:.7rem;align-items:center;font-size:.82rem;color:var(--muted)}
.tagpill{display:inline-flex;gap:.5rem;align-items:center;padding:.38rem .9rem;border:1px solid var(--line);border-radius:999px;background:var(--card)}
.tagpill b{width:8px;height:8px;border-radius:50%;background:var(--olive)}
.ghlink{padding:.38rem .95rem;border:1px solid var(--line2);border-radius:999px;color:var(--rust);transition:all .3s var(--ease)}
.ghlink:hover{background:var(--rust);color:#fff8ee;border-color:var(--rust)}

/* hero */
.hero{display:grid;grid-template-columns:1.12fr 1fr;gap:2.6rem;align-items:center;padding:1.8rem 0 1.2rem}
.eyebrow{font-size:.74rem;font-weight:700;letter-spacing:.2em;color:var(--orange);margin-bottom:1rem;text-transform:uppercase}
.hero h1{font-family:var(--serif);font-size:clamp(2.3rem,4.4vw,3.7rem);font-weight:600;line-height:1.04;letter-spacing:-.025em;margin:0;padding:0;color:var(--ink)}
.hero h1 em{font-style:italic;color:var(--orange);font-weight:600}
.lead{color:var(--muted);font-size:1.08rem;line-height:1.7;margin:1.2rem 0 1.3rem;max-width:34rem}
.chips{display:flex;flex-wrap:wrap;gap:.5rem}
.chips span{font-size:.8rem;font-weight:500;color:var(--rust);padding:.36rem .85rem;border:1px solid var(--line2);border-radius:999px;background:rgba(255,250,242,.7);transition:all .3s var(--ease)}
.chips span:hover{background:var(--cream);transform:translateY(-2px)}

/* pull-quote */
.paper{position:relative;background:linear-gradient(160deg,#fff9ee,#f6e7cd);border:1px solid var(--line2);border-radius:22px;padding:2rem 2rem 1.6rem;
box-shadow:0 30px 60px rgba(156,61,27,.12),0 2px 0 #fff inset;transform:rotate(1.2deg);transition:transform .5s var(--ease)}
.paper:hover{transform:rotate(0deg) translateY(-4px)}
.paper::before{content:"“";position:absolute;top:-.2rem;left:1.1rem;font-family:var(--serif);font-size:7rem;line-height:1;color:var(--mustard);opacity:.55}
.quotes{position:relative;min-height:170px;margin-top:1.8rem}
.q{position:absolute;inset:0;opacity:0;animation:qfade 24s infinite;animation-delay:calc(var(--k)*6s)}
.q p{font-family:var(--serif);font-style:italic;font-size:1.55rem;line-height:1.4;color:var(--ink);margin:0}
.q small{display:block;margin-top:.9rem;color:var(--soft);font-size:.8rem;letter-spacing:.04em}
.paper .by{display:flex;justify-content:space-between;align-items:center;border-top:1px dashed var(--line2);padding-top:.8rem;margin-top:.8rem;font-size:.78rem;color:var(--muted)}
.paper .by b{color:var(--rust);white-space:nowrap;margin-left:1rem}

/* cards */
.row3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:.4rem 0 1.1rem}
.row2{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:.6rem 0}
.row4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:.8rem 0}
.card{position:relative;background:var(--card);backdrop-filter:blur(6px);border:1px solid var(--line);border-radius:20px;padding:1.3rem 1.45rem;
transition:transform .4s var(--ease),box-shadow .4s var(--ease),border-color .4s var(--ease)}
.card:hover{transform:translateY(-4px);border-color:var(--line2);box-shadow:0 20px 44px rgba(156,61,27,.10)}
.card.tint{background:linear-gradient(160deg,rgba(255,244,222,.95),rgba(248,228,196,.8))}
.num{font-family:var(--serif);font-size:2.5rem;font-weight:600;letter-spacing:-.02em;line-height:1.05;color:var(--rust)}
.lab{color:var(--muted);font-size:.9rem;margin-top:.35rem;line-height:1.5}
.kick{font-size:.7rem;font-weight:700;letter-spacing:.16em;color:var(--orange);text-transform:uppercase;margin-bottom:.55rem}
.card p{color:var(--muted);font-size:.93rem;line-height:1.65;margin:.55rem 0 0}
.card b{color:var(--ink)}
.card h4{font-family:var(--serif);margin:0 0 .35rem;font-size:1.15rem;font-weight:600;color:var(--ink)}
.dotrow{display:flex;gap:6px;margin-top:.5rem}
.dotrow i{width:10px;height:10px;border-radius:0 80% 0 80%;background:var(--c)}

/* headings */
.sec{font-family:var(--serif);font-size:2.1rem;font-weight:600;letter-spacing:-.02em;margin:.9rem 0 .2rem;color:var(--ink)}
.sec em{font-style:italic;color:var(--orange)}
.sub{color:var(--muted);font-size:1rem;margin-bottom:1.1rem;max-width:44rem;line-height:1.7}
.sec2{font-family:var(--serif);font-size:1.45rem;font-weight:600;margin:1.6rem 0 .2rem}

/* bars */
.bars{display:grid;gap:.75rem;margin-top:.5rem}
.bars>div{display:grid;grid-template-columns:var(--lw,170px) 1fr 62px;gap:.9rem;align-items:center;font-size:.92rem;color:var(--muted)}
.bars span.t{height:12px;border-radius:99px;background:#f1e2c9;overflow:hidden}
.bars span.t i{display:block;height:100%;width:0;border-radius:99px;animation:grow 1.2s var(--ease) .3s forwards}
.bars code{font-family:var(--serif);font-weight:600;color:var(--rust);font-size:1.05rem;text-align:right;background:none;padding:0}

/* table */
.tbl{width:100%;border-collapse:separate;border-spacing:0 8px}
.tbl th{font-size:.7rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--soft);text-align:left;padding:.2rem 1rem}
.tbl td{padding:.85rem 1rem;background:var(--card);border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:.93rem}
.tbl td:first-child{border-left:1px solid var(--line);border-radius:14px 0 0 14px;font-family:var(--serif);font-weight:600;font-size:1.02rem}
.tbl td:last-child{border-right:1px solid var(--line);border-radius:0 14px 14px 0}
.tbl tr:hover td{background:#fff3df}
.tbl td.n,.tbl th.n{text-align:right}
.tbl td.n{font-variant-numeric:tabular-nums}

/* pages (written text) */
.page{background:#fffaf0 repeating-linear-gradient(transparent,transparent 27px,#efdfc4 28px);border:1px solid var(--line);border-radius:6px 18px 18px 6px;
padding:.5rem 1.1rem .6rem 1.4rem;font-family:var(--serif);font-size:.98rem;line-height:28px;color:var(--ink);white-space:pre-wrap;word-break:break-word;
max-height:14.5rem;overflow:hidden;box-shadow:inset 6px 0 0 rgba(200,86,31,.18);margin-top:.7rem;-webkit-mask-image:linear-gradient(#000 80%,transparent);mask-image:linear-gradient(#000 80%,transparent)}
.stage{display:flex;justify-content:space-between;align-items:baseline;font-family:var(--serif);font-size:1.12rem;font-weight:600}
.stage em{font-style:normal;font-family:var(--sans);font-size:.78rem;color:var(--orange);font-weight:600}
.gen{background:#fffaf0 repeating-linear-gradient(transparent,transparent 31px,#efdfc4 32px);border:1px solid var(--line2);border-radius:8px 22px 22px 8px;
padding:.6rem 1.6rem .8rem 2rem;font-family:var(--serif);font-size:1.12rem;line-height:32px;color:var(--ink);white-space:pre-wrap;word-break:break-word;min-height:12rem;
box-shadow:inset 8px 0 0 rgba(200,86,31,.2),0 24px 50px rgba(156,61,27,.10);margin-top:.7rem}
.gen .p{color:var(--orange);font-weight:600;font-style:italic}
.gen .c{display:inline-block;width:2px;height:1.1em;background:var(--orange);vertical-align:text-bottom;margin-left:1px;animation:blink 1s steps(1) infinite}
.gen.empty{color:var(--soft);font-style:italic}

/* architecture */
.arch{display:grid;gap:8px;max-width:620px;margin:.8rem auto}
.node{background:var(--card);border:1px solid var(--line2);border-radius:16px;padding:.8rem 1.1rem;text-align:center;font-family:var(--serif);font-size:1.02rem;font-weight:600;
transition:transform .3s var(--ease),box-shadow .3s var(--ease)}
.node:hover{transform:translateY(-2px);box-shadow:0 12px 26px rgba(156,61,27,.12)}
.node small{display:block;color:var(--muted);font-family:var(--sans);font-weight:400;font-size:.8rem;margin-top:.2rem}
.node.attn{background:linear-gradient(160deg,#fde9c9,#f9d9a6);border-color:#e6b96d}
.node.ffn{background:linear-gradient(160deg,#eef0d2,#dfe5b3);border-color:#b8c277}
.node.io{background:linear-gradient(160deg,#fbe0cf,#f6c9ad);border-color:#e3a47f}
.node.add{background:transparent;border-style:dashed;color:var(--olive);font-family:var(--sans);font-weight:600;padding:.4rem 1rem;font-size:.85rem}
.dn{text-align:center;color:var(--orange);line-height:1;font-size:1.1rem}
.blk{position:relative;border:1.5px dashed var(--line2);border-radius:24px;padding:1.5rem 1rem 1rem;display:grid;gap:8px;background:rgba(243,230,210,.35);margin-top:14px}
.blk .x{position:absolute;top:-13px;left:50%;transform:translateX(-50%);background:var(--bg);color:var(--rust);font-family:var(--serif);font-style:italic;font-size:.95rem;padding:0 .9rem}

.foot{margin-top:2.8rem;padding-top:1.3rem;border-top:1px solid var(--line);color:var(--soft);font-size:.84rem;text-align:center;line-height:1.8}

/* streamlit widgets and charts */
[data-testid="stPlotlyChart"]{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:8px 8px 0}
label p{color:var(--muted) !important;font-size:.86rem !important;font-weight:600 !important}
.stTextArea textarea{background:#fffaf0 !important;border:1px solid var(--line2) !important;border-radius:14px !important;font-family:var(--serif) !important;font-size:1.05rem !important;color:var(--ink) !important}
.stButton>button{background:linear-gradient(100deg,var(--orange),#d9772b);border:0;color:#fff8ee;font-weight:700;border-radius:999px;padding:.6rem 1.8rem;
box-shadow:0 10px 24px rgba(200,86,31,.28);transition:transform .3s var(--ease),box-shadow .3s}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 16px 34px rgba(200,86,31,.38);color:#fff}
[data-baseweb="select"]>div{background:#fffaf0 !important;border-color:var(--line2) !important;border-radius:12px !important}

@media (max-width:900px){
.hero{grid-template-columns:1fr}.row3,.row4{grid-template-columns:1fr 1fr}.row2{grid-template-columns:1fr}
.paper{transform:none}.q p{font-size:1.25rem}.bars>div{grid-template-columns:110px 1fr 50px}
}
@media (max-width:600px){.row3,.row4{grid-template-columns:1fr}.brand-r .tagpill{display:none}}
@media (prefers-reduced-motion:reduce){
*{animation:none !important;transition:none !important}
.fade{opacity:1 !important}.leaf{display:none}.q:first-child{opacity:1}
.bars span.t i{width:var(--w) !important}
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# a few slowly falling leaves
LEAVES = [(6, 22, 19, 0, ORANGE), (17, 14, 24, 6, MUSTARD), (29, 18, 21, 11, RUST), (41, 12, 27, 3, OLIVE), (55, 20, 20, 9, MUSTARD),
          (66, 15, 25, 14, ORANGE), (77, 24, 22, 2, WINE), (88, 13, 26, 8, MUSTARD), (95, 18, 23, 16, RUST)]
st.markdown("".join(f'<div class="leaf" style="--x:{x}%;--s:{s}px;--t:{t}s;--d:-{d}s;--c:{c}"></div>' for x, s, t, d, c in LEAVES),
            unsafe_allow_html=True)


# ----------------------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------------------
def H(markup: str) -> None:
    """Render HTML. Whitespace between lines is removed so Markdown never treats it as a code block."""
    st.markdown("".join(line.strip() for line in markup.strip().splitlines()), unsafe_allow_html=True)


def esc(x) -> str:
    return html.escape(str(x))


def style_fig(fig, height=420):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=height,
        margin=dict(l=20, r=45, t=30, b=20),
        font=dict(family="DM Sans, sans-serif", size=13, color=INK),
        hoverlabel=dict(bgcolor="#fffaf0", bordercolor="#dcc3a0", font=dict(family="DM Sans, sans-serif", size=13, color=INK)),
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=13)),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor="#dcc3a0", tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor="#dcc3a0", tickfont=dict(color=MUTED))
    return fig


def show(fig):
    cfg = {"displayModeBar": False}
    try:
        st.plotly_chart(fig, width="stretch", config=cfg)
    except TypeError:                      # older Streamlit versions
        st.plotly_chart(fig, use_container_width=True, config=cfg)


def perplexity(loss):
    return math.exp(loss)


def read_text(path):
    p = ROOT / path
    return p.read_text(encoding="utf-8") if p.exists() else None


# ----------------------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------------------
# The bigram baseline was run before the training script saved logs, so its numbers are recorded here.
BIGRAM = {
    "steps": [0, 300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000],
    "val": [4.7323, 2.8207, 2.5606, 2.5107, 2.4982, 2.4960, 2.4971, 2.4842, 2.4983, 2.4917, 2.4837],
}
SAMPLES = {
    "bigram": "Awit slarridf fa.\nAntthasllmbaventhasals s ROUS:\nTherrshonou.\n\nTh, oldur.\nORUK:",
    "v1": "Ad alt pis.\nLI\nIfll the, Pom, at why Wyo wase ave nd halleal to oseast y's ghe tmy,\nI atne; wik.",
    "small": "Warwas in't be teye.\n\nGLOUS:\nAll AURENCESTIO: tha that and not\nThill rempease drened: what goes!\nThat see, my thoolds the forthered?\n\nSUCKING UCESTER:\nWhere one coming the lie of my it;",
}
BIG_FALLBACK = ("CAMILLO:\nAlas, as he limits something amongst alone,\nShall be a shepherd's bloody and unlook'd\n"
                "Can let call him false to see us with their pants\nAnd and tell him good to our parloud,\n"
                "And he shall be too preparent for no,")
QUOTES = [
    ("Alas, as he limits something amongst alone,", "CAMILLO"),
    ("Their bridegrow does with me at better days,", "VALERIA"),
    ("Twenty-thousand love me all my knightly heart", "KING RICHARD II"),
    ("The noble; for when they say hath a looked to know him", "VOLUMNIA"),
]

def read_json(path):
    p = ROOT / path
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def history_of(data):
    """Logs are either a plain list (early runs) or a dict with a 'history' key."""
    if data is None:
        return None
    return data if isinstance(data, list) else data["history"]


def read_text(path):
    p = ROOT / path
    return p.read_text(encoding="utf-8") if p.exists() else None


def perplexity(loss):
    return math.exp(loss)


# ----------------------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------------------
# The bigram baseline was run before the training script saved logs, so its numbers are recorded here.
BIGRAM = {
    "steps": [0, 300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000],
    "train": [4.7280, 2.8026, 2.5435, 2.5121, 2.4897, 2.4637, 2.4660, 2.4686, 2.4664, 2.4535, 2.4549],
    "val": [4.7323, 2.8207, 2.5606, 2.5107, 2.4982, 2.4960, 2.4971, 2.4842, 2.4983, 2.4917, 2.4837],
}
SAMPLES = {
    "bigram": "Awit slarridf fa.\nAntthasllmbaventhasals s ROUS:\nTherrshonou.\n\nTh, oldur.\nORUK:",
    "v1": "Ad alt pis.\nLI\nIfll the, Pom, at why Wyo wase ave nd halleal to oseast y's ghe tmy,\nI atne; wik.",
    "small": "Warwas in't be teye.\n\nGLOUS:\nAll AURENCESTIO: tha that and not\nThill rempease drened: what goes!\nThat see, my thoolds the forthered?\n\nSUCKING UCESTER:\nWhere one coming the lie of my it;",
}
BIG_FALLBACK = ("CAMILLO:\nAlas, as he limits something amongst alone,\nShall be a shepherd's bloody and unlook'd\n"
                "Can let call him false to see us with their pants\nAnd and tell him good to our parloud,\n"
                "And he shall be too preparent for no,")

big_log = read_json("logs/big.json")
big_hist = history_of(big_log)
v1_hist = history_of(read_json("logs/gpt_v1.json"))
small_hist = history_of(read_json("logs/small.json"))

if not big_hist:
    st.error("Training log not found. Copy `logs/big.json` (downloaded from Colab) into the project's `logs` folder.")
    st.stop()

big_cfg = big_log["config"] if isinstance(big_log, dict) else {}
N_LAYER = int(big_cfg.get("n_layer", 6))
N_HEAD = int(big_cfg.get("n_head", 6))
N_EMBD = int(big_cfg.get("n_embd", 384))
BLOCK = int(big_cfg.get("block_size", 256))
DROPOUT = float(big_cfg.get("dropout", 0.2))
LR = big_cfg.get("lr", 3e-4)
BATCH = int(big_cfg.get("batch_size", 64))
VOCAB = 65


def count_params(L, E, T, V):
    block = 3 * E * E + (E * E + E) + (E * 4 * E + 4 * E) + (4 * E * E + E) + 4 * E
    return {"Token embeddings": V * E, "Position embeddings": T * E, f"{L} transformer blocks": L * block,
            "Final layer norm": 2 * E, "Output layer": E * V + V}


PARTS = count_params(N_LAYER, N_EMBD, BLOCK, VOCAB)
N_PARAMS = sum(PARTS.values())

best = min(big_hist, key=lambda r: r["val"])
last = big_hist[-1]
at_best_train = best["train"]
secs_to_best = best.get("seconds")
after = [r for r in big_hist if r["step"] > best["step"]]
overfit = bool(after) and last["val"] > best["val"] + 0.01

runs = [
    ("Bigram", "1 character", "–", 4225, min(BIGRAM["val"]), "Looks at one character"),
    ("One attention head", "8 characters", "1 head", 7553, min(r["val"] for r in v1_hist) if v1_hist else 2.4021, "First self-attention"),
    ("Small GPT", "32 characters", "4 layers · 4 heads", 209729, min(r["val"] for r in small_hist) if small_hist else 1.8988, "Full transformer blocks"),
    ("Big GPT", f"{BLOCK} characters", f"{N_LAYER} layers · {N_HEAD} heads", N_PARAMS, best["val"], "Trained on a GPU"),
]


# ----------------------------------------------------------------------------------------
# Brand bar
# ----------------------------------------------------------------------------------------
H(f"""
<div class="brand fade">
<div class="logo"><i></i>Mini-GPT</div>
<div class="brand-r"><span class="tagpill"><b></b>Written from scratch in PyTorch</span>
<a class="ghlink" href="{GITHUB}" target="_blank" rel="noopener">GitHub ↗</a></div>
</div>
""")

tab_over, tab_train, tab_prog, tab_gen, tab_arch = st.tabs(["Overview", "Training", "Progress", "Write", "Architecture"])

# ========================================================================================
# Overview
# ========================================================================================
with tab_over:
    quotes = "".join(f'<div class="q" style="--k:{k}"><p>{esc(t)}</p><small>{esc(who)}, as imagined by the model</small></div>'
                     for k, (t, who) in enumerate(QUOTES))
    H(f"""
<div class="hero">
<div class="fade" style="--i:1">
<div class="eyebrow">A small language model, written from scratch</div>
<h1>Teaching a machine to <em>write Shakespeare.</em></h1>
<p class="lead">A {N_PARAMS/1e6:.1f}-million-parameter transformer, built by hand in PyTorch and trained on the plays of Shakespeare. It started out guessing letters at random, and learned spelling, rhythm and the shape of a script.</p>
<div class="chips"><span>Multi-head attention</span><span>Built layer by layer</span><span>Trained on a free GPU</span></div>
</div>
<div class="paper fade" style="--i:3">
<div class="quotes">{quotes}</div>
<div class="by"><span>Every line above was written by the model, one letter at a time.</span><b>Mini-GPT</b></div>
</div>
</div>
""")

    mins = f"{secs_to_best/60:.0f} min" if secs_to_best else "–"
    H(f"""
<div class="row3">
<div class="card fade" style="--i:2"><div class="kick">Size</div><div class="num">{N_PARAMS/1e6:.1f}M</div><div class="lab">parameters, the numbers the model adjusts while it learns</div></div>
<div class="card fade" style="--i:3"><div class="kick">Skill</div><div class="num">{perplexity(big_hist[0]['val']):.0f} → {perplexity(best['val']):.1f}</div><div class="lab">letters it is choosing between, down from guessing among all {VOCAB}</div></div>
<div class="card fade" style="--i:4"><div class="kick">Effort</div><div class="num">{mins}</div><div class="lab">to reach its best version, on a free cloud GPU</div></div>
</div>
<div class="row2">
<div class="card tint fade" style="--i:5"><div class="kick">The honest part</div><h4>It started to memorise.</h4>
<p>After step <b>{best['step']:,}</b> the model kept getting better on the text it studied but worse on text it had never seen. That is overfitting, so the model on the Write tab is the <b>best checkpoint</b>, not the last one.</p></div>
<div class="card tint fade" style="--i:6"><div class="kick">What it is, and is not</div><h4>Style without meaning.</h4>
<p>It writes convincing Shakespearean words, line breaks and speaker names. It does not understand what it writes, which is why the sentences drift into delightful nonsense.</p></div>
</div>
""")

# ========================================================================================
# Training
# ========================================================================================
with tab_train:
    H('<div class="sec">How it <em>learned</em></div><div class="sub">Loss measures how surprised the model is by the real next letter, so lower is better. '
      'The <b>train</b> line is text it studies; the <b>validation</b> line is text it has never seen.</div>')
    zoom = st.radio("View", ["Whole journey", "Zoom in (from step 1,000)"], horizontal=True, label_visibility="collapsed")
    hist = [r for r in big_hist if r["step"] >= 1000] if zoom.startswith("Zoom") else big_hist

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r["step"] for r in hist], y=[r["train"] for r in hist], name="Train (studied)", mode="lines+markers",
                             line=dict(color=MUSTARD, width=3), marker=dict(size=7),
                             hovertemplate="step %{x}<br>train %{y:.4f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[r["step"] for r in hist], y=[r["val"] for r in hist], name="Validation (unseen)", mode="lines+markers",
                             line=dict(color=RUST, width=3.5), marker=dict(size=8),
                             hovertemplate="step %{x}<br>validation %{y:.4f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[best["step"]], y=[best["val"]], name="Best version", mode="markers",
                             marker=dict(size=17, color=OLIVE, symbol="star", line=dict(color="#fffaf0", width=1.5)),
                             hovertemplate=f"best version<br>step {best['step']}<br>validation {best['val']:.4f}<extra></extra>"))
    if overfit:
        fig.add_vrect(x0=best["step"], x1=last["step"], fillcolor=ORANGE, opacity=0.09, line_width=0,
                      annotation_text="starts memorising", annotation_position="top left", annotation_font=dict(color=RUST, size=12))
    fig.update_xaxes(title="Training step")
    fig.update_yaxes(title="Loss")
    style_fig(fig, 430)
    show(fig)

    gap_best = best["val"] - best["train"]
    gap_end = last["val"] - last["train"]
    H(f"""
<div class="row4">
<div class="card"><div class="num">{best['val']:.3f}</div><div class="lab">best validation loss, at step {best['step']:,}</div></div>
<div class="card"><div class="num">{last['train']:.2f}</div><div class="lab">final train loss, step {last['step']:,}</div></div>
<div class="card"><div class="num">{last['val']:.2f}</div><div class="lab">final validation loss, {'worse than its best' if overfit else 'still improving'}</div></div>
<div class="card"><div class="num">{gap_end:.2f}</div><div class="lab">gap between the two at the end (it was {gap_best:.2f} at the best step)</div></div>
</div>
""")
    if overfit:
        H(f"""
<div class="card tint"><div class="kick">What happened</div>
<h4>A student who memorised the textbook</h4>
<p>After step <b>{best['step']:,}</b>, train loss kept falling ({at_best_train:.2f} → {last['train']:.2f}) while validation loss crept up ({best['val']:.2f} → {last['val']:.2f}).
The model had begun learning the training text by heart instead of the patterns behind it. Dropout ({DROPOUT}) slows this down but cannot stop it, so the training script saves a checkpoint every time validation loss improves and the Write tab uses that one.</p></div>
""")
    H(f"""
<div class="sec2">The recipe</div>
<div class="row3">
<div class="card"><div class="kick">Optimiser</div><div class="num" style="font-size:1.7rem">AdamW</div><div class="lab">learning rate {LR}</div></div>
<div class="card"><div class="kick">Each step</div><div class="num" style="font-size:1.7rem">{BATCH} × {BLOCK}</div><div class="lab">{BATCH*BLOCK:,} letters read per step</div></div>
<div class="card"><div class="kick">The book</div><div class="num" style="font-size:1.7rem">1.1M letters</div><div class="lab">Tiny Shakespeare · 90% to study, 10% held back to test</div></div>
</div>
""")

# ========================================================================================
# Progress
# ========================================================================================
with tab_prog:
    H('<div class="sec">Four models, <em>one book</em></div><div class="sub">Each model was built to fix a weakness of the one before it. '
      'Same text, same test, same score.</div>')

    worst = max(r[4] for r in runs)
    cols = [MUSTARD, OLIVE, WINE, ORANGE]
    bars = "".join(
        f'<div>{esc(r[0])}<span class="t"><i style="--w:{r[4]/worst*100:.0f}%;background:linear-gradient(90deg,{c},{c}cc)"></i></span><code>{r[4]:.2f}</code></div>'
        for r, c in zip(runs, cols))
    H(f"""
<div class="card"><div class="kick">Best validation loss · shorter is better</div><div class="bars" style="--lw:170px">{bars}</div></div>
""")

    fig = go.Figure()
    series = [("Bigram", BIGRAM["steps"], BIGRAM["val"], MUSTARD)]
    if v1_hist:
        series.append(("One attention head", [r["step"] for r in v1_hist], [r["val"] for r in v1_hist], OLIVE))
    if small_hist:
        series.append(("Small GPT", [r["step"] for r in small_hist], [r["val"] for r in small_hist], WINE))
    series.append(("Big GPT", [r["step"] for r in big_hist], [r["val"] for r in big_hist], ORANGE))
    for name, xs, ys, col in series:
        fig.add_trace(go.Scatter(x=xs, y=ys, name=name, mode="lines", line=dict(color=col, width=3.5),
                                 hovertemplate=name + "<br>step %{x}<br>validation %{y:.3f}<extra></extra>"))
    fig.update_xaxes(title="Training step")
    fig.update_yaxes(title="Validation loss", range=[1.3, 3.0])
    style_fig(fig, 400)
    st.write("")
    show(fig)

    body = ""
    for name, ctx, shape, params, val, note in runs:
        body += (f"<tr><td>{esc(name)}</td><td>{esc(ctx)}</td><td>{esc(shape)}</td><td class='n'>{params:,}</td>"
                 f"<td class='n'>{val:.3f}</td><td class='n'>≈ {perplexity(val):.1f}</td></tr>")
    H(f"""
<table class="tbl"><thead><tr><th>Model</th><th>Memory</th><th>Shape</th><th class="n">Parameters</th><th class="n">Loss</th><th class="n">Letters it weighs</th></tr></thead>
<tbody>{body}</tbody></table>
""")

    big_text = (read_text("logs/big_best_sample.txt") or read_text("logs/big_sample.txt") or BIG_FALLBACK).strip()

    def page_card(stage, note, text):
        return (f'<div class="card" style="padding:1.1rem 1.2rem"><div class="stage">{esc(stage)}<em>{esc(note)}</em></div>'
                f'<div class="page">{esc(text.strip()[:380]).replace(chr(10), "<br>")}</div></div>')

    H('<div class="sec2">Four pages, four authors</div><div class="sub">Every page starts from a blank slate. Same book, bigger brain.</div>')
    H('<div class="row2">'
      + page_card("Bigram", f"loss {runs[0][4]:.2f}", SAMPLES["bigram"])
      + page_card("One attention head", f"loss {runs[1][4]:.2f}", SAMPLES["v1"])
      + page_card("Small GPT", f"loss {runs[2][4]:.2f}", SAMPLES["small"])
      + page_card("Big GPT", f"loss {runs[3][4]:.2f}", big_text)
      + "</div>")

# ========================================================================================
# Write
# ========================================================================================
with tab_gen:
    H('<div class="sec">Let it <em>write</em></div><div class="sub">Give it the start of a line and it will continue, one letter at a time. '
      'It has learned how Shakespeare looks, not what he meant, so expect lovely words and wandering sentences.</div>')

    CKPT = next((p for p in ["checkpoints/big_best.pt", "checkpoints/big.pt"] if (ROOT / p).exists()), None)

    if CKPT is None:
        st.info("The trained model file is not in this project yet. Copy `checkpoints/big_best.pt` from Colab into the `checkpoints` folder.")
    else:
        @st.cache_resource(show_spinner="Opening the model...")
        def load_model(path):
            import torch
            from model import GPT, GPTConfig
            ck = torch.load(ROOT / path, map_location="cpu")
            model = GPT(GPTConfig(**ck["config"]))
            model.load_state_dict(ck["model"])
            model.eval()
            text = (ROOT / "data" / "input.txt").read_text(encoding="utf-8")
            chars = sorted(set(text))
            return model, {c: i for i, c in enumerate(chars)}, {i: c for i, c in enumerate(chars)}

        model, stoi, itos = load_model(CKPT)

        def stream(prompt_ids, n_new, temperature, seed):
            import torch
            import torch.nn.functional as F
            torch.manual_seed(seed)
            idx = torch.tensor([prompt_ids], dtype=torch.long)
            block = model.cfg.block_size
            with torch.no_grad():
                for _ in range(n_new):
                    logits, _ = model(idx[:, -block:])
                    probs = F.softmax(logits[:, -1, :] / temperature, dim=-1)
                    nxt = torch.multinomial(probs, 1)
                    idx = torch.cat((idx, nxt), dim=1)
                    yield itos[int(nxt)]

        c1, c2 = st.columns([3, 2], gap="large")
        with c1:
            prompt = st.text_area("Begin the line", value="ROMEO:\n", height=110)
        with c2:
            n_new = st.slider("How much to write (letters)", 50, 500, 250, step=50)
            temp = st.slider("Boldness (higher is wilder)", 0.3, 1.5, 0.8, step=0.1)
        go_btn = st.button("Write for me")

        def page_html(shown, out, cursor):
            return ('<div class="gen"><span class="p">' + esc(shown).replace("\n", "<br>") + "</span>"
                    + esc(out).replace("\n", "<br>") + ('<span class="c"></span>' if cursor else "") + "</div>")

        if go_btn:
            ids = [stoi[c] for c in prompt if c in stoi] or [stoi["\n"]]
            dropped = len(prompt) - len([c for c in prompt if c in stoi])
            if dropped:
                st.caption(f"Skipped {dropped} character(s) the model has never seen (it only knows the {len(stoi)} characters used in Shakespeare).")
            shown = "".join(itos[i] for i in ids)
            box = st.empty()
            out = ""
            for k, ch in enumerate(stream(ids, n_new, temp, seed=int(__import__("time").time()) % 100000)):
                out += ch
                if k % 3 == 0:
                    box.markdown(page_html(shown, out, True), unsafe_allow_html=True)
            box.markdown(page_html(shown, out, False), unsafe_allow_html=True)
        else:
            H('<div class="gen empty">Press the button. Your words appear in orange and the model\'s writing follows in brown.</div>')

# ========================================================================================
# Architecture
# ========================================================================================
with tab_arch:
    hs = N_EMBD // N_HEAD
    H('<div class="sec">Inside the <em>machine</em></div><div class="sub">A decoder-only transformer, the same family of design as GPT. '
      'Text enters at the top and a guess for the next letter leaves at the bottom.</div>')
    H(f"""
<div class="arch">
<div class="node io">The letters so far<small>up to {BLOCK} letters of memory · an alphabet of {VOCAB} symbols</small></div><div class="dn">↓</div>
<div class="node io">Embeddings<small>each letter becomes {N_EMBD} numbers, plus a sense of where it sits</small></div>
<div class="blk"><span class="x">repeated {N_LAYER} times</span>
<div class="node">Layer norm</div>
<div class="node attn">Multi-head attention<small>{N_HEAD} heads of {hs} dimensions look back at earlier letters to decide what matters</small></div>
<div class="node add">+ shortcut that keeps the original signal</div>
<div class="node">Layer norm</div>
<div class="node ffn">Feed-forward network<small>{N_EMBD} → {4*N_EMBD} → {N_EMBD}: each letter thinks about what it gathered</small></div>
<div class="node add">+ shortcut that keeps the original signal</div>
</div>
<div class="dn">↓</div>
<div class="node">Final layer norm</div><div class="dn">↓</div>
<div class="node io">Next-letter probabilities<small>{N_EMBD} → {VOCAB}: a score for every possible next letter</small></div>
</div>
""")

    pcolors = [MUSTARD, OLIVE, ORANGE, WINE, RUST]
    parts_html = "".join(
        f'<div>{esc(k)}<span class="t"><i style="--w:{max(v/N_PARAMS*100, 1.5):.1f}%;background:{c}"></i></span><code>{v/1e6:.2f}M</code></div>'
        for (k, v), c in zip(PARTS.items(), pcolors))
    H(f"""
<div class="card" style="margin-top:1.2rem"><div class="kick">Where the {N_PARAMS:,} parameters live</div>
<div class="bars" style="--lw:200px">{parts_html}</div>
<p>Almost all of them sit in the repeated blocks: the attention layers hold {4*N_EMBD*N_EMBD/1e6:.2f}M and the feed-forward network {8*N_EMBD*N_EMBD/1e6:.2f}M in every block.</p></div>
""")
    H("""
<div class="sec2">Choices and limits</div>
<div class="row3">
<div class="card"><div class="kick">Letters, not words</div><p>The model reads one character at a time, only 65 symbols in all. It needs no dictionary, but it has to learn spelling before it can learn anything else.</p></div>
<div class="card"><div class="kick">Looking backwards</div><p>Each position may only look at earlier letters, so training matches how the model writes: one letter at a time, never peeking ahead.</p></div>
<div class="card"><div class="kick">A small library</div><p>Only 1.1 million letters of text, so the model overfits quickly. It learns the look of Shakespeare rather than the meaning.</p></div>
</div>
""")

H(f"""
<div class="foot">Made with care by Anoushka Yadav · <a href="{GITHUB}" target="_blank" rel="noopener">github.com/anuu-yd9/mini-gpt</a><br>
Trained on the Tiny Shakespeare text, which is in the public domain. Not affiliated with OpenAI.</div>
""")
