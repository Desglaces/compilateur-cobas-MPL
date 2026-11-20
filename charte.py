"""Charte graphique Roche de l'outil : bandeau fixe en haut (logo, nom de l'outil, version, étapes
numérotées, langue, mode sombre), couleurs, cartes et zones de dépôt, en mode clair et sombre.

Le thème de base (couleur principale, rayons, boutons en pastille) est dans .streamlit/config.toml ;
ce module ajoute le bandeau et quelques styles.

Mode sombre : toute la page est inversée par un filtre CSS (invert + hue-rotate 180°), ce qui couvre aussi les
champs, listes et tableaux sans dépendre de la structure interne de Streamlit. Les couleurs propres à l'outil
sont pré-calculées pour que le résultat affiché soit exactement la palette sombre voulue ; les images
(logo compris) reçoivent le même filtre pour retrouver leurs couleurs.

Le logo Roche n'est PAS dans le dépôt (public). Il est cherché, dans cet ordre :
  1. les secrets Streamlit : clé `roche_logo_b64` (PNG encodé en base64) ;
  2. la variable d'environnement ROCHE_LOGO_B64 ;
  3. un fichier local `assets/roche_logo.png` ou `roche_logo.png` (ignorés par git, voir .gitignore).
Sans logo, le bandeau reste identique, simplement sans logo. Le PNG (fond blanc) est détouré au chargement :
couleur d'origine en mode clair, blanc en mode sombre.
"""
import base64
import html as _html
import io
import os
import re
from pathlib import Path
from string import Template

import numpy as np
import streamlit as st
from PIL import Image

from i18n import LANGUES, t as tr

ICI = Path(__file__).parent
FICHIERS_LOGO = (ICI / "assets" / "roche_logo.png", ICI / "roche_logo.png")

# ----------------------------------------------------------------------------- palettes (couleurs affichées)
CLAIR = dict(
    bg="#FAFAFC", panel="#FFFFFF", panel2="#F4F6FB", border="#E1E6F0", dash="#B9C4DC",
    text="#16213A", muted="#5B6478", head="#0B1F52", primary="#0B41CD", soft="#E8EEFC", badge="#8C97B2",
    on="#FFFFFF", shadow="rgba(8,27,77,.08)",
    hdr="linear-gradient(90deg,#FFFFFF 0%,#F3F7FF 42%,#E2F6E9 100%)",
)
SOMBRE = dict(
    bg="#0D1324", panel="#121A2C", panel2="#182138", border="#26314D", dash="#3A4A78",
    text="#E6EAF5", muted="#9AA6C4", head="#BCC7FF", primary="#3E63F0", soft="#1B2646", badge="#4A5878",
    on="#FFFFFF", shadow="rgba(255,255,255,.35)",   # une ombre noire devient blanche une fois inversée : on l'écrit déjà inversée
    hdr="linear-gradient(90deg,#121A2C 0%,#10172E 55%,#1A2150 100%)",
)

# Filtre du mode sombre = invert(1) puis hue-rotate(180deg) ; M est la matrice de la rotation de teinte à 180°.
FILTRE_SOMBRE = "invert(1) hue-rotate(180deg)"
_M180 = np.array([[-0.574, 1.430, 0.144], [0.426, 0.430, 0.144], [0.426, 1.430, -0.856]])


def _avant_filtre(hexa):
    """Couleur à écrire dans la feuille de style pour obtenir `hexa` APRÈS le filtre sombre : on résout M·(1 - x) = cible."""
    cible = np.array([int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    x = 1 - np.linalg.solve(_M180, cible)
    return "#%02X%02X%02X" % tuple(int(round(min(max(v, 0.0), 1.0) * 255)) for v in x)


def _palette(dark):
    if not dark:
        return dict(CLAIR)
    return {k: (re.sub(r"#[0-9A-Fa-f]{6}", lambda m: _avant_filtre(m.group(0)), v) if k != "shadow" else v)
            for k, v in SOMBRE.items()}


# ----------------------------------------------------------------------------- feuille de style
CSS = Template(r"""
:root{--rc-bg:$bg;--rc-panel:$panel;--rc-panel2:$panel2;--rc-border:$border;--rc-dash:$dash;--rc-text:$text;--rc-muted:$muted;--rc-head:$head;--rc-primary:$primary;--rc-soft:$soft;--rc-badge:$badge;--rc-on:$on;--rc-shadow:$shadow;--rc-hdr:$hdr;--rc-font:"Roche Sans","Segoe UI",system-ui,-apple-system,Arial,sans-serif}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],#MainMenu,footer{display:none!important}
.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--rc-bg)!important}
[data-testid="stMainBlockContainer"],.block-container{padding-top:5.6rem!important;padding-bottom:2.5rem!important}
.stApp h1,.stApp h2,.stApp h3,.stApp h4{color:var(--rc-head)!important;scroll-margin-top:92px}
hr{border-color:var(--rc-border)!important}
/* Liste des fichiers masquée pour la case 1 seulement (les noms des CSV restent visibles) */
.st-key-depot_fichiers [data-testid="stFileUploaderFileList"],.st-key-depot_fichiers [data-testid="stFileChip"]{display:none}
/* bouton principal aux couleurs de la charte (identique à la pastille de version du bandeau) */
[data-testid="stBaseButton-primary"]{background:var(--rc-primary)!important;border-color:var(--rc-primary)!important;color:var(--rc-on)!important}
/* cartes et zones de dépôt */
[data-testid="stFileUploaderDropzone"]{background:var(--rc-panel2)!important;border:2px dashed var(--rc-dash)!important;border-radius:14px!important}
[data-testid="stFileUploaderDropzone"]:hover{border-color:var(--rc-primary)!important}
[data-testid="stExpander"] details{background:var(--rc-panel)!important;border:1px solid var(--rc-border)!important;border-radius:14px!important}
[data-testid="stExpander"] summary{font-weight:600;background:transparent!important}
[data-testid="stMetric"]{background:var(--rc-panel);border:1px solid var(--rc-border);border-radius:14px;padding:.8rem 1rem}
[data-testid="stMetricValue"]{color:var(--rc-head)!important}
[data-testid="stDataFrame"]{border:1px solid var(--rc-border);border-radius:12px;overflow:hidden}
/* bandeau fixe */
.st-key-rc_header{position:fixed!important;top:0;left:0;right:0;width:100%!important;height:64px;z-index:999990;box-sizing:border-box;padding:0 20px;display:flex!important;align-items:center;background:var(--rc-hdr);border-bottom:1px solid var(--rc-border);box-shadow:0 2px 14px var(--rc-shadow)}
.st-key-rc_header>div{width:100%;gap:0!important}
.rc-bar{display:flex;align-items:center;gap:14px;min-width:0;font-family:var(--rc-font)}
.rc-logo{height:34px;width:auto;display:block;flex:0 0 auto}
.rc-app{font-weight:650;font-size:1.14rem;white-space:nowrap;color:var(--rc-head)!important}
.rc-ver{background:var(--rc-primary);color:var(--rc-on)!important;border-radius:999px;font-size:.72rem;font-weight:700;padding:3px 10px;letter-spacing:.02em}
.rc-steps{display:flex;align-items:center;gap:4px;margin-left:12px}
.rc-step{display:flex;align-items:center;gap:8px;padding:4px 14px 4px 4px;border-radius:999px;text-decoration:none!important;color:var(--rc-muted)!important}
a.rc-step:hover{background:var(--rc-soft)}
.rc-ic{position:relative;width:40px;height:40px;border-radius:50%;display:grid;place-items:center;background:var(--rc-soft);color:var(--rc-primary)!important;opacity:.55}
.rc-ic::before{content:"";width:22px;height:22px;background:currentColor;-webkit-mask:var(--ico) center/contain no-repeat;mask:var(--ico) center/contain no-repeat}
.rc-ic.i1{--ico:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 16V5m0 0L8 9m4-4 4 4M5 15v3a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-3'/%3E%3C/svg%3E")}
.rc-ic.i2{--ico:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M7 8h11m0 0-3-3m3 3-3 3M17 16H6m0 0 3-3m-3 3 3 3'/%3E%3C/svg%3E")}
.rc-ic.i3{--ico:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='4' y='5' width='16' height='14' rx='2'/%3E%3Cpath d='M4 10h16M10 10v9'/%3E%3C/svg%3E")}
.rc-n{position:absolute;right:-3px;bottom:-3px;width:18px;height:18px;border-radius:50%;display:grid;place-items:center;font:700 .62rem/1 var(--rc-font);font-style:normal;color:var(--rc-on)!important;background:var(--rc-badge);border:2px solid var(--rc-panel)}
.rc-lbl{font-size:.88rem;font-weight:600;color:var(--rc-muted)!important}
.rc-step.done .rc-ic{opacity:1}
.rc-step.done .rc-n{background:var(--rc-primary)}
.rc-step.done .rc-lbl{color:var(--rc-text)!important}
.rc-step.active .rc-ic{opacity:1;background:var(--rc-panel);box-shadow:0 0 0 2px var(--rc-primary)}
.rc-step.active .rc-n{background:var(--rc-primary)}
.rc-step.active .rc-lbl{color:var(--rc-head)!important}
/* langue + mode sombre dans le bandeau */
.st-key-lang{position:fixed!important;top:12px;right:68px;width:96px!important;z-index:999995}
.st-key-btn_dark{position:fixed!important;top:12px;right:20px;z-index:999995}
.st-key-btn_dark button{width:40px;height:40px;min-height:40px!important;padding:0!important;border-radius:50%!important;background:transparent!important;border:0!important;color:var(--rc-text)!important}
.st-key-btn_dark button:hover{background:var(--rc-soft)!important;color:var(--rc-primary)!important}
@media (max-width:1180px){.rc-lbl{display:none}.rc-step{padding-right:4px}}
@media (max-width:820px){.rc-app{font-size:1rem}.rc-ver,.rc-steps{display:none}}
/* pied de page */
.rc-foot{text-align:center;color:var(--rc-muted)!important;font-size:.78rem;padding:1.4rem 0 .2rem}
""")

# Mode sombre : filtre sur la page entière, et le même filtre sur les images pour qu'elles gardent leurs couleurs.
CSS_SOMBRE = f"""
html{{filter:{FILTRE_SOMBRE}}}
img,video,.rc-logo{{filter:{FILTRE_SOMBRE}}}
"""


def css(dark):
    return CSS.safe_substitute(_palette(dark)) + (CSS_SOMBRE if dark else "")


# ----------------------------------------------------------------------------- logo
def _logo_octets():
    try:
        b64 = st.secrets.get("roche_logo_b64")
        if b64:
            return base64.b64decode(b64)
    except Exception:
        pass  # pas de fichier de secrets : normal en local
    b64 = os.environ.get("ROCHE_LOGO_B64")
    if b64:
        try:
            return base64.b64decode(b64)
        except Exception:
            pass
    for f in FICHIERS_LOGO:
        if f.exists():
            return f.read_bytes()
    return None


@st.cache_resource(show_spinner=False)
def _logo_uri(blanc):
    """Logo en data-URI PNG transparent : couleur d'origine, ou tout blanc (mode sombre). None si absent."""
    brut = _logo_octets()
    if not brut:
        return None
    try:
        a = np.asarray(Image.open(io.BytesIO(brut)).convert("RGBA"), dtype=np.float32)
        if a[..., 3].min() < 250:                      # déjà transparent : on garde la forme telle quelle
            rgb, alpha = a[..., :3], a[..., 3] / 255.0
        else:                                          # fond blanc -> transparent, trait = couleur de l'encre
            rgb3 = a[..., :3]
            lum = rgb3.mean(axis=2)
            encre = rgb3[np.unravel_index(lum.argmin(), lum.shape)]
            c = int(np.argmin(encre))                  # canal qui contraste le plus avec le blanc
            alpha = np.clip((255.0 - rgb3[..., c]) / max(255.0 - float(encre[c]), 1.0), 0, 1)
            rgb = np.broadcast_to(encre, rgb3.shape)
        if blanc:
            rgb = np.full(rgb.shape, 255.0, dtype=np.float32)
        img = Image.fromarray(np.dstack([rgb, alpha * 255.0]).clip(0, 255).astype(np.uint8), "RGBA")
        cadre = Image.fromarray((alpha > 0.04).astype(np.uint8) * 255).getbbox()
        if cadre:
            img = img.crop(cadre)
        tampon = io.BytesIO()
        img.save(tampon, "PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(tampon.getvalue()).decode()
    except Exception:
        return None


# ----------------------------------------------------------------------------- bandeau
def _etapes_html(etape):
    """Les 3 étapes de l'outil : faite (✓), en cours, à venir. Les étapes atteintes sont des liens vers leur section."""
    pieces = []
    for n in (1, 2, 3):
        etat = "done" if n < etape else "active" if n == etape else "todo"
        balise = "a" if etat != "todo" else "span"
        lien = f' href="#etape-{n}"' if balise == "a" else ""
        titre = _html.escape(tr(f"step{n}"), quote=True)
        pastille = "✓" if etat == "done" else str(n)
        pieces.append(
            f'<{balise} class="rc-step {etat}"{lien} title="{titre}">'
            f'<span class="rc-ic i{n}"><i class="rc-n">{pastille}</i></span>'
            f'<span class="rc-lbl">{_html.escape(tr(f"step{n}_short"))}</span></{balise}>')
    return f'<nav class="rc-steps" aria-label="{_html.escape(tr("steps_aria"), quote=True)}">' + "".join(pieces) + "</nav>"


def entete_html(version, etape, dark):
    logo = _logo_uri(bool(dark))
    img = f'<img class="rc-logo" src="{logo}" alt="Roche">' if logo else ""
    return (f'<div class="rc-bar">{img}'
            f'<div class="rc-app" role="heading" aria-level="1">{_html.escape(tr("app_name"))}</div>'
            f'<span class="rc-ver">{_html.escape(version)}</span>{_etapes_html(etape)}</div>')


def _basculer_sombre():
    st.session_state["dark_mode"] = not st.session_state.get("dark_mode", False)


def appliquer_charte(version):
    """Injecte la feuille de style et affiche le bandeau (langue et mode sombre inclus). Renvoie True si mode sombre.
    Réglages initiaux possibles par l'adresse : ?lang=en  /  ?theme=dark"""
    qp = st.query_params
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = qp.get("theme") == "dark"
    if "lang" not in st.session_state and qp.get("lang") in LANGUES:
        st.session_state["lang"] = qp.get("lang")
    dark = bool(st.session_state["dark_mode"])
    with st.container(key="rc_header"):
        st.html(f"<style>{css(dark)}</style>")
        st.html(entete_html(version, st.session_state.get("etape", 1), dark))
        st.selectbox(tr("lang"), list(LANGUES), format_func=str.upper, key="lang", label_visibility="collapsed", width=96)
        st.button(" ", key="btn_dark", icon=":material/light_mode:" if dark else ":material/dark_mode:",
                  type="tertiary", help=tr("dark_tip"), on_click=_basculer_sombre)
    return dark


def pied_de_page(version):
    st.html(f'<div class="rc-foot">{_html.escape(tr("app_name"))} · {_html.escape(version)} — '
            f'{_html.escape(tr("foot"))}</div>')
