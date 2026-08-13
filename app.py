import streamlit as st
import pandas as pd
import pypdf
import re
import io
import math

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageOps
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

VERSION = "v5.23"

# =========================================================================
# BASE DE DONNÉES INTERNE DES CODES ACN
# =========================================================================
MAPPING_ACN = {
    "AAGP2": "20020", "AAT2": "20030", "ACET2": "20042", "ALBT2U": "20061",
    "ALB2": "20090", "ALP2": "20110", "ALTP2": "20140", "AMIK2": "20150",
    "AMPS2": "20162", "AMYL2": "20170", "APOAT": "20190", "APOBT": "20200",
    "ASLOT": "20210", "ASTP2": "20230", "B2MG": "20250", "BNZ2": "20281",
    "BILD2": "20301", "BILT3": "20312", "C3C-2": "20320", "C4-2": "20330",
    "CA2": "20341", "CARB4": "20351", "CERU": "20360", "CHE2": "20370",
    "CHOL2-I": "20411", "CK": "20420", "CL": "29250", "CL-U": "29251",
    "CO2-L": "20440", "COC2": "20451", "CREP2": "20461", "21500": "21500",
    "CRP4": "20500", "ETOH2": "20560", "FERR4": "20570", "FRA": "20580",
    "GENT2": "20591", "GGT-2": "20600", "GLUC3": "20631", "HAPT2": "20640",
    "HCYS": "20700", "HDLC4": "20710", "IGA-2": "20720", "IGG-2": "20740",
    "IGM-2": "20750", "IRON2": "20770", "K": "29240", "K-U": "29241",
    "LACT2": "20791", "LDHI2": "20811", "LDLC3": "20820", "LI": "20840",
    "LIPC": "20850", "LPA2": "20860", "MDN2": "20880", "MG2": "20891",
    "NA-U": "29231", "NH3L2": "20940", "OPI2": "20952", "PHNO2": "20970",
    "PHNY2": "20980", "PHOS2": "20990", "PHOS2 URINE": "20991", "PREA": "21010",
    "RF-II": "21040", "THC2": "21071", "TP2": "21110", "TPUC3-U": "21122",
    "TRIGL": "21130", "TRSF2": "21150", "UREAL-U": "21190", "UREAL": "21191",
    "VANC3": "21211", "AU": "21170", "ACTH": "10206", "AFP": "10209",
    "HBSAG 2": "10049", "AMHP": "10158", "ACCP": "10084",
    "AHAVIGM": "10162", "AHAV 2": "10156", "AHBC 2": "10142",
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
    "HIVAG": "11014", "HIV DUO": "12018"
}

def get_acn_from_mapping(nom_test):
    nom_upper = str(nom_test).upper().strip()
    if nom_upper in MAPPING_ACN: return MAPPING_ACN[nom_upper]
    base_name = re.sub(r'[-\s][I123]+$', '', nom_upper).strip()
    if base_name in MAPPING_ACN: return MAPPING_ACN[base_name]
    base_alpha = re.sub(r'[^A-Z0-9]', '', nom_upper)
    for k, v in MAPPING_ACN.items():
        if re.sub(r'[^A-Z0-9]', '', k) == base_alpha: return v
    return ""

def read_csv_safe(file_bytes):
    seps = [';', ',']
    encodings = ['utf-8', 'latin1', 'cp1252']
    for enc in encodings:
        for sep in seps:
            try:
                df = pd.read_csv(io.BytesIO(file_bytes), sep=sep, encoding=enc)
                if len(df.columns) > 1: return df
            except: pass
    return pd.read_csv(io.BytesIO(file_bytes), sep=';')

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
    except:
        return False

# =========================================================================

st.set_page_config(page_title=f"Compilateur Cobas & MPL {VERSION}", layout="wide")

col_vide, col_bouton = st.columns([4, 1])
with col_bouton: dark_mode = st.toggle("🌙 Mode Sombre")

css = """
<style>
[data-testid="stFileUploaderFileList"] { display: none; }
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

if "etape" not in st.session_state:
    st.session_state.etape = 1
    st.session_state.df_cobas = None
    st.session_state.df_mpl = None
    st.session_state.df_final = None

def process_files(uploaded_files, csv_bytes=None, csv_mpl_trans_bytes=None):
    cobas_records = []
    mpl_records = []
    
    mots_cles_interp = ["non réactif", "nonreac", "réactif", "reac", "douteux", "positif", "négatif"]
    unites_fausses = [
        "COI", "G/L", "MG/L", "U/L", "IU/L", "UI/L", "MIU/ML", "MUI/ML", "MUI/L",
        "MMOL/L", "MMOLE/L", "UMOLES/L", "UMOL/L", "PMOL/L", "NG/ML", "PG/ML", 
        "INDEX", "UI/ML", "IU/ML", "NG/DL", "UG/L", "MG/DL", "UG/DL", 
        "-", "TEST", "NONREAC", "NON REACTIF"
    ]
    res_pattern = r'([<>]*\s*[0-9]+[\.\,]?[0-9]*[aA]?(?:\s*<Test|\s*>Test)?|<Test|>Test|\bTest\b|\\?sup|positif|négatif|negatif|douteux|réactif|reactif|nonreac|non\s*réactif|indétectable|indetectable|En\s*cours)'
    
    vocabulaire_mpl = []
    if csv_bytes:
        df_driver_temp = read_csv_safe(csv_bytes)
        col_nom_driver = [c for c in df_driver_temp.columns if "Nom de l" in c][0]
        vocabulaire_mpl = df_driver_temp[col_nom_driver].dropna().astype(str).str.strip().unique().tolist()
        vocabulaire_mpl.sort(key=len, reverse=True)

    libellong_to_nom = {}
    if csv_mpl_trans_bytes:
        df_trans = read_csv_safe(csv_mpl_trans_bytes)
        if 'LibelLong' in df_trans.columns and 'Nom' in df_trans.columns:
            for _, row in df_trans.iterrows():
                ll = str(row['LibelLong']).strip().lower()
                nom = str(row['Nom']).strip()
                if ll and ll != 'nan':
                    libellong_to_nom[ll] = nom
    
    for uploaded_file in uploaded_files:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        
        # ================= LECTURE PDF =================
        if file_ext == 'pdf':
            reader = pypdf.PdfReader(uploaded_file)
            first_page = reader.pages[0].extract_text()
            
            if "rapport" in first_page.lower() and "résultat" in first_page.lower():
                current_id = None
                for page in reader.pages:
                    text = page.extract_text()
                    if not text: continue
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    
                    for i, line in enumerate(lines):
                        line_clean = line.replace('|', ' ').strip()
                        
                        # --- DÉTECTION DES ID COBAS ---
                        if "ID" in line_clean:
                            m_id = re.search(r'ID\s*[:]?\s*([A-Za-z0-9_]+)', line_clean)
                            if m_id and m_id.group(1).upper() not in ["ID", "RACK"]:
                                current_id = m_id.group(1)
                            else:
                                for offset in [-2, -1, 1, 2]:
                                    if 0 <= i + offset < len(lines):
                                        surr_line = lines[i+offset].replace('|', ' ').strip()
                                        m_bar = re.search(r'\b(PV[A-Za-z0-9]{5,}|\d{8,16})\b', surr_line)
                                        if m_bar:
                                            current_id = m_bar.group(1)
                                            break
                        
                        # Nettoyage de l'ID (Suppression de la séquence si collée au PV)
                        if current_id and current_id.startswith("PV") and len(current_id) >= 14:
                            current_id = re.sub(r'\d{5,6}$', '', current_id)
                        
                        # --- DÉTECTION DES RÉSULTATS COBAS ---
                        matches = list(re.finditer(r'\s+'+res_pattern+r'(?=\s|$)', line_clean, re.IGNORECASE))
                        if matches and current_id:
                            last_match = matches[-1]
                            test_name = line_clean[:last_match.start()].strip()
                            test_name = re.sub(r'^\+\s*', '', test_name).strip()
                            test_name_upper = test_name.upper()
                            
                            # --- FILTRE ANTI-DÉCHETS STRICT ---
                            is_waste = False
                            if not test_name_upper: is_waste = True
                            if "COBAS" in test_name_upper or "SYSTEM" in test_name_upper: is_waste = True
                            if re.match(r'^(R[123]|SI|SI2|S12)\b', test_name_upper): is_waste = True
                            if test_name_upper.startswith("SEQUENCE") or test_name_upper.startswith("SÉQUENCE"): is_waste = True
                            for u in unites_fausses:
                                if test_name_upper == u or test_name_upper.startswith(u + " ") or test_name_upper.startswith(u + "-"):
                                    is_waste = True
                                    break
                            
                            if not is_waste:
                                result = last_match.group(1).strip()
                                unit, module = "", ""
                                interpretation_text = None
                                
                                for j in range(1, 4):
                                    if i + j < len(lines):
                                        next_line = lines[i+j].replace('|', ' ').strip()
                                        
                                        # Sécurité : Si la ligne suivante est un VRAI test, on s'arrête.
                                        next_matches = list(re.finditer(r'\s+'+res_pattern+r'(?=\s|$)', next_line, re.IGNORECASE))
                                        if next_matches:
                                            next_test_name = next_line[:next_matches[-1].start()].strip()
                                            next_test_name_upper = re.sub(r'^\+\s*', '', next_test_name).strip().upper()
                                            is_next_waste = False
                                            for u in unites_fausses:
                                                if next_test_name_upper == u or next_test_name_upper.startswith(u + " ") or next_test_name_upper.startswith(u + "-"):
                                                    is_next_waste = True
                                                    break
                                            if not is_next_waste and "COBAS" not in next_test_name_upper and "SYSTEM" not in next_test_name_upper:
                                                break
                                                
                                        m_unit = re.match(r'^([a-zA-Z\/\%µ]+)\s+([A-Za-z0-9\-\_]+)', next_line)
                                        if m_unit and not unit:
                                            unit = m_unit.group(1).strip()
                                            module_raw = m_unit.group(2).strip()
                                            
                                            if module_raw.isdigit():
                                                module = str(int(module_raw) - 1)
                                            elif "-" in module_raw:
                                                parts = module_raw.split("-")
                                                for k in range(len(parts)):
                                                    if parts[k].isdigit():
                                                        parts[k] = str(int(parts[k]) - 1)
                                                        break
                                                module = "-".join(parts)
                                            else:
                                                module = module_raw
                                                
                                        next_line_clean = next_line.lower()
                                        if any(interp in next_line_clean for interp in mots_cles_interp) and "réanalyse" not in next_line_clean:
                                            interpretation_text = next_line.strip()
                                            
                                cobas_records.append({"Nom de l'analyse": test_name, "Numéro de tube": current_id, "Module CPRO": module, "Résultat CPRO": result, "Unité CPRO": unit})
                                if interpretation_text:
                                    cobas_records.append({"Nom de l'analyse": f"{test_name} (Interprétation)", "Numéro de tube": current_id, "Module CPRO": module, "Résultat CPRO": interpretation_text, "Unité CPRO": ""})
            else:
                tube_id = "UNKNOWN"
                for page in reader.pages:
                    page_layout = page.extract_text(extraction_mode="layout")
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
                            
                            test_name_final = libellong_to_nom.get(test_name.strip().lower(), test_name)
                            
                            res_unit_text = " ".join(parts[1:])
                            m_res = re.match(r'^'+res_pattern+r'(.*)', res_unit_text.strip(), re.IGNORECASE)
                            
                            if m_res:
                                res = m_res.group(1).strip()
                                unit_raw = m_res.group(2).strip()
                            else:
                                res = parts[1]
                                unit_raw = parts[2] if len(parts) > 2 else ""
                            
                            # Nettoyage strict de l'unité
                            unit = re.split(r'\s+(?:[0-9]|[\↑\↓\☒\个<>\~])', unit_raw)[0].strip() if unit_raw else ""
                            
                            mpl_records.append({
                                "Nom de l'analyse": test_name_final, "Numéro de tube": tube_id, "Résulat MPL": res, "Unité MPL": unit
                            })
                            
        # ================= LECTURE IMAGE AVEC PRE-TRAITEMENT =================
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
                    
            for line in lines:
                test_name_trouve = None
                reste_ligne = ""
                
                if vocabulaire_mpl:
                    for vocab in vocabulaire_mpl:
                        pattern = r'(?i)\b' + re.escape(vocab) + r'\b'
                        m_vocab = re.search(pattern, line)
                        if m_vocab:
                            test_name_trouve = vocab
                            reste_ligne = line[m_vocab.end():]
                            break
                            
                elif not test_name_trouve:
                    matches = list(re.finditer(r'\s+'+res_pattern+r'(?=\s|$)', line, re.IGNORECASE))
                    if matches:
                        last_match = matches[-1]
                        pot_name = line[:last_match.start()].strip()
                        pot_name = re.sub(r'^\+\s*', '', pot_name).strip()
                        exclusions = ["validation", "séquence", "position", "essai", "patient", "né", "edité", "prélevé", "examen", "n°", "groupe", "sexe", "tri"]
                        
                        is_waste = False
                        if not pot_name or not re.search(r'[A-Za-z]', pot_name): is_waste = True
                        if any(pot_name.lower().startswith(excl) for excl in exclusions): is_waste = True
                        if "COBAS" in pot_name.upper() or "SYSTEM" in pot_name.upper(): is_waste = True
                        for u in unites_fausses:
                            if pot_name.upper() == u or pot_name.upper().startswith(u + " ") or pot_name.upper().startswith(u + "-"):
                                is_waste = True
                                break
                        
                        if not is_waste:
                            test_name_trouve = pot_name
                            reste_ligne = line[last_match.start():]
                
                if test_name_trouve and reste_ligne:
                    m_res = re.match(r'^\s*'+res_pattern+r'(.*)', reste_ligne.strip(), re.IGNORECASE)
                    res, unit_raw = "", ""
                    if m_res:
                        res = m_res.group(1).strip()
                        unit_raw = m_res.group(2).strip()
                        if re.match(r'^[<>]?\s*\d+a$', res.lower()): res = res[:-1] + '.4'
                        elif re.match(r'^[<>]?\s*\d+[\.,]\d*a$', res.lower()): res = res[:-1] + '4'
                            
                    if res:
                        # Nettoyage strict de l'unité
                        unit = re.split(r'\s+(?:[0-9]|[\↑\↓\☒\个<>\~])', unit_raw)[0].strip() if unit_raw else ""
                        mpl_records.append({
                            "Nom de l'analyse": test_name_trouve, "Numéro de tube": tube_id, "Résulat MPL": res, "Unité MPL": unit
                        })

    df_c = pd.DataFrame(cobas_records) if cobas_records else pd.DataFrame(columns=["Nom de l'analyse", "Numéro de tube", "Module CPRO", "Résultat CPRO", "Unité CPRO"])
    df_m = pd.DataFrame(mpl_records) if mpl_records else pd.DataFrame(columns=["Nom de l'analyse", "Numéro de tube", "Résulat MPL", "Unité MPL"])
    if not df_m.empty: df_m = df_m.drop_duplicates(subset=["Nom de l'analyse", "Numéro de tube", "Résulat MPL"], keep="first").reset_index(drop=True)
    return df_c, df_m

# -------------------------------------------------------------------------------------

st.subheader("Étape 1 : Dépôt des fichiers")
uploaded_files = st.file_uploader("1️⃣ Déposez les fichiers PDF ou IMAGES (png, jpg)", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)
if uploaded_files:
    st.info(f"📂 **{len(uploaded_files)} fichier(s) prêt(s) pour l'extraction**")

col_a, col_b = st.columns(2)
with col_a:
    uploaded_csv = st.file_uploader("2️⃣ Obligatoire : Driver MPL (CSV)", type="csv")
with col_b:
    uploaded_csv_mpl = st.file_uploader("3️⃣ Optionnel : Export analyse MPL (CSV)", type="csv")

if uploaded_files and uploaded_csv:
    if st.button("📥 Extraire les données des fichiers"):
        with st.spinner("Lecture et analyse intelligente en cours..."):
            csv_mpl_bytes = uploaded_csv_mpl.getvalue() if uploaded_csv_mpl else None
            df_cobas, df_mpl = process_files(uploaded_files, uploaded_csv.getvalue(), csv_mpl_bytes)
            st.session_state.df_cobas = df_cobas
            st.session_state.df_mpl = df_mpl
            st.session_state.csv_file = uploaded_csv.getvalue() 
            st.session_state.etape = 2
            st.rerun()

if st.session_state.etape >= 2:
    st.divider()
    st.subheader("Étape 2 : Correspondance des analyses")
    st.info("🪄 **L'outil a pré-rempli les menus déroulants !** Les tests sans correspondance sont marqués par un 🔴.")
    
    df_cobas = st.session_state.df_cobas
    df_mpl = st.session_state.df_mpl
    analyses_cobas = df_cobas["Nom de l'analyse"].dropna().unique()
    
    analyses_mpl = ["🔴 -- Aucune correspondance --"] + list(df_mpl["Nom de l'analyse"].dropna().unique())
    
    df_driver = read_csv_safe(st.session_state.csv_file)
    col_acn_driver = [c for c in df_driver.columns if "Code ACN" in c][0]
    col_nom_driver = [c for c in df_driver.columns if "Nom de l" in c][0]
    
    acn_to_mpl = {}
    for _, row in df_driver.iterrows():
        acn = str(row[col_acn_driver]).strip()
        nom = str(row[col_nom_driver]).strip()
        if acn and acn != 'nan': acn_to_mpl[acn] = nom
    
    with st.form("mapping_form"):
        col1, col2 = st.columns(2)
        mappings = {}
        for i, c_test in enumerate(analyses_cobas):
            default_idx = 0
            nom_recherche = c_test.replace(" (Interprétation)", "").strip()
            acn_trouve = get_acn_from_mapping(nom_recherche)
            if acn_trouve:
                mpl_attendu = acn_to_mpl.get(acn_trouve)
                if mpl_attendu and mpl_attendu in analyses_mpl:
                    default_idx = analyses_mpl.index(mpl_attendu)
            
            with (col1 if i % 2 == 0 else col2): 
                mappings[c_test] = st.selectbox(f"🔬 Cobas : **{c_test}**", options=analyses_mpl, index=default_idx, key=f"map_{c_test}")
        
        submit_mapping = st.form_submit_button("✅ Valider et générer le tableau final", type="primary")
        
        if submit_mapping:
            with st.spinner("Fusion intelligente en cours..."):
                df_c, df_m = df_cobas.copy(), df_mpl.copy()
                used_mpl_indices = set()
                
                df_c["Nom MPL"] = ""
                df_c["Résulat MPL"], df_c["Unité MPL"] = "", ""
                
                def match_tubes(t_cobas, t_mpl):
                    tc, tm = str(t_cobas).strip(), str(t_mpl).strip()
                    if tc == tm: return True
                    if len(tc) == len(tm) + 2 and (tc[2:] == tm or tc[:-2] == tm): return True
                    return False
                
                for idx, row in df_c.iterrows():
                    c_test, tube = row["Nom de l'analyse"], str(row["Numéro de tube"])
                    m_test_choisi = mappings.get(c_test)
                    merged = False
                    
                    if m_test_choisi and m_test_choisi != "🔴 -- Aucune correspondance --":
                        match = df_m[(df_m["Numéro de tube"].apply(lambda m: match_tubes(tube, m))) & (df_m["Nom de l'analyse"] == m_test_choisi)]
                        match = match[~match.index.isin(used_mpl_indices)]
                        if not match.empty:
                            df_c.at[idx, "Nom MPL"] = match.iloc[0]["Nom de l'analyse"]
                            df_c.at[idx, "Résulat MPL"] = match.iloc[0]["Résulat MPL"]
                            df_c.at[idx, "Unité MPL"] = match.iloc[0]["Unité MPL"]
                            used_mpl_indices.add(match.index[0])
                            merged = True
                    
                    if not merged:
                        potential_m = df_m[(df_m["Numéro de tube"].apply(lambda m: match_tubes(tube, m))) & (~df_m.index.isin(used_mpl_indices))]
                        for m_idx, m_row in potential_m.iterrows():
                            if are_values_equivalent(row["Résultat CPRO"], m_row["Résulat MPL"]):
                                df_c.at[idx, "Nom MPL"] = m_row["Nom de l'analyse"]
                                df_c.at[idx, "Résulat MPL"] = m_row["Résulat MPL"]
                                df_c.at[idx, "Unité MPL"] = m_row["Unité MPL"]
                                used_mpl_indices.add(m_idx)
                                break

                def get_12_digit(mpl_tube, df_cobas_ref):
                    matches = df_cobas_ref[df_cobas_ref["Numéro de tube"].apply(lambda c: match_tubes(c, mpl_tube))]
                    if not matches.empty: return str(matches.iloc[0]["Numéro de tube"])
                    return str(mpl_tube) + "00" if len(str(mpl_tube)) == 10 else str(mpl_tube)

                unused_mpl = df_m.drop(index=list(used_mpl_indices)).copy()
                unused_mpl["Numéro de tube"] = unused_mpl["Numéro de tube"].apply(lambda t: get_12_digit(t, df_cobas))
                
                unused_mpl["Nom MPL"] = unused_mpl["Nom de l'analyse"]
                unused_mpl["Nom de l'analyse"] = ""
                
                df_combined = pd.concat([df_c, unused_mpl], ignore_index=True)
                
                colonnes_finales = ["Nom de l'analyse", "Nom MPL", "Numéro de tube", "Module CPRO", "Résultat CPRO", "Unité CPRO", "Facteur de conversion COBASPRO", "Résulat MPL", "Unité MPL", "Facteur de conversion MPL", "Résultat Kalisil", "Unité Kalisil", "Code ACN", "Id de l'analyse", "Sous-champ résultat", "Résultat QC", "NEGATIF/POSITIF/DOUTEUX", "Repassage"]
                df_final = pd.DataFrame(columns=colonnes_finales)
                for col in df_combined.columns:
                    if col in df_final.columns: df_final[col] = df_combined[col]

                df_driver[col_acn_driver] = df_driver[col_acn_driver].astype(str).str.strip()
                for idx, row in df_final.iterrows():
                    nom_cobas = str(row.get("Nom de l'analyse", "")).replace(" (Interprétation)", "").strip()
                    nom_mpl = str(row.get("Nom MPL", "")).strip()
                    nom_recherche = nom_cobas if nom_cobas else nom_mpl
                    
                    acn = get_acn_from_mapping(nom_recherche)
                    if acn:
                        df_final.at[idx, "Code ACN"] = acn
                        match_driver = df_driver[df_driver[col_acn_driver] == acn]
                        if not match_driver.empty:
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
            
            # 1. Lignes sans correspondance (Rouge clair)
            if cpro_val in ["", "None", "nan"] or mpl_val in ["", "None", "nan"]:
                styles.loc[idx, :] = 'background-color: #ffcccc'
                continue
                
            # 2. Différence de résultats (Rose vif)
            if not are_values_equivalent(cpro_val, mpl_val):
                styles.loc[idx, "Résultat CPRO"] = 'background-color: #ff99cc'
                styles.loc[idx, "Résulat MPL"] = 'background-color: #ff99cc'
            
            # 3. Unités différentes (Orange)
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

# --- FENÊTRE DE DÉBOGAGE ---
if st.session_state.df_cobas is not None and st.session_state.df_mpl is not None:
    st.divider()
    with st.expander("🐛 Voir les données brutes extraites (Débogage)"):
        st.write("**Données extraites des Fichiers (Cobas) :**")
        st.dataframe(st.session_state.df_cobas, use_container_width=True)
        st.write("**Données extraites des Fichiers (MPL ou Images) :**")
        st.dataframe(st.session_state.df_mpl, use_container_width=True)
