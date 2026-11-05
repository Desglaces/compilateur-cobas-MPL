import streamlit as st
import pandas as pd
import pypdf
import re
import io
import difflib
import unicodedata

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageOps
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

VERSION = "v6.01"

# =========================================================================
# BASE DE DONNÉES INTERNE DES CODES ACN
# =========================================================================
# Table générique : s'applique quel que soit le type d'échantillon.
# Les surcharges par type d'échantillon (MAPPING_ACN_PAR_TYPE, plus bas) sont prioritaires.
MAPPING_ACN = {
    "AAGP2": "20020", "AAT2": "20030", "ACET2": "20042", "ALBT2U": "20061",
    "ALB2": "20090", "ALB2-G": "20090", "ALP2": "20110", "ALTP2": "20140",
    "AMIK2": "20150", "AMPS2": "20162", "AMYL2": "20170", "APOAT": "20190",
    "APOBT": "20200", "ASLOT": "20210", "ASTP2": "20230", "B2MG": "20250",
    "BNZ2": "20281", "BILD2": "20301", "BILD2-J": "20301", "BILT3": "20312",
    "BILT-3": "20312", "C3C-2": "20320", "C4-2": "20330", "CA2": "20341",
    "CARB4": "20351", "CERU": "20360", "CHE2": "20370", "CHOL2-I": "20411",
    "CHOL2-1": "20411", "CHOL2": "20411", "CK": "20420", "CL": "29250",
    "CL-U": "29251", "CO2-L": "20440", "COC2": "20451", "CREP2": "20461",
    "CREP2U": "20461", "21500": "21500", "CRP4": "20500", "ETOH2": "20560",
    "FERR4": "20570", "FRA": "20580", "GENT2": "20591", "GGT2-S": "20600",
    "GGT2-1": "20600", "GLUC3": "20631", "GLUC3U": "20631", "HAPT2": "20640",
    "HCYS": "20700", "HDLC4": "20710", "IGA-2": "20720", "IGG-2": "20740",
    "IGM-2": "20750", "IRON2": "20770", "K": "29240", "K-U": "29241",
    "LACT2": "20791", "LDHI2": "20811", "LDHI2P": "20811", "LDLC3": "20820",
    "LI": "20840", "LIP": "20850", "LPA2": "20860", "MDN2": "20880",
    "MG2": "20891", "NA-U": "29231", "NH3L2": "20940", "OPI2": "20952",
    "PHNO2": "20970", "PHNY2": "20980", "PHOS2": "20990", "PHOS2 URINE": "20991",
    "PREA": "21010", "RF-II": "21040", "THC2": "21071", "TP2": "21110",
    "TPUC3-U": "21122", "TPU3": "21122", "TRIGL": "21130", "TRSF2": "21150",
    "UREAL-U": "21190", "UREAL": "21191", "VANC3": "21211", "UA2": "21170",
    "ACTH": "10206", "AFP": "10209", "HBSAG 2": "10049", "AMHP": "10158",
    "ACCP": "10084", "AHAVIGM": "10162", "AHAV 2": "10156", "AHBC 2": "10142",
    "ANTI-HBE (AHBE)": "10033", "A-HBS 2": "10179", "AHCV 2": "10189",
    "ANTI-HEV IGG": "10222", "ANTI-HEV IGM": "10223", "ATG": "10202",
    "ATSHR": "10174", "HCG-BETA": "10072", "B12 2": "10088",
    "CROSSL": "10062", "CA125 2": "10018", "CA15-3 2": "10002",
    "CA 19-9": "10019", "HCT": "10191", "CEA": "10003",
    "CSA": "10109", "CK-MB": "10041", "CMV IGG": "10218",
    "CMV IGM": "10087", "CORT 2": "10042", "C-PEPTIDE (CPEPTID)": "10081",
    "CYFRA 21-1": "10030", "ASD": "10147", "DIGO": "10056",
    "EBVEBNA": "10165", "EBVIGM": "10163", "EBVVCAG": "10125",
    "E2 3": "10100", "FBHCG": "10017",
    "FOL 3": "10168", "FOLATE III (RBC / ÉRYTHRO.)": "10169",
    "FPSA": "10188", "FSH": "10207", "FT3 3": "10220",
    "FT4 4": "10195", "PROGRP": "10108", "HBEAG": "10036", "HE4": "10102",
    "HGH": "10096", "IGFBP-3": "10117", "INSULIN": "10059", "LH": "10113",
    "MYO": "10028", "NSE": "10073", "N-MID OSTÉOCALCINE": "10060",
    "P1NP TOTAL": "10119", "PAPP-A": "10089", "PCTX": "10241",
    "PLGF": "10038", "PBNPX": "10237", "PROG 3": "10045", "TPSA": "10185",
    "PTH (1-84)": "10101", "RUBIGG": "10024", "RUBELLA IGM": "10021",
    "ANTI-SARS-COV-2 S": "10230", "DHEA-S": "10068", "SFLT-1": "10046",
    "IGF-1": "10116", "SYPHILIS": "10212", "TCL": "10022",
    "TESTO 2": "10020", "TG II": "10215", "TOXO IGG": "10047",
    "TOXO IGM": "10016", "TNTHSSTX": "10240", "TSH": "10172",
    "VITDT 3": "10194", "IGE II": "10057", "PRL 2": "10111",
    "SHBG": "10071", "ATPO 2": "10187", "HBCM": "10140", "AHIV": "11013",
    "HIVAG": "11014", "HIV DUO": "12018",
    # Ajouts v6.00 (observés dans le jeu de connexion La Scala, à valider)
    "CK2": "20420", "LACT2P": "20791", "PBNPSTX": "10238",
    "AHIV_01": "12018-AHIV_01-1", "HIVAG_01": "12018-HIVAG_01-1",
}

# Surcharges par type d'échantillon (prioritaires sur MAPPING_ACN).
# Types normalisés : SER (sérum/plasma), URI (urine), LCR (liquide céphalo-rachidien).
# Valeurs déduites du jeu de connexion La Scala + driver cobaspro-258 (à valider).
MAPPING_ACN_PAR_TYPE = {
    ("GLUC3", "SER"): "20630",
    ("GLUC3U", "URI"): "20631",
    ("GLUC3C", "LCR"): "20632",
    ("CREP2", "SER"): "20460",
    ("CREP2U", "URI"): "20461",
    ("CA2", "SER"): "20340",
    ("GGT2-S", "SER"): "20601",
    ("ALBT2", "SER"): "20060",
    ("NA", "SER"): "29230",
    ("TPC3", "LCR"): "21123",
}

def get_acn_from_mapping(nom_test, type_ech=""):
    nom_upper = str(nom_test).upper().strip()
    t = str(type_ech or "").upper().strip()
    base_name = re.sub(r'[-\s][I123]+$', '', nom_upper).strip()
    for v in (nom_upper, base_name):
        if t and (v, t) in MAPPING_ACN_PAR_TYPE: return MAPPING_ACN_PAR_TYPE[(v, t)]
        if v in MAPPING_ACN: return MAPPING_ACN[v]
    base_alpha = re.sub(r'[^A-Z0-9]', '', nom_upper)
    if t:
        for (k, kt), v in MAPPING_ACN_PAR_TYPE.items():
            if kt == t and re.sub(r'[^A-Z0-9]', '', k) == base_alpha: return v
    for k, v in MAPPING_ACN.items():
        if re.sub(r'[^A-Z0-9]', '', k) == base_alpha: return v
    return ""

def read_csv_safe(file_bytes):
    # keep_default_na=False + na_values=[''] : seules les cellules vides sont des valeurs manquantes.
    # Sans cela, pandas lit le code "NA" (sodium) comme une valeur manquante.
    seps = [';', ',']
    encodings = ['utf-8', 'latin1', 'cp1252']
    for enc in encodings:
        for sep in seps:
            try:
                df = pd.read_csv(io.BytesIO(file_bytes), sep=sep, encoding=enc, keep_default_na=False, na_values=[''])
                if len(df.columns) > 1: return df
            except Exception: pass
    return pd.read_csv(io.BytesIO(file_bytes), sep=';', keep_default_na=False, na_values=[''])

def colonne(df, motif):
    cols = [c for c in df.columns if motif in str(c)]
    return cols[0] if cols else None

def clean_acn(val):
    s = str(val).strip()
    if s.endswith('.0'): return s[:-2]
    return s

def normalize_string(s):
    if pd.isna(s) or not isinstance(s, str): return ""
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8').lower().strip()

def are_values_equivalent(v1, v2):
    s1, s2 = str(v1).strip().lower(), str(v2).strip().lower()
    if s1 == s2: return True
    if s1.replace(' ', '') == s2.replace(' ', ''): return True
    try:
        c1 = re.sub(r'[^\d\.\,\-]', '', s1).replace(',', '.')
        c2 = re.sub(r'[^\d\.\,\-]', '', s2).replace(',', '.')
        if not c1 or not c2: return False
        f1, f2 = float(c1), float(c2)
        if abs(f1 - f2) < 1e-5: return True
        d1 = len(c1.split('.')[1]) if '.' in c1 else 0
        d2 = len(c2.split('.')[1]) if '.' in c2 else 0
        return abs(f1 - f2) <= 0.61 * (10 ** -min(d1, d2))
    except Exception:
        return False

def match_tubes_correct(t_cobas, t_mpl):
    tc, tm = str(t_cobas).strip(), str(t_mpl).strip()
    if tc == tm: return True
    if len(tc) == len(tm) + 2 and (tc[2:] == tm or tc[:-2] == tm): return True
    if len(tm) == len(tc) + 2 and (tm[2:] == tc or tm[:-2] == tc): return True
    return False

def index_driver(df_driver):
    """Retourne (acn -> [(code MPL, sous-champ)], code MPL -> [index des lignes du driver])."""
    col_nom = colonne(df_driver, "Nom de l")
    col_acn = colonne(df_driver, "Code ACN")
    col_sc = colonne(df_driver, "Sous-champ")
    acn_to_mpl, code_to_rows = {}, {}
    for idx, row in df_driver.iterrows():
        acn = clean_acn(row[col_acn])
        nom = str(row[col_nom]).strip()
        sc = clean_acn(row[col_sc]) if col_sc else ""
        if nom and nom != 'nan':
            code_to_rows.setdefault(nom, []).append(idx)
        if acn and acn != 'nan' and nom and nom != 'nan':
            acn_to_mpl.setdefault(acn, []).append((nom, sc))
    return acn_to_mpl, code_to_rows

def codes_mpl_attendus(acn, interpretation, acn_to_mpl):
    """Codes MPL alimentés par cet ACN. Valeur : sous-champ 1 en premier.
    Interprétation : uniquement le sous-champ 2 (si le driver renseigne les sous-champs)."""
    lst = acn_to_mpl.get(acn, [])
    if interpretation:
        s2 = [n for n, sc in lst if sc == "2"]
        return s2 if (s2 or any(sc for _, sc in lst)) else [n for n, _ in lst]
    return [n for n, sc in lst if sc == "1"] + [n for n, sc in lst if sc != "1"]

# =========================================================================
# LECTURE DU RAPPORT COBAS (mode "layout" de pypdf : une ligne du PDF = une ligne de texte)
# =========================================================================
RE_COBAS_RESULTAT = re.compile(
    r'^(?:[<>]=?\s*)?-?\d+(?:[.,]\d+)?(?:[eE][+-]?\d+)?$|^\*+$|'
    r'^(?:positif|n[ée]gatif|douteux|r[ée]actif|non\s*r[ée]actif|nonreac|reac|ind[ée]tectable)$',
    re.IGNORECASE)
RE_COBAS_MODULE = re.compile(r'^(?:[A-Za-z]\d+-\d+-[A-Za-z0-9]+|ISE\S*)$')
RE_COBAS_LIGNE_R = re.compile(r'^R\d$')
RE_DATE_FIN = re.compile(r'\d{2}/\d{2}/\d{4}(?:\d{2}:\d{2}(?::\d{2})?)?$')
RE_COBAS_ENTETES = re.compile(
    r'^(Symboles li|‘\+’|‘\*’|\'\+\'|\'\*\'|Rapport r[ée]sultats|Type de r[ée]sultat|Type [ée]chant|'
    r'Comment\.|NOM\s*:|Test\s{2,}R[ée]sultat|Unit[ée]\s{2,}|Message de r[ée]sultat|Syst[èe]me\s*:)',
    re.IGNORECASE)
# Messages d'interprétation reconnus (comparés sans accents ni majuscules)
RE_COBAS_INTERP = re.compile(r'^(?:non\s*-?\s*)?reac(?:tif|tive)?$|^(?:douteux|positif|negatif|indetermine|equivoque)$')
UNITES_SEULES = {"COI", "INDEX", "%", "-", "RATIO", "AU/ML", "U", "IU", "UI"}
RE_COBAS_CODE_TEST = re.compile(r'^[A-Za-z0-9][\w\-\.]*(?: \w+)?$')

def est_rapport_cobas(texte_page1):
    t = texte_page1 or ""
    return (re.search(r'Rapport\s+r[ée]sultats\s+[ée]chant', t, re.IGNORECASE) is not None
            and re.search(r'Examen\s*n', t, re.IGNORECASE) is None)

def type_echantillon(libelle):
    """Normalise le type d'échantillon du rapport cobas : SER, URI, LCR, sinon le libellé en majuscules."""
    s = (libelle or '').strip().lower()
    if s.startswith(('ser', 'sér', 'plas', 's/p')): return 'SER'
    if s.startswith(('urin', 'uri')): return 'URI'
    if s.startswith(('csf', 'lcr')): return 'LCR'
    return (libelle or '').strip().upper()

def convertir_module(module_raw):
    # Convention conservée depuis la v5.40 : on retire 1 au premier nombre (c7-1-B -> c7-0-B).
    if module_raw.isdigit(): return str(int(module_raw) - 1)
    if "-" in module_raw:
        parts = module_raw.split("-")
        for k in range(len(parts)):
            if parts[k].isdigit(): parts[k] = str(int(parts[k]) - 1); break
        return "-".join(parts)
    return module_raw

def _segments(ligne):
    return [s.strip() for s in re.split(r'\s{2,}', ligne.strip()) if s.strip()]

def lire_rapport_cobas(textes_pages):
    """Lit le "Rapport résultats échant." du cobas pro.
    Retourne (résultats, lignes non reconnues). Un résultat = un test d'un échantillon."""
    resultats, non_reconnues = [], []
    lignes = []
    for num_page, texte in enumerate(textes_pages, start=1):
        for brut in (texte or '').split('\n'):
            ligne = brut.rstrip()
            if ligne.strip() and not RE_COBAS_ENTETES.match(ligne.strip()):
                lignes.append((num_page, ligne))

    def segments_corps(ligne):
        m = re.match(r'^([+*](?:\s*[+*])?)(?=\s)', ligne)
        drapeau = re.sub(r'\s', '', m.group(1)) if m else ''
        return drapeau, _segments(ligne[m.end():] if m else ligne)

    def est_entete_echantillon(ligne):
        # Ligne d'en-tête d'un échantillon : commence en colonne 0 (type d'échantillon), pas en retrait
        if ligne[:1].isspace() or ligne[:1] in '+*': return False
        return (re.search(r'ID\s*:', ligne) is not None or re.search(r'Lot\s+de\s+CQ\s*:', ligne, re.IGNORECASE) is not None
                or (re.search(r'\b\d{4,6}-\d{1,2}\b', ligne) is not None and re.search(r'\d{2}:\d{2}:\d{2}', ligne) is not None))

    def est_ligne_unite(segs):
        return any(RE_COBAS_MODULE.match(s) for s in segs) or '/' in segs[0] or segs[0].upper() in UNITES_SEULES

    def suivante_est_unite(i):
        for j in range(i + 1, min(i + 3, len(lignes))):
            if est_entete_echantillon(lignes[j][1]): continue  # en-tête répété en haut de page
            segs = segments_corps(lignes[j][1])[1]
            return bool(segs) and est_ligne_unite(segs) and not RE_COBAS_LIGNE_R.match(segs[0])
        return False

    ech, etat, dernier, parent = None, 'libre', None, None
    for i, (num_page, ligne) in enumerate(lignes):
        if est_entete_echantillon(ligne):
            m_id = re.search(r'ID\s*:\s*(\S+)', ligne)
            id_ech = RE_DATE_FIN.sub('', m_id.group(1)) if m_id else ''
            if not id_ech:
                # Bloc sans identifiant d'échantillon (contrôle qualité ou format inconnu) : non attribué
                ech, etat, dernier, parent = None, 'libre', None, None
                non_reconnues.append((num_page, ligne.strip()))
                continue
            segs = _segments(ligne)
            type_brut = segs[0] if segs and not segs[0].startswith('ID') else ''
            if ech is None or ech['id'] != id_ech:
                ech = {'id': id_ech, 'type_brut': type_brut, 'type': type_echantillon(type_brut)}
                etat, dernier, parent = 'libre', None, None
            continue
        drapeau, segs = segments_corps(ligne)
        if not segs: continue
        if RE_COBAS_LIGNE_R.match(segs[0]): continue  # lots de réactifs R1/R2/R3
        if len(segs) == 2 and segs[0].lower() == 'non' and RE_COBAS_INTERP.match(normalize_string(' '.join(segs))):
            segs = [' '.join(segs)]  # "Non   réactif" éclaté en deux colonnes
        a_module = any(RE_COBAS_MODULE.match(s) for s in segs)
        ressemble_test = (len(segs) >= 2 and RE_COBAS_RESULTAT.match(segs[1]) is not None
                          and not RE_COBAS_MODULE.match(segs[1]) and not a_module)
        interp = len(segs) == 1 and RE_COBAS_INTERP.match(normalize_string(segs[0])) is not None

        if etat == 'attente_unite' and dernier is not None:
            if interp:  # interprétation directement sous la ligne de test, sans ligne d'unité
                dernier['interpretation'] = segs[0]
                etat = 'bloc'
                continue
            if not (ressemble_test and not est_ligne_unite(segs)):
                if RE_COBAS_MODULE.match(segs[0]):  # test sans unité : la ligne commence par le module
                    dernier['module_brut'] = segs[0]
                else:
                    dernier['unite'] = segs[0]
                    for s in segs[1:]:
                        if RE_COBAS_MODULE.match(s):
                            dernier['module_brut'] = s
                            break
                if not dernier['module_brut'] and '*' in dernier['drapeau'] and parent is not None and parent is not dernier:
                    dernier['module_brut'] = parent['module_brut']  # sous-résultat e flow : module du parent
                etat = 'bloc'
                continue
            # sinon : nouvelle ligne de test (le test précédent n'avait pas de ligne d'unité)

        est_test = (ech is not None and ressemble_test and segs[0].upper() not in UNITES_SEULES
                    and ('/' not in segs[0] or suivante_est_unite(i)))
        sans_valeur = (ech is not None and not est_test and len(segs) >= 2 and not a_module
                       and RE_COBAS_CODE_TEST.match(segs[0]) is not None and not est_ligne_unite(segs)
                       and suivante_est_unite(i))
        if est_test or sans_valeur:
            dernier = {'id': ech['id'], 'type': ech['type'], 'type_brut': ech['type_brut'],
                       'test': segs[0], 'resultat': segs[1] if est_test else '',
                       'alarme': ' '.join(segs[2:] if est_test else segs[1:]),
                       'drapeau': drapeau, 'unite': '', 'module_brut': '', 'interpretation': ''}
            resultats.append(dernier)
            if '*' in drapeau and set(dernier['resultat']) == {'*'}: parent = dernier
            etat = 'attente_unite'
            continue
        if etat == 'bloc' and dernier is not None and interp and not dernier['interpretation']:
            dernier['interpretation'] = segs[0]
            continue
        non_reconnues.append((num_page, ligne.strip()))
    return resultats, non_reconnues

# =========================================================================

st.set_page_config(page_title=f"Compilateur Cobas & MPL {VERSION}", layout="wide")

col_vide, col_bouton = st.columns([4, 1])
with col_bouton: dark_mode = st.toggle("🌙 Mode Sombre")

css = """
<style>
/* Liste des fichiers masquée pour la case 1 seulement (les noms des CSV restent visibles) */
.st-key-depot_fichiers [data-testid="stFileUploaderFileList"] { display: none; }
.st-key-depot_fichiers [data-testid="stFileChip"] { display: none; }
</style>
"""
if dark_mode:
    css += """
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .st-emotion-cache-1wivap2 { color: #FAFAFA; }
    div[data-testid="stFileUploader"] > section { background-color: #262730; }
    </style>
    """
st.markdown(css, unsafe_allow_html=True)

st.title(f"🧪 Compilateur de Résultats Cobas & MPL vers Excel (Version {VERSION})")

if not OCR_AVAILABLE:
    st.warning("⚠️ Module `pytesseract` ou `Pillow` non détecté. L'extraction depuis des images sera désactivée.")

# === EXPORT VIERGE ===
st.info("💡 **Astuce :** Vous pouvez générer un fichier Excel d'analyses vierges dès maintenant (sans déposer de fichier) si vous souhaitez faire une saisie entièrement manuelle.")
colonnes_vierge = ["Nom de l'analyse", "Nom MPL", "Numéro de tube", "Module CPRO", "Résultat CPRO", "Unité CPRO", "Facteur de conversion COBASPRO", "Résulat MPL", "Unité MPL", "Facteur de conversion MPL", "Résultat Kalisil", "Unité Kalisil", "Code ACN", "Id de l'analyse", "Sous-champ résultat", "Résultat QC", "NEGATIF/POSITIF/DOUTEUX", "Repassage"]
df_export_vierge = pd.DataFrame(columns=colonnes_vierge)
output_vierge = io.BytesIO()
with pd.ExcelWriter(output_vierge, engine='xlsxwriter') as writer: 
    df_export_vierge.to_excel(writer, index=False, sheet_name="L3_cobaspro")
output_vierge.seek(0)
st.download_button("⬇️ Télécharger la trame vierge", data=output_vierge, file_name="Modele_Vierge_MPL.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
st.divider()

if "etape" not in st.session_state:
    st.session_state.etape = 1
    st.session_state.df_cobas = None
    st.session_state.df_mpl = None
    st.session_state.df_final = None

def process_files(uploaded_files, csv_bytes=None, csv_mpl_trans_bytes=None):
    cobas_records = []
    mpl_records = []
    erreurs = []
    lignes_non_reconnues = []

    unites_cobas = [
        "COI", "G/L", "MG/L", "U/L", "IU/L", "UI/L", "MIU/ML", "MUI/ML", "MUI/L",
        "MMOL/L", "MMOLE/L", "UMOLES/L", "UMOL/L", "PMOL/L", "NMOL/L", "NG/ML", "PG/ML",
        "INDEX", "UI/ML", "IU/ML", "NG/DL", "UG/L", "MG/DL", "UG/DL",
        "µIU/ML", "µUI/ML", "UIU/ML", "UUI/ML", "ΜIU/ML", "ΜUI/ML", "U/ML",
        "µMOL/L", "ΜMOL/L", "µG/L", "ΜG/L", "NG/L", "-"
    ]
    mots_dechets = ["TEST", "NONREAC", "NON REACTIF"]
    res_pattern = r'([<>]*\s*[0-9]+[\.\,]?[0-9]*[aA]?(?:\s*<Test|\s*>Test)?|<Test|>Test|\bTest\b|\\?sup|positif|négatif|negatif|douteux|réactif|reactif|nonreac|non\s*réactif|indétectable|indetectable|En\s*cours)'

    vocabulaire_mpl = []
    acn_to_mpl = {}
    if csv_bytes:
        df_driver_temp = read_csv_safe(csv_bytes)
        col_nom_driver = colonne(df_driver_temp, "Nom de l")
        vocabulaire_mpl = df_driver_temp[col_nom_driver].dropna().astype(str).str.strip().unique().tolist()
        vocabulaire_mpl.sort(key=len, reverse=True)
        acn_to_mpl, _ = index_driver(df_driver_temp)

    libellong_list = []
    if csv_mpl_trans_bytes:
        df_trans = read_csv_safe(csv_mpl_trans_bytes)
        if 'LibelLong' in df_trans.columns and 'Nom' in df_trans.columns:
            for _, row in df_trans.iterrows():
                ll = str(row['LibelLong']).strip()
                nom = str(row['Nom']).strip()
                if ll and ll != 'nan' and nom and nom != 'nan':
                    libellong_list.append((ll, nom))

    def get_mpl_candidats(test_name_pdf):
        """Tous les codes MPL qui partagent le libellé lu sur le CR (un libellé peut servir à plusieurs codes)."""
        if not libellong_list: return [test_name_pdf]
        tn = test_name_pdf.strip()
        tn_norm = normalize_string(tn)
        for cond in (lambda ll: ll.strip() == tn,
                     lambda ll: ll.strip().lower() == tn.lower(),
                     lambda ll: normalize_string(ll) == tn_norm):
            trouves = [n for ll, n in libellong_list if cond(ll)]
            if trouves: return list(dict.fromkeys(trouves))
        best_ll = None
        best_ratio = 0.0
        for ll, n in libellong_list:
            ratio = difflib.SequenceMatcher(None, tn_norm, normalize_string(ll)).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_ll = ll
        if best_ratio > 0.85:
            return list(dict.fromkeys(n for ll, n in libellong_list if ll == best_ll))
        return [tn]

    def ajouter_mpl(test_name_pdf, tube_id, res, unit):
        cands = get_mpl_candidats(test_name_pdf)
        mpl_records.append({
            "Nom de l'analyse": cands[0], "Numéro de tube": tube_id, "Résulat MPL": res, "Unité MPL": unit,
            "Libellé CR MPL": test_name_pdf, "Codes MPL possibles": " | ".join(cands)
        })

    for uploaded_file in uploaded_files:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        records_found_for_file = 0

        # ================= LECTURE PDF =================
        if file_ext == 'pdf':
            reader = pypdf.PdfReader(uploaded_file)
            textes_layout = [(p.extract_text(extraction_mode="layout") or "") for p in reader.pages]
            if not "".join(textes_layout).strip():
                erreurs.append(f"⚠️ Le PDF '{uploaded_file.name}' ne contient aucun texte lisible (document scanné ?). Fournis-le en image (png/jpg) pour passer par l'OCR.")
                continue

            if est_rapport_cobas(textes_layout[0]):
                resultats, non_reconnues = lire_rapport_cobas(textes_layout)
                for p, l in non_reconnues:
                    lignes_non_reconnues.append({"Fichier": uploaded_file.name, "Page": p, "Ligne": l})
                for r in resultats:
                    if set(r['resultat']) == {'*'}: continue  # parent e flow sans valeur (les sous-résultats suivent)
                    if re.match(r'^(SI|SI2|S12)\b', r['test'].upper()): continue  # indices sériques, exclus comme en v5.40
                    resultat = r['resultat']
                    m_borne = re.search(r'[<>]Test', r['alarme'])
                    if not resultat: resultat = r['alarme']  # pas de valeur : on affiche l'alarme du cobas
                    elif m_borne: resultat = f"{resultat} {m_borne.group(0)}"
                    module = convertir_module(r['module_brut']) if r['module_brut'] else ""
                    commun = {"Numéro de tube": r['id'], "Module CPRO": module,
                              "Type échantillon": r['type_brut'], "_type": r['type'],
                              "Alarme": r['alarme'], "Réanalyse": "oui" if '+' in r['drapeau'] else ""}
                    cobas_records.append({"Nom de l'analyse": r['test'], "Résultat CPRO": resultat, "Unité CPRO": r['unite'], **commun})
                    records_found_for_file += 1
                    if r['interpretation']:
                        cobas_records.append({"Nom de l'analyse": f"{r['test']} (Interprétation)", "Résultat CPRO": r['interpretation'], "Unité CPRO": "", **commun})
                if records_found_for_file == 0:
                    erreurs.append(f"⚠️ Le rapport cobas '{uploaded_file.name}' n'a retourné aucun résultat.")
            else:
                tube_id = "UNKNOWN"
                for page_layout in textes_layout:
                    lines = [l.strip() for l in page_layout.split('\n') if l.strip()]

                    if tube_id == "UNKNOWN":
                        text_full = " ".join(lines)
                        m_examen = re.search(r'Examen\s*n.*?([A-Za-z0-9]{6,})', text_full, re.IGNORECASE)
                        if m_examen:
                            tube_id = m_examen.group(1)
                        else:
                            m_pv = re.search(r'(PV[A-Za-z0-9]{5,})', text_full)
                            if m_pv:
                                tube_id = m_pv.group(1)
                            else:
                                m_id = re.search(r'\b(\d{8,16})\b', text_full)
                                if m_id:
                                    tube_id = m_id.group(1)

                    for line in lines:
                        if line.strip().startswith("Page ") or "Normales" in line or line.strip() == "Résultat": continue
                        parts = [p.strip() for p in re.split(r'\s{2,}', line) if p.strip()]
                        if len(parts) >= 2:
                            test_name = parts[0]
                            exclusions = ["patient", "né", "edité", "prélevé", "t.sec", "examen", "indice", "repasse", "urines", "comment", "n°", "du", "à", "aspect", "prescripteur"]
                            if any(test_name.lower().startswith(excl) for excl in exclusions): continue
                            if not re.search(r'[A-Za-zÀ-ÿ]', test_name): continue

                            res_unit_text = " ".join(parts[1:])
                            m_res = re.match(r'^'+res_pattern+r'(.*)', res_unit_text.strip(), re.IGNORECASE)

                            if m_res:
                                res = m_res.group(1).strip()
                                unit_raw = m_res.group(2).strip()
                            else:
                                res = parts[1]
                                unit_raw = parts[2] if len(parts) > 2 else ""

                            # Coupe l'unité avant la colonne "Normales" (chiffres, flèches ou "-" isolé)
                            unit = re.split(r'\s+(?:[0-9]|[\↑\↓\☒\个<>\~]|-(?=\s|$))', re.sub(r'[\ue000-\uf8ff]', ' ', unit_raw))[0].strip() if unit_raw else ""
                            if unit.startswith(("<", ">")): unit = ""  # pas d'unité : c'est la colonne "Normales"
                            ajouter_mpl(test_name, tube_id, res, unit)
                            records_found_for_file += 1
                if records_found_for_file == 0:
                    erreurs.append(f"⚠️ Le compte rendu MPL '{uploaded_file.name}' n'a retourné aucune analyse (ni rapport cobas reconnu, ni ligne de résultat MPL).")

        # ================= LECTURE IMAGE AVEC PRE-TRAITEMENT =================
        elif file_ext in ['png', 'jpg', 'jpeg'] and not OCR_AVAILABLE:
            erreurs.append(f"⚠️ Image '{uploaded_file.name}' ignorée : le module OCR (pytesseract / Pillow) n'est pas installé.")
        elif file_ext in ['png', 'jpg', 'jpeg'] and OCR_AVAILABLE:
            try:
                img = Image.open(uploaded_file)
                w, h = img.size
                img = img.resize((w * 2, h * 2), getattr(Image, 'LANCZOS', getattr(Image, 'ANTIALIAS', 1)))
                img = img.convert('L')
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(2.0)
                img = img.point(lambda p: 255 if p > 150 else 0)

                text = pytesseract.image_to_string(img, config='--psm 6')
            except Exception as e:
                erreurs.append(f"⚠️ Image '{uploaded_file.name}' non lue par l'OCR ({type(e).__name__} : {e}). Le programme Tesseract est-il installé sur ce poste ?")
                continue

            lines = [l.strip() for l in text.split('\n') if l.strip()]
            tube_id = "UNKNOWN"

            text_full = " ".join(lines)
            m_examen = re.search(r'Examen\s*n.*?([A-Za-z0-9]{6,})', text_full, re.IGNORECASE)
            if m_examen:
                tube_id = m_examen.group(1)
            else:
                m_pv = re.search(r'(PV[A-Za-z0-9]{5,})', text_full)
                if m_pv:
                    tube_id = m_pv.group(1)
                else:
                    m_id = re.search(r'\b(\d{8,16})\b', text_full)
                    if m_id:
                        tube_id = m_id.group(1)

            libelles_tries = sorted({ll for ll, _ in libellong_list}, key=len, reverse=True)
            for line in lines:
                test_name_trouve = None
                reste_ligne = ""
                ligne_norm = normalize_string(line)

                # 1) Libellé du compte rendu MPL (export analyses) : le plus long qui commence la ligne
                for ll in libelles_tries:
                    ll_norm = normalize_string(ll)
                    if ll_norm and ligne_norm.startswith(ll_norm) and (len(ligne_norm) == len(ll_norm) or ligne_norm[len(ll_norm)] == ' '):
                        test_name_trouve = ll
                        reste_ligne = " ".join(line.split()[len(ll.split()):])
                        break

                # 2) Code MPL du driver présent dans la ligne
                if not test_name_trouve and vocabulaire_mpl:
                    for vocab in vocabulaire_mpl:
                        pattern = r'(?i)\b' + re.escape(vocab) + r'\b'
                        m_vocab = re.search(pattern, line)
                        if m_vocab:
                            test_name_trouve = vocab
                            reste_ligne = line[m_vocab.end():]
                            break

                # 3) Sans référentiel : le nom est ce qui précède la première valeur de la ligne
                if not test_name_trouve:
                    matches = list(re.finditer(r'\s+'+res_pattern+r'(?=\s|$)', line, re.IGNORECASE))
                    if matches:
                        first_match = matches[0]
                        pot_name = line[:first_match.start()].strip()
                        pot_name = re.sub(r'^\+\s*', '', pot_name).strip()
                        exclusions = ["validation", "séquence", "position", "essai", "patient", "né", "edité", "prélevé", "examen", "n°", "groupe", "sexe", "tri"]
                        
                        is_waste = False
                        if not pot_name or not re.search(r'[A-Za-z]', pot_name): is_waste = True
                        if any(pot_name.lower().startswith(excl) for excl in exclusions): is_waste = True
                        if "COBAS" in pot_name.upper() or "SYSTEM" in pot_name.upper(): is_waste = True
                        for u in unites_cobas + mots_dechets:
                            if pot_name.upper() == u or pot_name.upper().startswith(u + " ") or pot_name.upper().startswith(u + "-"):
                                is_waste = True
                                break
                        
                        if not is_waste:
                            test_name_trouve = pot_name
                            reste_ligne = line[first_match.start():]
                
                if test_name_trouve and reste_ligne:
                    m_res = re.match(r'^\s*'+res_pattern+r'(.*)', reste_ligne.strip(), re.IGNORECASE)
                    res, unit_raw = "", ""
                    if m_res:
                        res = m_res.group(1).strip()
                        unit_raw = m_res.group(2).strip()
                        if re.match(r'^[<>]?\s*\d+a$', res.lower()): res = res[:-1] + '.4'
                        elif re.match(r'^[<>]?\s*\d+[\.,]\d*a$', res.lower()): res = res[:-1] + '4'

                    if res:
                        unit_raw = unit_raw.lstrip(",;: ")
                        unit = re.split(r'\s+(?:[0-9]|[\↑\↓\☒\个<>\~]|-(?=\s|$))', re.sub(r'[\ue000-\uf8ff]', ' ', unit_raw))[0].strip() if unit_raw else ""
                        if unit.startswith(("<", ">")): unit = ""
                        ajouter_mpl(test_name_trouve, tube_id, res, unit)

    # ===== Libellés MPL partagés par plusieurs codes : on garde le code alimenté par le cobas pour ce tube =====
    if acn_to_mpl:
        for rec in mpl_records:
            cands = rec["Codes MPL possibles"].split(" | ")
            if len(cands) < 2: continue
            attendus = set()
            for c in cobas_records:
                if match_tubes_correct(c["Numéro de tube"], rec["Numéro de tube"]):
                    acn = get_acn_from_mapping(c["Nom de l'analyse"].replace(" (Interprétation)", "").strip(), c["_type"])
                    attendus.update(n for n, _ in acn_to_mpl.get(acn, []))
            retenus = [n for n in cands if n in attendus]
            if retenus: rec["Nom de l'analyse"] = retenus[0]

    df_c = pd.DataFrame(cobas_records) if cobas_records else pd.DataFrame(columns=["Nom de l'analyse", "Numéro de tube", "Module CPRO", "Résultat CPRO", "Unité CPRO", "Type échantillon", "_type", "Alarme", "Réanalyse"])
    def cle_cobas(r):
        # Clé de correspondance de l'étape 2 : nom du test + type d'échantillon (ex. "GLUC3 [Ser/PI]")
        nom, typ = r["Nom de l'analyse"], r["Type échantillon"]
        return f"{nom} [{typ}]" if typ else nom
    df_c["_cle"] = df_c.apply(cle_cobas, axis=1) if not df_c.empty else []
    df_m = pd.DataFrame(mpl_records) if mpl_records else pd.DataFrame(columns=["Nom de l'analyse", "Numéro de tube", "Résulat MPL", "Unité MPL", "Libellé CR MPL", "Codes MPL possibles"])
    if not df_m.empty: df_m = df_m.drop_duplicates(subset=["Nom de l'analyse", "Numéro de tube", "Résulat MPL"], keep="first").reset_index(drop=True)
    df_nr = pd.DataFrame(lignes_non_reconnues, columns=["Fichier", "Page", "Ligne"])
    return df_c, df_m, erreurs, df_nr

# -------------------------------------------------------------------------------------

st.subheader("Étape 1 : Dépôt des fichiers")
uploaded_files = st.file_uploader("1️⃣ Déposez les fichiers PDF ou IMAGES (png, jpg)", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="depot_fichiers")
if uploaded_files:
    st.info(f"📂 **{len(uploaded_files)} fichier(s) prêt(s) pour l'extraction**")

col_a, col_b = st.columns(2)
with col_a:
    uploaded_csv = st.file_uploader("2️⃣ Obligatoire : Export Driver Manager (onglet Analyse)", type="csv")
with col_b:
    uploaded_csv_mpl = st.file_uploader("3️⃣ Optionnel : Export analyse MPL (CSV)", type="csv")

if uploaded_files and uploaded_csv:
    if st.button("📥 Extraire les données des fichiers"):
        df_drv_check = read_csv_safe(uploaded_csv.getvalue())
        if colonne(df_drv_check, "Nom de l") is None or colonne(df_drv_check, "Code ACN") is None:
            st.error("❌ La case 2️⃣ doit contenir le driver MPL : colonnes \"Nom de l'analyse\" et \"Code ACN\" introuvables. Les deux CSV sont-ils inversés ?")
            st.stop()
        if uploaded_csv_mpl:
            df_exp_check = read_csv_safe(uploaded_csv_mpl.getvalue())
            if 'LibelLong' not in df_exp_check.columns or 'Nom' not in df_exp_check.columns:
                st.warning("⚠️ La case 3️⃣ ne contient pas les colonnes \"LibelLong\" et \"Nom\" : les libellés MPL ne seront pas traduits en codes.")

        for k in list(st.session_state.keys()):
            if k.startswith("widget_") or k == "user_mapping":
                del st.session_state[k]

        with st.spinner("Lecture et analyse intelligente en cours..."):
            csv_mpl_bytes = uploaded_csv_mpl.getvalue() if uploaded_csv_mpl else None
            df_cobas, df_mpl, erreurs, df_non_reconnues = process_files(uploaded_files, uploaded_csv.getvalue(), csv_mpl_bytes)

            if erreurs:
                for err in erreurs:
                    st.error(err)

            st.session_state.df_cobas = df_cobas
            st.session_state.df_mpl = df_mpl
            st.session_state.df_non_reconnues = df_non_reconnues
            st.session_state.csv_file = uploaded_csv.getvalue()
            st.session_state.csv_mpl_bytes = csv_mpl_bytes
            st.session_state.etape = 2

            if not erreurs:
                st.rerun()

if st.session_state.etape >= 2:
    st.divider()
    st.subheader("Étape 2 : Correspondance des analyses")

    df_cobas = st.session_state.df_cobas
    df_mpl = st.session_state.df_mpl
    analyses_cobas = df_cobas["_cle"].dropna().unique()

    if len(analyses_cobas) == 0:
        st.error("❌ Impossible de passer à l'étape 2 : aucun rapport cobas lisible parmi les fichiers déposés dans la première case.")
    else:
        st.info("🪄 **L'outil a pré-rempli les menus déroulants !** Modifiez-les si besoin.")

        analyses_mpl = ["🔴 -- Aucune correspondance --", "❌ -- Ignorer cette analyse --"] + list(df_mpl["Nom de l'analyse"].dropna().unique())

        df_driver = read_csv_safe(st.session_state.csv_file)
        col_acn_driver = colonne(df_driver, "Code ACN")
        col_nom_driver = colonne(df_driver, "Nom de l")
        acn_to_mpl, code_to_rows = index_driver(df_driver)

        nom_to_libellong = {}
        if st.session_state.csv_mpl_bytes:
            df_trans = read_csv_safe(st.session_state.csv_mpl_bytes)
            if 'LibelLong' in df_trans.columns and 'Nom' in df_trans.columns:
                for _, row in df_trans.iterrows():
                    ll = str(row['LibelLong']).strip()
                    nom = str(row['Nom']).strip()
                    if ll and ll != 'nan' and nom and nom != 'nan':
                        nom_to_libellong[nom] = ll

        if "user_mapping" not in st.session_state:
            st.session_state.user_mapping = {}

        premiere_ligne = df_cobas.drop_duplicates(subset=["_cle"]).set_index("_cle")
        for c_test in analyses_cobas:
            if c_test not in st.session_state.user_mapping:
                default_match = "🔴 -- Aucune correspondance --"
                nom_cobas = premiere_ligne.at[c_test, "Nom de l'analyse"]
                interpretation = nom_cobas.endswith(" (Interprétation)")
                nom_recherche = nom_cobas.replace(" (Interprétation)", "").strip()
                acn_trouve = get_acn_from_mapping(nom_recherche, premiere_ligne.at[c_test, "_type"])
                if acn_trouve:
                    for att in codes_mpl_attendus(acn_trouve, interpretation, acn_to_mpl):
                        if att in analyses_mpl:
                            default_match = att
                            break
                st.session_state.user_mapping[c_test] = default_match

        def update_mapping(test_name):
            st.session_state.user_mapping[test_name] = st.session_state[f"widget_{test_name}"]

        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            filtre = st.radio(
                "Filtre d'affichage des analyses :",
                ["Toutes", "🔴 À vérifier (Aucune correspondance)", "✅ Validées", "❌ Ignorées"],
                horizontal=True
            )
        with col_f2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Recalculer les liens automatiques", use_container_width=True):
                if "user_mapping" in st.session_state:
                    del st.session_state["user_mapping"]
                st.rerun()

        filtered_c_tests = []
        for c_test in analyses_cobas:
            current_val = st.session_state.user_mapping[c_test]
            if filtre == "Toutes":
                filtered_c_tests.append(c_test)
            elif filtre == "🔴 À vérifier (Aucune correspondance)" and current_val == "🔴 -- Aucune correspondance --":
                filtered_c_tests.append(c_test)
            elif filtre == "✅ Validées" and current_val not in ["🔴 -- Aucune correspondance --", "❌ -- Ignorer cette analyse --"]:
                filtered_c_tests.append(c_test)
            elif filtre == "❌ Ignorées" and current_val == "❌ -- Ignorer cette analyse --":
                filtered_c_tests.append(c_test)

        st.write(f"Affichage de **{len(filtered_c_tests)}** analyse(s) sur {len(analyses_cobas)}.")
        st.markdown("<br>", unsafe_allow_html=True)

        cols = st.columns(4)
        for i, c_test in enumerate(filtered_c_tests):
            with cols[i % 4]:
                current_val = st.session_state.user_mapping[c_test]
                try:
                    idx = analyses_mpl.index(current_val)
                except ValueError:
                    idx = 0

                st.selectbox(
                    f"🔬 {c_test}",
                    options=analyses_mpl,
                    index=idx,
                    key=f"widget_{c_test}",
                    on_change=update_mapping,
                    args=(c_test,),
                    format_func=lambda x: f"{x} ({nom_to_libellong[x]})" if x in nom_to_libellong else x
                )

        st.markdown("---")
        if st.button("✅ Générer le tableau final", type="primary", use_container_width=True):
            with st.spinner("Fusion intelligente en cours..."):
                df_c, df_m = df_cobas.copy(), df_mpl.copy()
                used_mpl_indices = set()
                indices_to_drop = []

                df_c["Nom MPL"] = ""
                df_c["Résulat MPL"], df_c["Unité MPL"] = "", ""

                for idx, row in df_c.iterrows():
                    c_test, tube = row["_cle"], str(row["Numéro de tube"])
                    m_test_choisi = st.session_state.user_mapping.get(c_test, "🔴 -- Aucune correspondance --")
                    merged = False

                    if m_test_choisi == "❌ -- Ignorer cette analyse --":
                        indices_to_drop.append(idx)
                        continue

                    if m_test_choisi and m_test_choisi != "🔴 -- Aucune correspondance --":
                        match = df_m[(df_m["Numéro de tube"].apply(lambda m: match_tubes_correct(tube, m))) & (df_m["Nom de l'analyse"] == m_test_choisi)]
                        match = match[~match.index.isin(used_mpl_indices)]
                        if not match.empty:
                            df_c.at[idx, "Nom MPL"] = match.iloc[0]["Nom de l'analyse"]
                            df_c.at[idx, "Résulat MPL"] = match.iloc[0]["Résulat MPL"]
                            df_c.at[idx, "Unité MPL"] = match.iloc[0]["Unité MPL"]
                            used_mpl_indices.add(match.index[0])
                            merged = True

                    if not merged:
                        potential_m = df_m[(df_m["Numéro de tube"].apply(lambda m: match_tubes_correct(tube, m))) & (~df_m.index.isin(used_mpl_indices))]
                        for m_idx, m_row in potential_m.iterrows():
                            if are_values_equivalent(row["Résultat CPRO"], m_row["Résulat MPL"]):
                                df_c.at[idx, "Nom MPL"] = m_row["Nom de l'analyse"]
                                df_c.at[idx, "Résulat MPL"] = m_row["Résulat MPL"]
                                df_c.at[idx, "Unité MPL"] = m_row["Unité MPL"]
                                used_mpl_indices.add(m_idx)
                                break

                df_c = df_c.drop(index=indices_to_drop)

                def get_12_digit(mpl_tube, df_cobas_ref):
                    matches = df_cobas_ref[df_cobas_ref["Numéro de tube"].apply(lambda c: match_tubes_correct(c, mpl_tube))]
                    if not matches.empty: return str(matches.iloc[0]["Numéro de tube"])
                    return str(mpl_tube) + "00" if len(str(mpl_tube)) == 10 else str(mpl_tube)

                unused_mpl = df_m.drop(index=list(used_mpl_indices)).copy()
                unused_mpl["Numéro de tube"] = unused_mpl["Numéro de tube"].apply(lambda t: get_12_digit(t, df_cobas))

                unused_mpl["Nom MPL"] = unused_mpl["Nom de l'analyse"]
                unused_mpl["Nom de l'analyse"] = ""

                # ===== Code ACN et ligne du driver de chaque ligne =====
                # Cobas : ACN de la table interne (test + type d'échantillon), puis la ligne du driver
                # qui porte le code MPL apparié, sinon celle du bon sous-champ (1 = valeur, 2 = interprétation).
                df_driver[col_acn_driver] = df_driver[col_acn_driver].apply(clean_acn)
                col_sc_driver = colonne(df_driver, "Sous-champ")
                df_c["Code ACN"], df_c["_ligne_driver"] = "", None
                for idx, row in df_c.iterrows():
                    nom_cobas = str(row["Nom de l'analyse"])
                    interpretation = nom_cobas.endswith(" (Interprétation)")
                    acn = get_acn_from_mapping(nom_cobas.replace(" (Interprétation)", "").strip(), row["_type"])
                    if not acn: continue
                    df_c.at[idx, "Code ACN"] = acn
                    lignes = df_driver[df_driver[col_acn_driver] == acn]
                    if lignes.empty: continue
                    nom_mpl = str(row["Nom MPL"]).strip()
                    if not nom_mpl:
                        # Pas de résultat MPL pour ce tube : on prend le code MPL choisi à l'étape 2 pour ce test.
                        choix_etape2 = st.session_state.user_mapping.get(row["_cle"], "")
                        if not choix_etape2.startswith(("🔴", "❌")): nom_mpl = choix_etape2
                    choix = lignes[lignes[col_nom_driver].astype(str).str.strip() == nom_mpl] if nom_mpl else lignes.iloc[0:0]
                    if choix.empty and col_sc_driver:
                        choix = lignes[lignes[col_sc_driver].apply(clean_acn) == ("2" if interpretation else "1")]
                        if choix.empty and interpretation: continue  # aucun code MPL d'interprétation pour cet ACN
                    if choix.empty: choix = lignes
                    # Plusieurs codes MPL possibles pour cet ACN et aucun code MPL connu : on ne devine pas.
                    if choix[col_nom_driver].astype(str).str.strip().nunique() > 1: continue
                    df_c.at[idx, "_ligne_driver"] = choix.index[0]
                # MPL sans résultat cobas : ACN et ligne lus directement dans le driver à partir du code MPL.
                unused_mpl["Code ACN"], unused_mpl["_ligne_driver"] = "", None
                for idx, row in unused_mpl.iterrows():
                    lignes = code_to_rows.get(str(row["Nom MPL"]).strip(), [])
                    if lignes:
                        unused_mpl.at[idx, "Code ACN"] = df_driver.at[lignes[0], col_acn_driver]
                        unused_mpl.at[idx, "_ligne_driver"] = lignes[0]

                df_combined = pd.concat([df_c, unused_mpl], ignore_index=True)

                colonnes_finales = ["Nom de l'analyse", "Nom MPL", "Numéro de tube", "Module CPRO", "Résultat CPRO", "Unité CPRO", "Facteur de conversion COBASPRO", "Résulat MPL", "Unité MPL", "Facteur de conversion MPL", "Résultat Kalisil", "Unité Kalisil", "Code ACN", "Id de l'analyse", "Sous-champ résultat", "Résultat QC", "NEGATIF/POSITIF/DOUTEUX", "Repassage"]
                df_final = pd.DataFrame(columns=colonnes_finales)
                for col in df_combined.columns:
                    if col in df_final.columns: df_final[col] = df_combined[col]

                for idx in df_final.index:
                    ligne_driver = df_combined.at[idx, "_ligne_driver"]
                    if ligne_driver is None or pd.isna(ligne_driver): continue
                    match_driver = df_driver.loc[[int(ligne_driver)]]
                    for c in match_driver.columns:
                        if "Id de l'analyse" in c: df_final.at[idx, "Id de l'analyse"] = match_driver.iloc[0][c]
                        elif "Sous-champ résultat" in c: df_final.at[idx, "Sous-champ résultat"] = match_driver.iloc[0][c]
                        elif "QC" in c: df_final.at[idx, "Résultat QC"] = match_driver.iloc[0][c]
                        elif "NEGATIF" in c or "POSITIF" in c: df_final.at[idx, "NEGATIF/POSITIF/DOUTEUX"] = match_driver.iloc[0][c]
                        elif "Repassage" in c: df_final.at[idx, "Repassage"] = match_driver.iloc[0][c]

                st.session_state.df_final = df_final
                st.session_state.etape = 3
                st.rerun()

if st.session_state.etape == 3:
    st.divider()
    st.success("✅ Fichier compilé avec succès !")

    def highlight_cells(df):
        styles = pd.DataFrame('', index=df.index, columns=df.columns)

        for idx, row in df.iterrows():
            cpro_val = str(row.get("Résultat CPRO", "")).strip()
            mpl_val = str(row.get("Résulat MPL", "")).strip()

            if cpro_val in ["", "None", "nan"] or mpl_val in ["", "None", "nan"]:
                styles.loc[idx, :] = 'background-color: #ffcccc'
                continue

            if not are_values_equivalent(cpro_val, mpl_val):
                styles.loc[idx, "Résultat CPRO"] = 'background-color: #ff99cc'
                styles.loc[idx, "Résulat MPL"] = 'background-color: #ff99cc'

            cpro_unit = str(row.get("Unité CPRO", "")).strip().lower()
            mpl_unit = str(row.get("Unité MPL", "")).strip().lower()
            empty_cpro = cpro_unit in ["", "none", "nan"]
            empty_mpl = mpl_unit in ["", "none", "nan"]

            if cpro_unit != mpl_unit and not (empty_cpro and empty_mpl):
                styles.loc[idx, "Unité CPRO"] = 'background-color: #ffe699'
                styles.loc[idx, "Unité MPL"] = 'background-color: #ffe699'

        return styles

    styled_df = st.session_state.df_final.style.apply(highlight_cells, axis=None)
    st.dataframe(styled_df, use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        styled_df.to_excel(writer, index=False, sheet_name="L3_cobaspro")
    output.seek(0)

    col_dl, col_reset = st.columns(2)
    with col_dl: st.download_button("📥 Télécharger le fichier compilé (Excel)", data=output, file_name=f"Resultats_Compiles_{VERSION}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col_reset:
        if st.button("🔄 Recommencer une nouvelle compilation"):
            st.session_state.etape = 1
            st.rerun()

if st.session_state.df_cobas is not None and st.session_state.df_mpl is not None:
    st.divider()
    with st.expander("🐛 Voir les données brutes extraites (Débogage)"):
        st.write("**Données extraites des Fichiers (Cobas) :**")
        st.dataframe(st.session_state.df_cobas.drop(columns=["_type", "_cle"], errors="ignore"), use_container_width=True)
        st.write("**Données extraites des Fichiers (MPL ou Images) :**")
        st.dataframe(st.session_state.df_mpl, use_container_width=True)
        df_nr = st.session_state.get("df_non_reconnues")
        if df_nr is not None and not df_nr.empty:
            st.write(f"**Lignes du rapport cobas non reconnues ({len(df_nr)}) :**")
            st.dataframe(df_nr, use_container_width=True)
