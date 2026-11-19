"""Procès-verbal d'installation (optionnel).

Reproduit le PV « Administration Commerciale V 2.0 » (onglet « Formulaire » du classeur
PVInstall_..._gsheet) et génère le PDF, prêt à être signé (DocuSign...).

Pré-remplissage à partir de la fiche SIDIV (si elle est renseignée) :
  - « Représenté par » = nom du référent du LBM ;
  - intervenant Roche (case grise du haut) = nom de l'intervenant S.I ;
  - gamme « IT », produit « Licence MPL cnxROCHE » (la référence se complète seule) ;
  - date d'installation / connexion = date d'utilisation de l'outil.
Le logo Roche n'est pas dans le dépôt : il est lu dans les secrets Streamlit (voir logo_octets).

Module indépendant du compilateur : il n'est appelé que depuis une section repliée en bas de page.
"""
import base64
import datetime
import io
from pathlib import Path

import pandas as pd
import streamlit as st
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

LOGO = Path(__file__).with_name("roche_logo.png")  # option locale (ignoré par git, jamais publié)
P = "pv_"  # préfixe des clés de session
BLEU = HexColor("#2F6FBE")
GRIS = HexColor("#D9D9D9")
GRIS_TXT = HexColor("#595959")

# Catalogue « gamme IT » (désignation -> référence), extrait de l'onglet « produits » du classeur.
CATALOGUE_IT = {
    "SET CD-ROM C-TAQ UTIL CHANNEL ANALYSIS": "03376958190",
    "Ecran TFT 17": "04415566001",
    "Clavier  Tabulateur à formule": "04416384001",
    "cobas Link2": "07269234001",
    "Fortigate 50 E": "08153299001",
    "c8000 data manager server G9": "08680523001",
    "X800 Data Manager PC": "09275819001",
    "Prise en charge devis connexion SIL": "04496124001",
    "Carte MATROX TRIPLE pour MPL360": "05188555001",
    "Pied 3 écrans ERGOTRON": "05188571001",
    "Licence MPL servMAJevo2": "05472628001",
    "Licence MPL appCOLIS [Pack 5 coursiers]": "07100191001",
    "Licence MPL appCOLIS [Pack 10 coursiers]": "07100205001",
    "Licence MPL appCOLIS [Pack 25 coursiers]": "07100264001",
    "Licence MPL appCOLIS [Pack 50 coursiers]": "07100299001",
    "Imprimante CB Intermec PM43i": "07422563001",
    "Douchette Zebra DS 9308": "07497814001",
    "Scanner code à barre MOTOROLA DS9208": "07497814001",
    "Licence MPL servMULTI": "07927924001",
    "Licence MPL appCORELAB": "07927932001",
    "Licence MPL appSATELLITE": "07927959001",
    "Licence MPL cnxROCHE": "07928335001",
    "Licence MPL cnx1PARAM": "07928343001",
    "Licence MPL cnxMONO-INSTR": "07928360001",
    "Licence MPL cnxMULTI-INSTR": "07928378001",
    "Licence MPL cnxSIL": "07928394001",
    "Serveur Proliant MPL 150 GEN9 (Tour)": "07940092001",
    "Serveur HP DL180 GEN9 RACK": "07940106001",
    "NAS Synology DS216 2 X 2To": "07950748001",
    "Screen HP ProDisplay P223 LED 21.5": "08499098001",
    "NPORT 5110A MOXA pour MPL": "08675902001",
    "MPL PRINTER HONEYWELL INTERMEC PC23d": "08688834001",
    "PC LENOVO M910q": "08717753001",
    "Licence MPL cnxMULTI-PTA": "08771138001",
    "MPL Server Virtual FTP Download center": "09004602001",
    "MWF virtual cobas 8100 Server License": "09096884001",
}
GAMME_DEFAUT = "IT"
PRODUIT_DEFAUT = "Licence MPL cnxROCHE"  # -> 07928335001

COL_GAMME, COL_PROD, COL_REF = "Gamme", "Produit Roche", "Référence"
COL_SERIE, COL_INSTALL, COL_MES = "N° de série", "Date d'installation / connexion", "Date de mise en service ou routine"
COL_AUTO = "Connexion IT : nom et N/S de l'automate connecté"
COLONNES = [COL_GAMME, COL_PROD, COL_REF, COL_SERIE, COL_INSTALL, COL_MES, COL_AUTO]
MAX_LIGNES = 20


def logo_octets():
    """Logo Roche (PNG) : lu dans les secrets Streamlit (clé `roche_logo_b64`, PNG encodé en base64),
    pour ne pas publier le logo dans le dépôt. À défaut, fichier local `roche_logo.png` s'il existe ;
    sinon le PV est généré sans logo."""
    try:
        b64 = st.secrets.get("roche_logo_b64")
        if b64:
            return base64.b64decode("".join(str(b64).split()))
    except Exception:
        pass
    try:
        if LOGO.exists():
            return LOGO.read_bytes()
    except Exception:
        pass
    return None


def aujourdhui():
    return datetime.date.today().strftime("%d/%m/%Y")


def reference(produit):
    """Référence du produit dans le catalogue (vide si inconnu)."""
    return CATALOGUE_IT.get(str(produit or "").strip(), "")


# ---------------------------------------------------------------------------
# Génération du PDF
# ---------------------------------------------------------------------------
def _ajuster(c, texte, police, taille, largeur, mini=5.0):
    """Réduit la taille de police pour que le texte tienne dans la largeur donnée."""
    while taille > mini and stringWidth(texte, police, taille) > largeur:
        taille -= 0.25
    return taille


def _lignes(texte, police, taille, largeur):
    """Découpe un texte en lignes qui tiennent dans la largeur (retours à la ligne respectés)."""
    sortie = []
    for para in str(texte or "").splitlines() or [""]:
        courant = ""
        for mot in para.split(" "):
            essai = (courant + " " + mot).strip()
            if courant and stringWidth(essai, police, taille) > largeur:
                sortie.append(courant)
                courant = mot
            else:
                courant = essai
        sortie.append(courant)
    return sortie


def generer_pdf(d):
    """d : dictionnaire des champs du PV (voir _collecter). Retourne le PDF en octets."""
    W, H = A4
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle("Procès-verbal d'installation")
    X0, X1 = 40, W - 40
    y = lambda top: H - top  # coordonnées « depuis le haut »

    def texte(x, top, s, police="Helvetica", taille=8, couleur=black, largeur=None, align="l"):
        s = str(s or "")
        if largeur:
            taille = _ajuster(c, s, police, taille, largeur)
        c.setFont(police, taille)
        c.setFillColor(couleur)
        {"l": c.drawString, "c": c.drawCentredString, "r": c.drawRightString}[align](x, y(top), s)

    def case(x, top, w, h, s="", grise=False, taille=8, align="l"):
        c.setStrokeColor(HexColor("#6FA8DC") if not grise else HexColor("#BFBFBF"))
        c.setLineWidth(0.8)
        if grise:
            c.setFillColor(GRIS)
            c.rect(x, y(top + h), w, h, stroke=1, fill=1)
        else:
            c.setFillColor(white)
            c.rect(x, y(top + h), w, h, stroke=1, fill=1)
        if s:
            px = x + 4 if align == "l" else x + w / 2
            texte(px, top + h / 2 + taille * 0.35, s, taille=taille, largeur=w - 8, align=align)

    # --- En-tête
    texte(X0, 62, "PROCES-VERBAL D'INSTALLATION", "Helvetica-Bold", 16, BLEU)
    logo = logo_octets()
    if logo:
        try:
            c.drawImage(ImageReader(io.BytesIO(logo)), X1 - 46, y(78), width=46, height=24.5, mask="auto")
        except Exception:
            pass  # logo illisible : PV sans logo
    case(X0 + 105, 92, 190, 17, d["roche_nom"])
    texte(X0 + 305, 103, "Fonction :", taille=7.5, couleur=GRIS_TXT)
    case(X0 + 355, 92, X1 - (X0 + 355), 17, d["roche_fonction"])

    # --- Client
    texte(X0, 135, "Le Client :", "Helvetica-BoldOblique", 8)
    texte(X1, 135, "Type : " + d["type"], taille=7.5, couleur=GRIS_TXT, align="r")
    texte(X0, 152, d["client_nom"], "Helvetica-Bold", 8.5, BLEU, largeur=X1 - X0)
    texte(X0, 180, "Représenté par :", taille=7.5, couleur=GRIS_TXT)
    texte(X0 + 105, 180, d["rep_nom"], taille=8, largeur=190)
    c.setStrokeColor(HexColor("#6FA8DC")); c.setLineWidth(0.8)
    c.line(X0 + 105, y(184), X0 + 295, y(184))
    texte(X0 + 305, 180, "Fonction :", taille=7.5, couleur=GRIS_TXT)
    case(X0 + 355, 168, X1 - (X0 + 355), 17, d["rep_fonction"])
    texte(X0, 208, "N° Client :", taille=7.5, couleur=GRIS_TXT)
    texte(X0 + 105, 208, d["client_num"], taille=8, largeur=190)
    texte(X0, 232, "Adresse :", taille=7.5, couleur=GRIS_TXT)
    texte(X0 + 105, 232, d["adresse"], taille=8, largeur=X1 - X0 - 105)
    texte(X0 + 105, 250, d["cp"], taille=8, largeur=190)
    texte(X0, 268, "Ville :", taille=7.5, couleur=GRIS_TXT)
    texte(X0 + 105, 268, d["ville"], taille=8, largeur=190)
    if d["type"] == "Privé":
        libelle, lib2 = "Inscrite au Registre du commerce et des sociétés de", "Sous le numéro"
        case(X0 + 150, 283, 145, 17, grise=True)
        valeur = d["siren"]
    else:
        libelle = "Identifié sous le n° SIREN ou n° FINESS ou autre n° d'identification"
        lib2, valeur = "Service de", d["service"]
        case(X0 + 150, 283, 145, 17, d["siren"])
    texte(X0, 294, libelle, taille=6.2, couleur=GRIS_TXT, largeur=148)
    texte(X0 + 298, 294, lib2, taille=6.8, couleur=GRIS_TXT)
    case(X0 + 355, 283, X1 - (X0 + 355), 17, valeur)

    # --- Système / produits installés
    texte(X0, 328, "Système/Produit Installé", "Helvetica-Bold", 9, BLEU)
    texte(X0, 343, "DESCRIPTION DES SYSTEMES (mis en service par du personnel Roche habilité)",
          "Helvetica-BoldOblique", 7)
    c.setLineWidth(0.4); c.setStrokeColor(black)
    c.line(X0, y(345), X0 + stringWidth("DESCRIPTION DES SYSTEMES (mis en service par du personnel Roche habilité)",
                                        "Helvetica-BoldOblique", 7), y(345))
    largeurs = [30, 125, 68, 50, 70, 70, 102]  # total 515
    largeurs[-1] = (X1 - X0) - sum(largeurs[:-1])
    titres = ["Gamme", "Produit Roche", "Référence", "N°série", "Date d'Installation/ Connexion",
              "Date de Mise en Service ou Routine", "Pour les Connexions IT\nNom et N/S Automate connecté"]
    top = 352
    htete = 28
    xs = [X0]
    for w in largeurs:
        xs.append(xs[-1] + w)
    c.setStrokeColor(black); c.setLineWidth(0.7)
    for i, t in enumerate(titres):
        c.setFillColor(HexColor("#F2F2F2")); c.rect(xs[i], y(top + htete), largeurs[i], htete, stroke=1, fill=1)
        lignes = []
        for part in t.split("\n"):
            lignes += _lignes(part, "Helvetica-Bold", 6.3, largeurs[i] - 6)
        dy = top + htete / 2 - (len(lignes) - 1) * 3.6 + 2.2
        for k, ligne in enumerate(lignes):
            texte(xs[i] + largeurs[i] / 2, dy + k * 7.2, ligne, "Helvetica-Bold", 6.3, GRIS_TXT, align="c")
    top += htete
    lignes_prod = [r for r in d["produits"] if any(str(v or "").strip() for v in r)]
    nb = max(10, min(len(lignes_prod), MAX_LIGNES))
    hlig = 17
    for k in range(nb):
        r = lignes_prod[k] if k < len(lignes_prod) else [""] * 7
        for i in range(7):
            c.setFillColor(white if k < len(lignes_prod) else HexColor("#F7F7F7"))
            c.rect(xs[i], y(top + hlig), largeurs[i], hlig, stroke=1, fill=1)
            val = str(r[i] or "")
            if val:
                texte(xs[i] + (4 if i in (1, 6) else largeurs[i] / 2), top + hlig / 2 + 2.6, val, taille=7,
                      largeur=largeurs[i] - 6, align="l" if i in (1, 6) else "c")
        top += hlig

    # --- Réserves
    top += 10
    hres = 52
    c.setStrokeColor(black); c.setLineWidth(0.7); c.setFillColor(white)
    c.rect(X0, y(top + hres), X1 - X0, hres, stroke=1, fill=1)
    texte(X0 + 4, top + 10, "Réserves si nécessaire :", taille=7.5)
    for k, ligne in enumerate(_lignes(d["reserves"], "Helvetica", 7.5, X1 - X0 - 10)[:4]):
        texte(X0 + 4, top + 22 + k * 9, ligne, taille=7.5)
    top += hres + 9
    if any(str(r[6] or "").strip() for r in lignes_prod):
        texte(X0, top, "Pour les connexions middleware, la signature du Procès-Verbal d'Installation transfère "
                       "la responsabilité de la validation et de la surveillance de la connexion au laboratoire.",
              "Helvetica-Bold", 5.6, largeur=X1 - X0)
    top += 12

    # --- Signatures
    hsig = 82
    lsig = (X1 - X0) * 0.62
    c.setStrokeColor(black); c.rect(X0, y(top + hsig), lsig, hsig, stroke=1, fill=0)
    milieu = X0 + lsig / 2
    texte(X0 + 8, top + 13, "Pour Roche Diagnostics France", "Helvetica-Bold", 7.5, BLEU)
    texte(milieu + 8, top + 13, "Pour le Client", "Helvetica-Bold", 7.5, BLEU)
    texte(X0 + 8, top + 33, d["roche_nom"] or "Nom Prénom", "Helvetica-Bold", 7.5, largeur=lsig / 2 - 14)
    texte(milieu + 8, top + 33, d["rep_nom"] or "Nom Prénom", "Helvetica-Bold", 7.5, largeur=lsig / 2 - 14)
    texte(X0 + 8, top + 50, d["roche_fonction"] or "Fonction", "Helvetica-Bold", 7.5, largeur=lsig / 2 - 14)
    texte(milieu + 8, top + 50, d["rep_fonction"] or "Fonction", "Helvetica-Bold", 7.5, largeur=lsig / 2 - 14)
    texte(X0 + 8, top + 70, "Signature :", taille=7.5)
    texte(milieu + 8, top + 70, "Signature :", taille=7.5)

    # --- Pied de page
    texte(X0, H - 28, "Administration Commerciale-V 2.0", taille=8, couleur=GRIS_TXT)
    texte(X1, H - 28, "01/12/2021", taille=8, couleur=GRIS_TXT, align="r")
    c.showPage()
    c.save()
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Interface Streamlit
# ---------------------------------------------------------------------------
def _suivre(cle, source):
    """Pré-remplit un champ avec la valeur de la SIDIV tant que l'utilisateur ne l'a pas modifié."""
    k = P + cle
    source = str(source or "").strip()
    if k not in st.session_state or st.session_state[k] == st.session_state.get(k + "_sync", ""):
        st.session_state[k] = source
        st.session_state[k + "_sync"] = source


def _df_initial():
    return pd.DataFrame([{COL_GAMME: GAMME_DEFAUT, COL_PROD: PRODUIT_DEFAUT, COL_REF: reference(PRODUIT_DEFAUT),
                          COL_SERIE: "", COL_INSTALL: aujourdhui(), COL_MES: "", COL_AUTO: ""}], columns=COLONNES)


def _collecter(df):
    g = lambda k: str(st.session_state.get(P + k) or "").strip()
    return dict(
        roche_nom=g("roche_nom"), roche_fonction=g("roche_fonction"), type=g("type") or "Privé",
        client_nom=g("client_nom"), rep_nom=g("rep_nom"), rep_fonction=g("rep_fonction"),
        client_num=g("client_num"), adresse=g("adresse"), cp=g("cp"), ville=g("ville"),
        siren=g("siren"), service=g("service"), reserves=str(st.session_state.get(P + "reserves") or ""),
        produits=[[str(v if v is not None and str(v) != "nan" else "") for v in row]
                  for row in df[COLONNES].itertuples(index=False, name=None)])


def afficher_section_pv():
    """Section optionnelle (repliée) : saisie du PV d'installation et génération du PDF."""
    with st.expander("📄 PV d'installation (optionnel)", expanded=False):
        st.caption("Facultatif et indépendant du compilateur. Pré-rempli à partir de la fiche SIDIV "
                   "(référent du LBM, intervenant S.I) et de la date du jour ; tout reste modifiable.")
        if P + "base" not in st.session_state:
            st.session_state[P + "base"] = _df_initial()
            st.session_state[P + "ver"] = 0
            st.session_state[P + "type"] = "Privé"
        _suivre("roche_nom", st.session_state.get("sidiv_si_nom"))
        _suivre("rep_nom", st.session_state.get("sidiv_lbm_nom"))

        st.markdown("**Intervenant Roche**")
        c1, c2 = st.columns(2)
        c1.text_input("Nom, Prénom (nom de l'intervenant S.I)", key=P + "roche_nom")
        c2.text_input("Fonction", key=P + "roche_fonction")
        st.markdown("**Client**")
        st.radio("Type de client", ["Privé", "Public"], key=P + "type", horizontal=True)
        c1, c2 = st.columns(2)
        c1.text_input("Nom du client (laboratoire)", key=P + "client_nom")
        c2.text_input("N° client", key=P + "client_num")
        st.text_input("Adresse", key=P + "adresse")
        c1, c2 = st.columns(2)
        c1.text_input("Code postal", key=P + "cp")
        c2.text_input("Ville", key=P + "ville")
        if st.session_state.get(P + "type") == "Public":
            c1, c2 = st.columns(2)
            c1.text_input("N° SIREN / FINESS / autre n° d'identification", key=P + "siren")
            c2.text_input("Service de", key=P + "service")
        else:
            st.text_input("Inscrite au RCS – sous le numéro (SIREN)", key=P + "siren")
        st.markdown("**Représenté par**")
        c1, c2 = st.columns(2)
        c1.text_input("Nom (référent du LBM)", key=P + "rep_nom")
        c2.text_input("Fonction", key=P + "rep_fonction")

        st.markdown("**Système / Produit installé**")
        st.caption("La référence se complète toute seule d'après le produit choisi. "
                   "Le bouton ➕ en bas du tableau ajoute une ligne.")
        base = st.session_state[P + "base"]
        cfg = {COL_GAMME: st.column_config.TextColumn(COL_GAMME, width="small"),
               COL_PROD: st.column_config.SelectboxColumn(COL_PROD, options=list(CATALOGUE_IT), width="large"),
               COL_REF: st.column_config.TextColumn(COL_REF, disabled=True, width="small"),
               COL_SERIE: st.column_config.TextColumn(COL_SERIE, width="small"),
               COL_INSTALL: st.column_config.TextColumn(COL_INSTALL, width="small"),
               COL_MES: st.column_config.TextColumn(COL_MES, width="small"),
               COL_AUTO: st.column_config.TextColumn(COL_AUTO, width="medium")}
        edite = st.data_editor(base, column_config=cfg, hide_index=True, width="stretch", num_rows="dynamic",
                               key=P + "ed_" + str(st.session_state[P + "ver"]))
        edite = edite.fillna("")
        calcule = edite.copy()
        calcule[COL_REF] = calcule[COL_PROD].map(reference)
        # nouvelle ligne : gamme IT et date du jour par défaut
        calcule.loc[calcule[COL_GAMME] == "", COL_GAMME] = GAMME_DEFAUT
        calcule.loc[(calcule[COL_INSTALL] == "") & (calcule[COL_PROD] != ""), COL_INSTALL] = aujourdhui()
        if not calcule.equals(edite):  # référence / valeurs par défaut à jour -> on rafraîchit l'éditeur
            st.session_state[P + "base"] = calcule.reset_index(drop=True)
            st.session_state[P + "ver"] += 1
            st.rerun()

        st.text_area("Réserves si nécessaire", key=P + "reserves", height=80)

        st.divider()
        if st.button("📄 Générer le PV d'installation (PDF)", type="primary", key=P + "gen"):
            try:
                st.session_state[P + "pdf"] = generer_pdf(_collecter(calcule))
            except Exception as e:  # ne doit jamais gêner le reste de l'outil
                st.session_state.pop(P + "pdf", None)
                st.error(f"Échec de la génération du PV : {e}")
        if st.session_state.get(P + "pdf"):
            nom = str(st.session_state.get(P + "client_nom") or "").strip().replace(" ", "_").replace("/", "-")
            st.download_button("⬇️ Télécharger le PV d'installation (PDF)", data=st.session_state[P + "pdf"],
                               file_name="PVInstall" + (f"_{nom}" if nom else "") + ".pdf",
                               mime="application/pdf", key=P + "dl")
