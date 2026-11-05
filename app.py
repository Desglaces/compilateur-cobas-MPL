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
    r'^(?:[<>]=?\s*)?-?\d+(?:[.,]\d+)?(?:[eE][+-]?\d+)?$\vert{}^\*+$|'
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
RE_COBAS_INTERP = re.compile(r'^(?:non\s*-?\s*)?reac(?:tif|tive)?$\vert{}^(?:douteux\vert{}positif\vert{}negatif\vert{}indetermine\vert{}equivoque)$')
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

css =
