"""Mini-GPT: a transformer language model built from scratch (Streamlit dashboard)."""
import html
import json
import math
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Mini-GPT", page_icon="🧠", layout="wide")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))   # so `from model import ...` works anywhere
GITHUB = "https://github.com/anuu-yd9/mini-gpt"
BLUE, VIOLET, PINK, GREEN, AMBER, RED = "#3b82f6", "#8b5cf6", "#ec4899", "#2dd4a0", "#f5a524", "#ff5d73"

# ----------------------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
:root{--ease:cubic-bezier(.22,1,.36,1);--panel:#07080c;--panel2:#0c0e14;--line:#1b1e2b;--line-hi:#2c3350;
--text:#f4f5f7;--muted:#9aa1b2;--dim:#7d8497;--blue:#3b82f6;--violet:#8b5cf6;--pink:#ec4899;--green:#2dd4a0;
--mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
html,body,.stApp{font-family:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif}
.stApp{background:radial-gradient(1100px 460px at 50% -140px,rgba(59,130,246,.17),transparent 62%),
radial-gradient(700px 380px at 92% 8%,rgba(139,92,246,.10),transparent 60%),#000}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{visibility:hidden;height:0}
.block-container{max-width:1180px;padding-top:1.2rem;padding-bottom:3.5rem}
h1,h2,h3,p,li,label{letter-spacing:-.01em}
a{color:#8fb4ff;text-decoration:none} a:hover{color:#fff}

@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes grow{to{width:var(--w)}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes typing{from{width:0}to{width:calc(var(--n)*1ch)}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(45,212,160,.5)}50%{box-shadow:0 0 0 6px rgba(45,212,160,0)}}
.fade{opacity:0;animation:up .75s var(--ease) forwards;animation-delay:calc(var(--i,0)*70ms)}

/* tabs */
.stTabs [data-baseweb="tab-list"]{gap:.2rem;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:50;
background:rgba(0,0,0,.84);backdrop-filter:blur(14px);padding-top:.35rem;margin-bottom:.6rem}
.stTabs [data-baseweb="tab"]{height:46px;padding:0 16px;font-weight:600;font-size:.95rem;color:var(--muted);border-radius:10px 10px 0 0;
transition:color .25s var(--ease),background .25s var(--ease)}
.stTabs [data-baseweb="tab"]:hover{color:#fff;background:rgba(255,255,255,.05)}
.stTabs [aria-selected="true"]{color:#fff}
.stTabs [data-baseweb="tab-highlight"]{background:linear-gradient(90deg,var(--blue),var(--violet));height:2px}
.stTabs [data-baseweb="tab-border"]{display:none}

/* brand bar */
.brand{display:flex;justify-content:space-between;align-items:center;padding:.2rem 0 .9rem}
.logo{font-size:1.05rem;font-weight:700;letter-spacing:-.02em;display:flex;align-items:center;gap:.55rem}
.logo i{display:grid;place-items:center;width:32px;height:32px;border-radius:9px;font-style:normal;
background:linear-gradient(135deg,var(--blue),var(--violet));box-shadow:0 6px 20px rgba(59,130,246,.35)}
.brand-r{display:flex;gap:.8rem;align-items:center;font-size:.82rem;color:var(--muted)}
.live{display:inline-flex;gap:.5rem;align-items:center;padding:.32rem .75rem;border:1px solid var(--line);border-radius:999px;background:var(--panel)}
.live b{width:8px;height:8px;border-radius:50%;background:var(--green);animation:pulse 2.2s infinite}
.ghlink{padding:.32rem .8rem;border:1px solid var(--line);border-radius:999px;transition:all .3s var(--ease);color:#cfd5e4}
.ghlink:hover{border-color:var(--blue);color:#fff;transform:translateY(-1px)}

/* hero */
.hero{display:grid;grid-template-columns:1.1fr 1fr;gap:2.2rem;align-items:center;padding:1.6rem 0 1.2rem}
.eyebrow{font-family:var(--mono);font-size:.74rem;font-weight:500;letter-spacing:.14em;color:var(--blue);margin-bottom:.9rem}
.hero h1{font-size:clamp(2.3rem,4.6vw,3.7rem);font-weight:800;line-height:1.04;letter-spacing:-.035em;margin:0;padding:0;color:var(--text)}
.grad{background:linear-gradient(92deg,#3b82f6 0%,#8b5cf6 55%,#ec4899 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
.lead{color:var(--muted);font-size:1.06rem;line-height:1.65;margin:1.1rem 0 1.2rem;max-width:34rem}
.chips{display:flex;flex-wrap:wrap;gap:.5rem}
.chips span{font-size:.8rem;font-weight:500;color:#cfd5e4;padding:.34rem .8rem;border:1px solid var(--line);border-radius:999px;background:var(--panel);
transition:all .3s var(--ease)}
.chips span:hover{border-color:var(--blue);transform:translateY(-2px);color:#fff}

/* terminal */
.term{background:#0a0b10;border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:0 30px 80px rgba(59,130,246,.10);
transition:border-color .4s var(--ease),transform .4s var(--ease)}
.term:hover{border-color:var(--line-hi);transform:translateY(-3px)}
.term .bar{display:flex;align-items:center;gap:.4rem;padding:.65rem .9rem;background:#12141c;border-bottom:1px solid var(--line)}
.term .bar i{width:11px;height:11px;border-radius:50%;display:inline-block}
.term .bar span{margin-left:.6rem;color:var(--dim);font-family:var(--mono);font-size:.74rem}
.term .body{padding:1rem 1.15rem 1.2rem;font-family:var(--mono);font-size:.76rem;line-height:1.85;min-height:250px}
.tl{white-space:nowrap;overflow:hidden;text-overflow:clip}
.ps{color:var(--green)} .pm{color:var(--dim)}
.typed{display:inline-block;overflow:hidden;white-space:nowrap;vertical-align:bottom;width:0;box-sizing:content-box;padding-right:.6ch;color:#7fb2ff;
animation:typing var(--t) steps(var(--n),end) var(--d) forwards}
.tl.out{opacity:0;animation:up .45s var(--ease) var(--d) forwards;color:#e6e9f2;white-space:normal}
.tl.out b{color:var(--green);font-weight:600} .tl.out em{color:var(--dim);font-style:normal}
.cur{display:inline-block;width:.6ch;height:1.05em;background:#e5e7eb;vertical-align:text-bottom;opacity:0;animation:blink 1s steps(1) infinite;animation-delay:var(--d)}

/* cards, bento */
.bento{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin:.4rem 0 1.2rem}
.card{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:1.15rem 1.3rem;
transition:transform .35s var(--ease),border-color .35s var(--ease),box-shadow .35s var(--ease)}
.card:hover{transform:translateY(-4px);border-color:var(--line-hi);box-shadow:0 18px 50px rgba(59,130,246,.09)}
.s2{grid-column:span 2} .s3{grid-column:span 3} .s6{grid-column:span 6}
.num{font-size:2.15rem;font-weight:800;letter-spacing:-.035em;line-height:1.1;background:linear-gradient(95deg,#fff,#a9c3ff);-webkit-background-clip:text;background-clip:text;color:transparent}
.lab{color:var(--muted);font-size:.84rem;margin-top:.25rem}
.kick{font-family:var(--mono);font-size:.7rem;letter-spacing:.12em;color:var(--dim);text-transform:uppercase;margin-bottom:.5rem}
.card p{color:var(--muted);font-size:.9rem;line-height:1.6;margin:.5rem 0 0}
.card b{color:var(--text)}
.dots{display:grid;grid-template-columns:repeat(20,1fr);gap:4px;margin-top:.8rem}
.dots i{aspect-ratio:1;border-radius:3px;background:#161926}
.dots i.on{background:linear-gradient(135deg,var(--blue),var(--violet));opacity:0;animation:up .5s var(--ease) forwards;animation-delay:calc(var(--k)*45ms + .4s)}
.cmp{margin-top:.8rem;display:grid;gap:.5rem}
.cmp div{display:grid;grid-template-columns:110px 1fr 64px;gap:.7rem;align-items:center;font-size:.8rem;color:var(--muted)}
.cmp span.t{height:8px;border-radius:99px;background:#161926;overflow:hidden}
.cmp span.t i{display:block;height:100%;width:0;border-radius:99px;animation:grow 1.1s var(--ease) .5s forwards}
.cmp code{font-family:var(--mono);color:var(--text);font-size:.8rem;text-align:right;white-space:nowrap}
.bug{display:flex;gap:1.2rem;align-items:center;flex-wrap:wrap}
.bug .big{font-family:var(--mono);font-size:1.5rem;font-weight:600}
.bug .old{color:var(--dim);text-decoration:line-through;text-decoration-color:var(--red)}
.bug .arrow{color:var(--blue)}
.explore{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-top:.2rem}
.explore .card{padding:1rem 1.1rem}
.explore h4{margin:0 0 .3rem;font-size:.95rem;font-weight:700;color:var(--text)}
.explore p{margin:0;font-size:.82rem}

/* headings */
.sec{font-size:1.75rem;font-weight:800;letter-spacing:-.03em;margin:.8rem 0 .15rem;color:var(--text)}
.sub{color:var(--muted);font-size:.95rem;margin-bottom:1rem;max-width:46rem;line-height:1.6}

/* leaderboard */
.lb{display:grid;gap:8px;margin:.6rem 0 .8rem}
.lb-row{display:grid;grid-template-columns:34px minmax(150px,1.1fr) 2.4fr 76px 110px;gap:14px;align-items:center;padding:.62rem .9rem;
background:var(--panel);border:1px solid var(--line);border-radius:12px;opacity:0;animation:up .55s var(--ease) forwards;animation-delay:calc(var(--i)*45ms);
transition:border-color .3s var(--ease),transform .3s var(--ease),background .3s var(--ease)}
.lb-row:hover{border-color:var(--line-hi);transform:translateX(4px);background:var(--panel2)}
.rk{font-family:var(--mono);color:var(--dim);font-size:.85rem;text-align:center}
.lb-row:nth-child(1) .rk{color:#ffd166;font-weight:700}.lb-row:nth-child(2) .rk{color:#cfd5e4;font-weight:700}.lb-row:nth-child(3) .rk{color:#e09f6e;font-weight:700}
.nm{font-weight:600;font-size:.95rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nm em{font-style:normal;font-family:var(--mono);font-size:.76rem;color:var(--dim);margin-left:.5rem;font-weight:400}
.track{height:10px;border-radius:99px;background:#141725;overflow:hidden}
.fill{display:block;height:100%;width:0;border-radius:99px;background:linear-gradient(90deg,var(--blue),var(--violet));animation:grow 1s var(--ease) forwards;animation-delay:calc(var(--i)*45ms + .15s)}
.val{white-space:nowrap;min-width:4.4em;font-family:var(--mono);font-weight:600;font-size:.92rem;text-align:right;color:#cfe0ff}
.meta{font-size:.76rem;color:var(--dim);text-align:right;white-space:nowrap}
.tag{display:inline-block;font-size:.68rem;padding:.1rem .45rem;border:1px solid #4a3a1a;color:#e6b455;border-radius:6px;margin-left:.4rem}

/* scouting */
.hdr{display:flex;gap:1.1rem;align-items:center;padding:1.2rem 1.4rem}
.av{width:62px;height:62px;border-radius:18px;display:grid;place-items:center;font-size:1.35rem;font-weight:800;
background:linear-gradient(135deg,var(--blue),var(--violet));box-shadow:0 10px 30px rgba(59,130,246,.3);flex:none}
.hdr h2{margin:0;font-size:1.65rem;font-weight:800;letter-spacing:-.03em;display:flex;gap:.7rem;align-items:center;flex-wrap:wrap}
.pill{display:inline-block;font-size:.74rem;font-weight:600;letter-spacing:0;padding:.22rem .7rem;border-radius:999px;border:1px solid;white-space:nowrap}
.verdict{color:#c9cfdd;font-size:.95rem;margin-top:.35rem;line-height:1.6}
.verdict b{color:#fff}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:14px 0}
.kpi .num{font-size:1.9rem}
.pbar{height:6px;border-radius:99px;background:#161926;margin-top:.7rem;overflow:hidden}
.pbar i{display:block;height:100%;width:0;border-radius:99px;background:linear-gradient(90deg,var(--blue),var(--violet));animation:grow 1s var(--ease) .3s forwards}
.pt{font-size:.74rem;color:var(--dim);margin-top:.35rem}

/* tables */
.tbl{width:100%;border-collapse:separate;border-spacing:0 6px}
.tbl th{font-size:.72rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);text-align:left;padding:.2rem .9rem}
.tbl td{padding:.7rem .9rem;background:var(--panel);border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:.9rem;transition:background .25s}
.tbl td:first-child{border-left:1px solid var(--line);border-radius:12px 0 0 12px;font-weight:600}
.tbl td:last-child{border-right:1px solid var(--line);border-radius:0 12px 12px 0}
.tbl tr:hover td{background:var(--panel2)}
.tbl td.n,.tbl th.n{text-align:right;font-family:var(--mono)}

/* tale of the tape */
.tape{display:grid;gap:8px;margin-top:.5rem}
.tp{display:grid;grid-template-columns:74px 1fr 170px 1fr 74px;gap:12px;align-items:center;padding:.62rem .9rem;background:var(--panel);border:1px solid var(--line);border-radius:12px;transition:border-color .3s var(--ease)}
.tp:hover{border-color:var(--line-hi)}
.tp .v{font-family:var(--mono);font-weight:600;font-size:.92rem;color:var(--dim)} .tp .v.w{color:#fff}
.tp .v.l{text-align:left} .tp .v.r{text-align:right}
.tp .lbl{text-align:center;font-size:.8rem;color:var(--muted)}
.tp .b{height:10px;border-radius:99px;background:#141725;display:flex;overflow:hidden}
.tp .b.l{justify-content:flex-end}
.tp .b i{display:block;height:100%;width:0;border-radius:99px;animation:grow 1s var(--ease) .2s forwards}
.tph{display:grid;grid-template-columns:1fr 1fr;gap:12px;font-weight:700;font-size:1.05rem;margin-bottom:.2rem}
.tph div:last-child{text-align:right}

/* style cards */
.scards{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-top:1rem}
.sc{border-top:3px solid var(--c)}
.sc h4{margin:.1rem 0 .15rem;font-size:1rem;font-weight:700;line-height:1.25}
.sc .cnt{font-family:var(--mono);font-size:.74rem;color:var(--dim)}
.trait{display:inline-block;font-size:.74rem;padding:.2rem .55rem;margin:.25rem .25rem 0 0;border-radius:7px;background:#11141d;border:1px solid var(--line);color:#cfd5e4}
.trait.up{color:#9be7c7}.trait.dn{color:#ffa3b1}
.sc .ex{margin-top:.8rem;font-size:.78rem;color:var(--muted);line-height:1.5}

/* method */
.flow{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:.6rem 0 1rem;align-items:stretch}
.step{position:relative}
.step .no{font-family:var(--mono);font-size:.72rem;color:var(--blue)}
.step h4{margin:.25rem 0 .3rem;font-size:.95rem}
.step p{font-size:.8rem !important}
.step:not(:last-child)::after{content:"→";position:absolute;right:-13px;top:50%;transform:translateY(-50%);color:var(--blue);z-index:2;font-size:1rem}
.good{color:#9be7c7}.bad{color:#ffa3b1}
.foot{margin-top:2.6rem;padding-top:1.2rem;border-top:1px solid var(--line);color:var(--dim);font-size:.82rem;text-align:center;line-height:1.7}

/* streamlit widgets and charts */
[data-testid="stPlotlyChart"]{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:6px 6px 0;transition:border-color .35s var(--ease)}
[data-testid="stPlotlyChart"]:hover{border-color:var(--line-hi)}
[data-testid="stExpander"]{border:1px solid var(--line);border-radius:14px;background:var(--panel);margin-bottom:.7rem}
[data-testid="stExpander"] summary{font-weight:600}
[data-testid="stExpander"] summary:hover{color:#fff}
label p{color:var(--muted) !important;font-size:.84rem !important;font-weight:500 !important}
[data-baseweb="select"]>div{background:var(--panel) !important;border-color:var(--line) !important;border-radius:12px !important;transition:border-color .25s}
[data-baseweb="select"]>div:hover{border-color:var(--line-hi) !important}

@media (max-width:900px){
.hero{grid-template-columns:1fr}.bento{grid-template-columns:repeat(2,1fr)}.s2,.s3,.s6{grid-column:span 2}
.explore,.scards,.flow{grid-template-columns:1fr 1fr}.kpis{grid-template-columns:1fr 1fr}.step:not(:last-child)::after{display:none}
.lb-row{grid-template-columns:30px 1fr 70px}.lb-row .track,.lb-row .meta{display:none}
.tp{grid-template-columns:56px 1fr 56px}.tp .b,.tp .lbl{display:none}.tp .lbl{display:block;grid-column:1/-1;order:-1}
}
@media (prefers-reduced-motion:reduce){
*{animation:none !important;transition:none !important}
.fade,.lb-row,.tl.out,.dots i.on{opacity:1 !important}
.typed{width:calc(var(--n)*1ch) !important}
.fill,.cmp span.t i,.pbar i,.tp .b i{width:var(--w) !important}
.cur{opacity:1 !important}
}
/* mini-gpt additions */
.sample{font-family:var(--mono);font-size:.76rem;line-height:1.7;color:#d7dcea;white-space:pre-wrap;word-break:break-word;margin-top:.7rem;max-height:14rem;overflow:hidden;
-webkit-mask-image:linear-gradient(#000 78%,transparent);mask-image:linear-gradient(#000 78%,transparent)}
.grid2{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:.6rem 0}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:.6rem 0}
.stage{font-family:var(--mono);font-size:.7rem;letter-spacing:.1em;color:var(--blue);text-transform:uppercase}
.stage em{font-style:normal;color:var(--dim);margin-left:.5rem}
.gen{background:#0a0b10;border:1px solid var(--line);border-radius:16px;padding:1.2rem 1.4rem;font-family:var(--mono);font-size:.9rem;line-height:1.75;color:#e6e9f2;
white-space:pre-wrap;word-break:break-word;min-height:9rem;margin-top:.6rem}
.gen .p{color:#7fb2ff}
.gen .c{display:inline-block;width:.6ch;height:1.05em;background:#e5e7eb;vertical-align:text-bottom;animation:blink 1s steps(1) infinite}
.arch{display:grid;gap:8px;max-width:640px;margin:.6rem auto}
.node{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:.7rem 1rem;text-align:center;font-size:.92rem;font-weight:600;
transition:border-color .3s var(--ease),transform .3s var(--ease)}
.node:hover{border-color:var(--blue);transform:translateY(-2px)}
.node small{display:block;color:var(--dim);font-family:var(--mono);font-weight:400;font-size:.72rem;margin-top:.15rem}
.dn{text-align:center;color:var(--blue);line-height:1}
.blk{position:relative;border:1px dashed var(--line-hi);border-radius:18px;padding:1.3rem .9rem .9rem;display:grid;gap:8px;background:rgba(59,130,246,.04)}
.blk .x{position:absolute;top:-11px;left:50%;transform:translateX(-50%);background:#000;color:var(--blue);font-family:var(--mono);font-size:.76rem;padding:0 .7rem;border-radius:99px}
.node.hl{border-color:#2f5fb8;background:rgba(59,130,246,.08)}
.node.add{border-style:dashed;color:var(--green);font-weight:500;padding:.35rem 1rem;font-size:.82rem}
.ok{color:#9be7c7}.warn{color:#e6b455}
.stButton>button{background:linear-gradient(95deg,#3b82f6,#8b5cf6);border:0;color:#fff;font-weight:700;border-radius:12px;padding:.55rem 1.4rem;transition:transform .25s var(--ease),box-shadow .25s}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(59,130,246,.35);color:#fff}
.stTextArea textarea{background:var(--panel) !important;border:1px solid var(--line) !important;border-radius:12px !important;font-family:var(--mono) !important}
@media (max-width:900px){.grid2,.grid3{grid-template-columns:1fr}}
.blk{margin-top:14px}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


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
        margin=dict(l=20, r=20, t=24, b=20),
        font=dict(family="Inter, sans-serif", size=13, color="#cfd5e4"),
        hoverlabel=dict(bgcolor="#12141c", bordercolor="#2c3350", font=dict(family="Inter, sans-serif", size=13, color="#f4f5f7")),
        legend=dict(orientation="h", y=1.1, x=0),
    )
    fig.update_xaxes(gridcolor="#171a26", zeroline=False, linecolor="#1f2333")
    fig.update_yaxes(gridcolor="#171a26", zeroline=False, linecolor="#1f2333")
    return fig


def show(fig):
    cfg = {"displayModeBar": False}
    try:
        st.plotly_chart(fig, width="stretch", config=cfg)
    except TypeError:                      # older Streamlit versions
        st.plotly_chart(fig, use_container_width=True, config=cfg)


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
<div class="logo"><i>🧠</i>Mini-GPT</div>
<div class="brand-r"><span class="live"><b></b>Trained from scratch · PyTorch</span>
<a class="ghlink" href="{GITHUB}" target="_blank" rel="noopener">GitHub ↗</a></div>
</div>
""")

tab_over, tab_train, tab_prog, tab_gen, tab_arch = st.tabs(["Overview", "Training", "Progress", "Generate", "Architecture"])

# ========================================================================================
# Overview
# ========================================================================================
with tab_over:
    script = [
        ("cmd", f"gpt train --layers {N_LAYER} --heads {N_HEAD} --embd {N_EMBD}"),
        ("out", f"<b>{N_PARAMS:,}</b> <em>parameters · trained on a free T4 GPU</em>"),
        ("cmd", "gpt eval --split val"),
        ("out", f"loss <b>{big_hist[0]['val']:.2f} → {best['val']:.2f}</b> <em>in {best['step']:,} steps</em>"),
        ("cmd", "gpt generate --prompt CAMILLO:"),
        ("out", "<em>Alas, as he limits something amongst alone,</em>"),
    ]
    t, rows = 0.5, []
    for kind, text in script:
        if kind == "cmd":
            n = len(text)
            dur = round(n * 0.03, 2)
            rows.append(f'<div class="tl"><span class="ps">gpt@t4</span> <span class="pm">~ %</span> '
                        f'<span class="typed" style="--n:{n};--t:{dur}s;--d:{t:.2f}s">{esc(text)}</span></div>')
            t += dur + 0.3
        else:
            rows.append(f'<div class="tl out" style="--d:{t:.2f}s">{text}</div>')
            t += 0.55
    rows.append(f'<div class="tl"><span class="ps">gpt@t4</span> <span class="pm">~ %</span> <span class="cur" style="--d:{t:.2f}s"></span></div>')

    H(f"""
<div class="hero">
<div class="fade" style="--i:1">
<div class="eyebrow">TRANSFORMER LANGUAGE MODEL</div>
<h1>A GPT built<br><span class="grad">from scratch.</span></h1>
<p class="lead">A {N_PARAMS/1e6:.1f}M-parameter character-level transformer in PyTorch, trained on Shakespeare. No pretrained weights and no model libraries: attention, layer norm and the training loop are all written by hand.</p>
<div class="chips"><span>Multi-head attention</span><span>Residuals + LayerNorm</span><span>Trained on a GPU</span></div>
</div>
<div class="term fade" style="--i:3"><div class="bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i><span>gpt: zsh</span></div>
<div class="body">{''.join(rows)}</div></div>
</div>
""")

    mins = f"{secs_to_best/60:.0f} min" if secs_to_best else "–"
    H(f"""
<div class="bento">
<div class="card s2 fade" style="--i:2"><div class="num">{N_PARAMS/1e6:.1f}M</div><div class="lab">Parameters</div></div>
<div class="card s2 fade" style="--i:3"><div class="num">{best['val']:.2f}</div><div class="lab">Best validation loss (started at {big_hist[0]['val']:.2f})</div></div>
<div class="card s2 fade" style="--i:4"><div class="num">{mins}</div><div class="lab">Training time to best model, on a free T4 GPU</div></div>
<div class="card s3 fade" style="--i:5"><div class="kick">What the loss means</div>
<div class="num">{perplexity(big_hist[0]['val']):.0f} → {perplexity(best['val']):.1f}</div>
<div class="lab">Characters the model is effectively choosing between</div>
<p>At the start the model guesses among all {VOCAB} characters. After training it is torn between about <b>{perplexity(best['val']):.0f}</b>, which is how it learned spelling, punctuation and play layout.</p></div>
<div class="card s3 fade" style="--i:6"><div class="kick">Honest evaluation</div>
<div class="num">Overfits</div><div class="lab">after step {best['step']:,}</div>
<p>Training loss kept falling while validation loss started rising, so the saved model is the <b>best checkpoint</b>, not the last one. See the Training tab.</p></div>
</div>
""")
    H("""
<div class="sec">Explore</div>
<div class="explore" style="grid-template-columns:repeat(4,1fr)">
<div class="card"><h4>Training</h4><p>Loss curves and the overfitting point.</p></div>
<div class="card"><h4>Progress</h4><p>Four models, one dataset, and what each change bought.</p></div>
<div class="card"><h4>Generate</h4><p>Type a prompt and watch the model write.</p></div>
<div class="card"><h4>Architecture</h4><p>Every layer, and where the parameters live.</p></div>
</div>
""")

# ========================================================================================
# Training
# ========================================================================================
with tab_train:
    H('<div class="sec">Training run</div><div class="sub">Loss is how surprised the model is by the real next character. Lower is better. '
      'Train loss is measured on text it learns from; validation loss on text it has never seen.</div>')
    zoom = st.radio("View", ["Full run", "Zoom in (from step 1,000)"], horizontal=True, label_visibility="collapsed")
    hist = [r for r in big_hist if r["step"] >= 1000] if zoom.startswith("Zoom") else big_hist

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r["step"] for r in hist], y=[r["train"] for r in hist], name="Train loss", mode="lines+markers",
                             line=dict(color=VIOLET, width=2.5), marker=dict(size=6),
                             hovertemplate="step %{x}<br>train %{y:.4f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[r["step"] for r in hist], y=[r["val"] for r in hist], name="Validation loss", mode="lines+markers",
                             line=dict(color=BLUE, width=3), marker=dict(size=7),
                             hovertemplate="step %{x}<br>val %{y:.4f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[best["step"]], y=[best["val"]], name="Best model", mode="markers",
                             marker=dict(size=15, color=GREEN, symbol="star", line=dict(color="#000", width=1)),
                             hovertemplate=f"best model<br>step {best['step']}<br>val {best['val']:.4f}<extra></extra>"))
    if overfit:
        fig.add_vrect(x0=best["step"], x1=last["step"], fillcolor=RED, opacity=0.07, line_width=0,
                      annotation_text="overfitting", annotation_position="top left", annotation_font=dict(color="#ffa3b1", size=12))
    fig.update_xaxes(title="Training step")
    fig.update_yaxes(title="Loss")
    style_fig(fig, 430)
    show(fig)

    gap_best = best["val"] - best["train"]
    gap_end = last["val"] - last["train"]
    H(f"""
<div class="kpis">
<div class="card kpi"><div class="num">{best['val']:.4f}</div><div class="lab">Best validation loss</div><div class="pt">at step {best['step']:,}</div></div>
<div class="card kpi"><div class="num">{last['train']:.2f}</div><div class="lab">Final train loss</div><div class="pt">at step {last['step']:,}</div></div>
<div class="card kpi"><div class="num">{last['val']:.2f}</div><div class="lab">Final validation loss</div><div class="pt">{'higher than its best' if overfit else 'still improving'}</div></div>
<div class="card kpi"><div class="num">{gap_end:.2f}</div><div class="lab">Train/validation gap at the end</div><div class="pt">was {gap_best:.2f} at the best step</div></div>
</div>
""")
    if overfit:
        H(f"""
<div class="card s6"><div class="kick">What happened</div>
<p style="margin-top:.2rem">After step <b>{best['step']:,}</b>, train loss kept falling ({at_best_train:.2f} → {last['train']:.2f}) while validation loss went the other way
({best['val']:.2f} → {last['val']:.2f}). The model started <b>memorising</b> the training text instead of learning patterns that carry over to new text. Dropout ({DROPOUT}) slows this down but does not stop it.
The training script therefore saves a checkpoint whenever validation loss improves, and the model used on the Generate tab is that best checkpoint.</p></div>
""")
    H(f"""
<div class="sec" style="font-size:1.25rem;margin-top:1.4rem">Training settings</div>
<div class="bento">
<div class="card s2"><div class="kick">Optimiser</div><div class="num" style="font-size:1.4rem">AdamW</div><div class="lab">learning rate {LR}</div></div>
<div class="card s2"><div class="kick">Batch</div><div class="num" style="font-size:1.4rem">{BATCH} × {BLOCK}</div><div class="lab">{BATCH*BLOCK:,} characters per step</div></div>
<div class="card s2"><div class="kick">Data</div><div class="num" style="font-size:1.4rem">1.1M chars</div><div class="lab">Tiny Shakespeare · 90% train, 10% validation</div></div>
</div>
""")

# ========================================================================================
# Progress
# ========================================================================================
with tab_prog:
    H('<div class="sec">Four models, one dataset</div><div class="sub">Each model was built to fix a weakness of the previous one. '
      'Same text, same validation set, same loss.</div>')

    base = runs[0][4]
    worst = max(r[4] for r in runs)
    bars = "".join(
        f'<div>{esc(r[0])}<span class="t"><i style="--w:{r[4]/worst*100:.0f}%;background:linear-gradient(90deg,#3b82f6,#8b5cf6)"></i></span><code>{r[4]:.2f}</code></div>'
        for r in runs)
    H(f"""
<div class="card s6" style="margin-bottom:14px"><div class="kick">Best validation loss (lower is better)</div>
<div class="cmp" style="margin-top:.4rem"><style>.cmp div{{grid-template-columns:170px 1fr 56px}}</style>{bars}</div></div>
""")

    fig = go.Figure()
    series = [("Bigram", BIGRAM["steps"], BIGRAM["val"], AMBER)]
    if v1_hist:
        series.append(("One attention head", [r["step"] for r in v1_hist], [r["val"] for r in v1_hist], PINK))
    if small_hist:
        series.append(("Small GPT", [r["step"] for r in small_hist], [r["val"] for r in small_hist], VIOLET))
    series.append(("Big GPT", [r["step"] for r in big_hist], [r["val"] for r in big_hist], BLUE))
    for name, xs, ys, col in series:
        fig.add_trace(go.Scatter(x=xs, y=ys, name=name, mode="lines", line=dict(color=col, width=3),
                                 hovertemplate=name + "<br>step %{x}<br>val %{y:.3f}<extra></extra>"))
    fig.update_xaxes(title="Training step")
    fig.update_yaxes(title="Validation loss", range=[1.3, 3.0])
    style_fig(fig, 400)
    show(fig)

    body = ""
    for name, ctx, shape, params, val, note in runs:
        body += (f"<tr><td>{esc(name)}</td><td>{esc(ctx)}</td><td>{esc(shape)}</td><td class='n'>{params:,}</td>"
                 f"<td class='n'>{val:.3f}</td><td class='n'>≈ {perplexity(val):.1f}</td></tr>")
    H(f"""
<table class="tbl"><thead><tr><th>Model</th><th>Context</th><th>Shape</th><th class="n">Parameters</th><th class="n">Val loss</th><th class="n">Choices per char</th></tr></thead>
<tbody>{body}</tbody></table>
""")

    big_text = (read_text("logs/big_best_sample.txt") or read_text("logs/big_sample.txt") or BIG_FALLBACK).strip()

    def sample_card(stage, note, text):
        return (f'<div class="card"><div class="stage">{esc(stage)}<em>{esc(note)}</em></div>'
                f'<div class="sample">{esc(text.strip()[:380]).replace(chr(10), "<br>")}</div></div>')

    H('<div class="sec" style="font-size:1.25rem;margin-top:1.2rem">What each model writes</div>'
      '<div class="sub">Every sample starts from nothing. Same data, bigger brain.</div>')
    H('<div class="grid2">'
      + sample_card("Bigram", f"val {runs[0][4]:.2f}", SAMPLES["bigram"])
      + sample_card("One head", f"val {runs[1][4]:.2f}", SAMPLES["v1"])
      + sample_card("Small GPT", f"val {runs[2][4]:.2f}", SAMPLES["small"])
      + sample_card("Big GPT", f"val {runs[3][4]:.2f}", big_text)
      + "</div>")

# ========================================================================================
# Generate
# ========================================================================================
with tab_gen:
    H('<div class="sec">Make it write</div><div class="sub">Type the start of a line and the model continues it, one character at a time. '
      'It writes in the style of Shakespeare but has no understanding of meaning, so expect convincing words and nonsense sentences.</div>')

    CKPT = next((p for p in ["checkpoints/big_best.pt", "checkpoints/big.pt"] if (ROOT / p).exists()), None)

    if CKPT is None:
        st.info("The trained model file is not in this project yet. Copy `checkpoints/big_best.pt` from Colab into the `checkpoints` folder.")
    else:
        @st.cache_resource(show_spinner="Loading the model...")
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

        c1, c2 = st.columns([3, 2])
        with c1:
            prompt = st.text_area("Prompt", value="ROMEO:\n", height=110)
        with c2:
            n_new = st.slider("Characters to write", 50, 500, 250, step=50)
            temp = st.slider("Temperature (higher = wilder)", 0.3, 1.5, 0.8, step=0.1)
        go_btn = st.button("Generate")

        if go_btn:
            ids = [stoi[c] for c in prompt if c in stoi] or [stoi["\n"]]
            dropped = len(prompt) - len([c for c in prompt if c in stoi])
            if dropped:
                st.caption(f"Ignored {dropped} character(s) the model has never seen (it only knows the {len(stoi)} characters in Shakespeare).")
            shown = "".join(itos[i] for i in ids)
            box = st.empty()
            out = ""
            for k, ch in enumerate(stream(ids, n_new, temp, seed=int(__import__("time").time()) % 100000)):
                out += ch
                if k % 3 == 0 or k == n_new - 1:
                    box.markdown('<div class="gen"><span class="p">' + esc(shown).replace("\n", "<br>") + "</span>"
                                 + esc(out).replace("\n", "<br>") + '<span class="c"></span></div>', unsafe_allow_html=True)
            box.markdown('<div class="gen"><span class="p">' + esc(shown).replace("\n", "<br>") + "</span>"
                         + esc(out).replace("\n", "<br>") + "</div>", unsafe_allow_html=True)
        else:
            H('<div class="gen" style="color:var(--dim)">Press Generate. The prompt appears in blue and the model\'s writing follows in white.</div>')

# ========================================================================================
# Architecture
# ========================================================================================
with tab_arch:
    hs = N_EMBD // N_HEAD
    H(f'<div class="sec">Architecture</div><div class="sub">A decoder-only transformer, the same design as GPT. '
      f'Text goes in at the top and the probabilities for the next character come out at the bottom.</div>')
    H(f"""
<div class="arch">
<div class="node">Input characters<small>up to {BLOCK} characters of context · vocabulary of {VOCAB}</small></div><div class="dn">↓</div>
<div class="node hl">Token embedding + position embedding<small>each character becomes {N_EMBD} numbers</small></div><div class="dn">↓</div>
<div class="blk"><span class="x">× {N_LAYER} blocks</span>
<div class="node">LayerNorm</div>
<div class="node hl">Masked multi-head self-attention<small>{N_HEAD} heads × {hs} dimensions · each character looks only backwards</small></div>
<div class="node add">+ residual connection</div>
<div class="node">LayerNorm</div>
<div class="node hl">Feed-forward network<small>{N_EMBD} → {4*N_EMBD} → {N_EMBD} with GELU</small></div>
<div class="node add">+ residual connection</div>
</div><div class="dn">↓</div>
<div class="node">Final LayerNorm</div><div class="dn">↓</div>
<div class="node hl">Linear layer + softmax<small>{N_EMBD} → {VOCAB} probabilities for the next character</small></div>
</div>
""")

    parts_html = "".join(
        f'<div>{esc(k)}<span class="t"><i style="--w:{v/N_PARAMS*100:.1f}%;background:linear-gradient(90deg,#3b82f6,#8b5cf6)"></i></span><code>{v/1e6:.2f}M</code></div>'
        for k, v in PARTS.items())
    H(f"""
<div class="card s6" style="margin-top:1rem"><div class="kick">Where the {N_PARAMS:,} parameters live</div>
<div class="cmp"><style>.cmp div{{grid-template-columns:190px 1fr 64px}}</style>{parts_html}</div>
<p>Almost everything sits in the transformer blocks. Each block holds the attention layers ({4*N_EMBD*N_EMBD/1e6:.2f}M) and the feed-forward network ({8*N_EMBD*N_EMBD/1e6:.2f}M).</p></div>
""")
    H("""
<div class="sec" style="font-size:1.25rem;margin-top:1.4rem">Design choices and limits</div>
<div class="grid3">
<div class="card"><div class="kick">Character level</div><p>The tokenizer is one number per character (65 in total). It is simple and needs no vocabulary file, but the model must learn spelling before it can learn anything else.</p></div>
<div class="card"><div class="kick">Causal mask</div><p>Each position can only attend to earlier positions, so training matches how the model is used when it writes one character at a time.</p></div>
<div class="card"><div class="kick">Limits</div><p>The data is only 1.1M characters, so the model overfits quickly. It learns the look of Shakespeare, not meaning.</p></div>
</div>
""")

H(f"""
<div class="foot">Built by Anoushka Yadav · <a href="{GITHUB}" target="_blank" rel="noopener">github.com/anuu-yd9/mini-gpt</a><br>
Trained on the Tiny Shakespeare text (public domain). Not affiliated with OpenAI.</div>
""")
