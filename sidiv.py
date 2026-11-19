"""Fiche SIDIV de vérification de connexion (optionnelle).

Reproduit dans Streamlit toutes les cases de la fiche « Doc_SIDIV_Verification.pdf »
(SIDIV / SFIL, VER_CX_SGL1_INST2) et génère le PDF rempli, qui reste modifiable
(champs de formulaire conservés). Les champs « Signature » ne sont pas touchés
(à signer ensuite, par ex. via DocuSign).

Ce module est indépendant du compilateur Cobas/MPL : il n'est appelé que depuis
une section repliée en bas de page.
"""
import datetime
import io
import re
from pathlib import Path

import pandas as pd
import pypdf
import streamlit as st

MODELE = Path(__file__).with_name("Doc_SIDIV_Verification.pdf")
P = "sidiv_"  # préfixe des clés de session

# ---------------------------------------------------------------------------
# Sections 1 à 3 : (clé, libellé, nom du champ PDF, type)
#   type : "t" = texte, "a" = zone de texte, "c" = case à cocher
# ---------------------------------------------------------------------------
SEC1 = [
    ("Référent du LBM", [
        ("lbm_nom", "Nom du référent du LBM", "Text6.0", "t"),
        ("lbm_tel", "Tél", "Text6.1.0", "t"),
        ("lbm_mail", "Adresse mail", "Text6.1.1", "t")]),
    ("Intervenant S.I", [
        ("si_nom", "Nom", "Text5.0", "t"),
        ("si_tel", "Tél", "Text5.1", "t"),
        ("si_mail", "Adresse mail", "Text5.2", "t"),
        ("si_site", "Sur site", "sur site", "c"),
        ("si_tele", "En télémaintenance", "Check Box1", "c")]),
    ("Intervenant DIV", [
        ("div_nom", "Nom", "Text5.3", "t"),
        ("div_tel", "Tél", "Text5.4.0", "t"),
        ("div_mail", "Adresse mail", "Text5.4.1", "t"),
        ("div_site", "Sur site", "site_02", "c"),
        ("div_tele", "En télémaintenance", "Check Box4", "c")]),
    ("Commande et date", [
        ("commande", "Numéro de commande", "Text5.4.3", "t"),
        ("date_verif", "Date de la vérification de la connexion", "Text5.4.2.0", "t")]),
]
SEC2 = [
    ("Périmètre de la validation", [
        ("automate", "Automate (instrument) – choisir dans la liste ou saisir manuellement",
         "Text5.4.2.1.0", "s"),
        ("fournisseur", "Fournisseur", "Text5.4.2.1.1.0", "t"),
        ("v_automate", "Version logiciel de l'automate", "Text5.4.2.1.1.1", "t"),
        ("v_driver_auto", "Version driver de connexion de l'automate", "Text5.4.2.1.1.2", "t"),
        ("v_mw", "Version logiciel du MW", "Text5.4.2.1.1.3", "t"),
        ("v_sgl", "Version logiciel du SGL", "Text5.4.2.1.1.4", "t"),
        ("v_driver_cx", "Version logiciel du « driver de connexion » côté SGL/MW", "Text5.4.2.1.1.5", "t"),
        ("protocole", "Protocole de référence (spécification fournisseur instrument)", "Text5.4.2.1.1.6", "t"),
        ("ref_valid", "Référence du document de validation inter-fournisseurs (si existant)", "Text5.4.2.1.1.7.0.0", "t"),
        ("cadre", "Cadre général / description du mode opératoire « Autre »  "
                  "(dans le modèle SIDIV, ces deux zones sont un seul champ)", "Text5.4.2.1.1.7.0.1", "a")]),
    ("Mode opératoire de la validation", [
        ("m_dossiers", "Utilisation de dossiers", "Check Box2.0.0", "c"),
        ("m_base", "Utilisation d'une base de test", "Check Box2.1.0", "c"),
        ("m_autre", "Autre", "Check Box2.0.1", "c")]),
]
SEC3 = [
    ("3.1 Principe de fonctionnement", [
        ("p_mono_sgl", "Mono SGL/MW → Instrument", "Check Box3.0", "c"),
        ("p_mono_inst", "Mono Instrument → SGL/MW", "Check Box3.1", "c"),
        ("p_bidi_interro", "Bidi mode interrogatif", "Check Box3.2", "c"),
        ("p_bidi_charg", "Bidi mode chargement", "Check Box3.3.1", "c"),
        ("p_bidi_mixte", "Bidi mode mixte (interrogatif pour les demandes, chargement pour les repasses)",
         "Check Box3.3.0.0", "c")]),
    ("3.2 Format", [
        ("f_astm", "ASTM", "Check Box3.3.0.2", "c"),
        ("f_hprim", "Hprim", "Check Box3.3.0.3", "c"),
        ("f_hl7", "HL7", "Check Box3.3.0.4", "c"),
        ("f_ihe", "Profil IHE LAW", "Check Box3.3.0.5", "c"),
        ("f_prop", "Propriétaire", "Check Box3.3.0.6.0", "c")]),
    ("3.3 Mode de communication", [
        ("c_serie", "Série", "Check Box3.3.0.6.1", "c"),
        ("c_fichiers", "Transfert de fichiers", "Check Box3.3.0.6.2.0", "c"),
        ("c_ftp", "   ↳ FTP", "Check Box3.3.0.6.2.4", "c"),
        ("c_autre", "   ↳ Autre mode", "Check Box3.3.0.6.2.2", "c"),
        ("c_semaphore", "   ↳ Avec sémaphore", "Check Box3.3.0.6.2.3", "c"),
        ("c_socket", "Socket", "Check Box3.3.0.6.2.1.0.0", "c"),
        ("c_1socket", "   ↳ 1 socket", "Check Box3.3.0.6.2.1.1.0", "c"),
        ("c_nsocket", "   ↳ Plus d'un socket", "Check Box3.3.0.6.2.1.1.1", "c"),
        ("c_expl", "Expliquer le mode de fonctionnement (plus d'un socket)", "Text11", "a"),
        ("c_cli_srv", "SGL/MW Client – Instrument Serveur", "Check Box3.3.0.6.2.5", "c"),
        ("c_srv_cli", "SGL/MW Serveur – Instrument client", "Check Box3.3.0.6.2.6", "c"),
        ("c_srv_dem", "SGL/MW Serveur pour les demandes – Client pour les résultats",
         "Check Box3.3.0.6.2.7", "c"),
        ("c_cli_dem", "SGL/MW Client pour les demandes – Serveur pour les résultats",
         "Check Box3.3.0.6.2.8", "c"),
        ("c_images", "Mode de communication pour les images – zone explicative", "Text1", "a")]),
]
SEC_REM = [
    ("Zones de remarques (page 6)", [
        ("rem_lbm", "Zone remarque LBM", "Text4.1.1", "a"),
        ("rem_si", "Zone remarque S.I", "Text4.1.0", "a"),
        ("rem_div", "Zone remarque DIV", "Text4.0", "a")]),
    ("Dates de signature (les signatures elles-mêmes restent à faire sur le PDF)", [
        ("date_lbm", "Date – Le LBM", "Text7.0.0", "t"),
        ("date_si", "Date – Intervenant S.I", "Text7.1.1", "t"),
        ("date_div", "Date – Intervenant DIV", "Text7.1.0", "t")]),
]
TOUS_CHAMPS = [c for sec in (SEC1, SEC2, SEC3, SEC_REM) for _, lst in sec for c in lst]

# Champs « enfants » (flèche ↳ dans la fiche) : affichés sous leur parent, seulement si celui-ci est coché.
PARENT = {
    "c_ftp": "c_fichiers", "c_autre": "c_fichiers", "c_semaphore": "c_fichiers",
    "c_1socket": "c_socket", "c_nsocket": "c_socket",
    "c_expl": "c_nsocket",
}
ENFANTS = {}
for _enfant, _parent in PARENT.items():
    ENFANTS.setdefault(_parent, []).append(_enfant)

OPTIONS_AUTOMATE = ["Cobas pro", "Cobas pure"]

# Valeurs pré-remplies à l'ouverture (modifiables)
DEFAUTS = {
    "automate": "Cobas pro",
    "fournisseur": "ROCHE",
    "m_dossiers": True,        # utilisation de dossiers
    "p_bidi_interro": True,    # 3.1 bidi mode interrogatif
    "f_hl7": True,             # 3.2 HL7
    "c_socket": True,          # 3.3 socket
    "c_1socket": True,         #     1 socket
    "c_srv_cli": True,         #     SGL/MW Serveur – Instrument client
}


def analyser_nom_csv(nom):
    """Déduit automate et version du driver du nom du CSV d'analyses (Driver Manager),
    ex. « cobaspro-258-v3.21.0.6739-Analyses.csv » -> ("Cobas pro", "3.21.0.6739")."""
    nom = str(nom or "")
    bas = nom.lower()
    automate = "Cobas pure" if "pure" in bas else ("Cobas pro" if "pro" in bas else None)
    m = re.search(r"-v(\d+(?:\.\d+)+)", nom, flags=re.IGNORECASE)
    return automate, (m.group(1) if m else None)

# ---------------------------------------------------------------------------
# Section 4 : grille de tests (Réf. dossier test / Tr / NA / T / OK / NOK / Commentaires)
# ---------------------------------------------------------------------------
COLS_CASES = ["Tr", "NA", "T", "OK", "NOK"]
C_REF, C_COM, C_LIB = "Réf. dossier test", "Commentaires", "Test"

# Cases pré-cochées par grille (indices de lignes) : "TrT" = Transmis + Testé ; "NA" = sans objet.
# 4.1 : IPP … Sexe testés ; « Renseignements permanents » et « Traitement patient » NA.
# 4.2 : N° échantillon, Analyse/test, Urgence testés ; toutes les autres lignes NA.
# 4.3 : valeur brute, seuils, horodatage mesure, position échantillon, identification instrument,
#       valeurs CQ testés ; unités NA ; de « Identification opérateur » à « Graphiques » NA ;
#       les 3 lignes après « Valeurs CQ » et les 2 dernières (maintenance, autres champs) NA.
#       (« valeur interprétée » est laissée vide.)
#       « valeurs alphanumériques » (index 3) est coché seulement si un dossier MPL adapté existe.
TR_T = {"41": list(range(7)), "42": [0, 1, 4], "43": [0, 2, 5, 6, 7, 21]}
NA_PAR_DEFAUT = {"41": [7, 8],
                 "42": [i for i in range(18) if i not in (0, 1, 4)],
                 "43": [4] + list(range(8, 21)) + [22, 23, 24, 25, 26]}
# Lignes qui reçoivent un n° de dossier issu de l'extraction (un dossier différent par ligne)
LIGNES_AVEC_DOSSIER = [("41", i) for i in range(7)] + [("42", i) for i in (0, 1, 4)]
IDX_43_BRUT, IDX_43_SEUILS, IDX_43_ALPHA = 0, 2, 3


def tubes_dossiers_tests(df_cobas=None, df_mpl=None):
    """N° de dossiers tests à proposer : ceux présents à la fois dans le rapport Cobas et dans les
    PDF MPL (ce sont les dossiers réellement suivis de bout en bout), triés. À défaut (un seul des
    deux côtés extrait), tous les tubes connus."""
    def tubes(df):
        if df is None or "Numéro de tube" not in getattr(df, "columns", []):
            return []
        return list(dict.fromkeys(str(t).strip() for t in df["Numéro de tube"].dropna() if str(t).strip()))
    c, m = tubes(df_cobas), tubes(df_mpl)
    communs = [t for t in c if t in set(m)]
    return sorted(communs or dict.fromkeys(c + m))


def dossiers_mpl(df_mpl):
    """Cherche dans l'extraction MPL un dossier avec un résultat à seuil (commençant par < ou >)
    et un dossier avec un résultat alphanumérique (texte, hors indices sérum H/I/L).
    Retourne (dossier_seuil, dossier_alpha), None si absent."""
    seuil = alpha = None
    try:
        col = "Résulat MPL"
        if df_mpl is None or df_mpl.empty or col not in df_mpl.columns:
            return None, None
        for _, row in df_mpl.iterrows():
            tube, res = str(row.get("Numéro de tube", "")).strip(), str(row[col]).strip()
            if not tube or not res or res.lower() == "nan":
                continue
            if res[0] in "<>":
                seuil = seuil or tube
                continue
            try:
                float(res.replace(",", "."))
                continue  # numérique
            except ValueError:
                pass
            nom = str(row.get("Nom de l'analyse", ""))
            if re.search(r"[A-Za-zÀ-ÿ]", res) and not re.match(r"^[HIL] ?\w{1,3}$", nom.strip()):
                alpha = alpha or tube
            if seuil and alpha:
                break
    except Exception:
        pass
    return seuil, alpha

L41 = ["IPP", "Nom usuel", "Prénom", "Nom de naissance", "Civilité", "Date de naissance", "Sexe",
       "Renseignements permanents", "Traitement patient"]
L42 = ["N° échantillon", "Analyse/test", "Antériorités analyse/test", "Transmission d'un résultat",
       "Urgence", "Urgence Vitale", "Horodatage prélèvement", "Préleveur",
       "Renseignements liés à la demande", "Médecin prescripteur", "Service", "Correspondant(s)",
       "Date d'hospitalisation", "N° de chambre", "Gestion des demandes de repasse (rerun)",
       "Ajout d'analyse/test sur SGL/MW", "Suppression d'analyse/test sur SGL/MW",
       "URL de documents associés à la demande"]
L43 = ["Intégration de la valeur « brute » (1)", "Intégration de la valeur interprétée",
       "Intégration des seuils (ex : <0.10)", "Intégration des valeurs alphanumériques",
       "Intégration des unités", "Horodatage de la mesure", "Position de l'échantillon sur l'instrument",
       "Identification Instrument", "Identification opérateur sur l'instrument", "N° lots réactifs",
       "Date péremption lot réactif", "Inventaires lots réactifs", "N° de série du réactif (cassette)",
       "N° de lot de calibrants", "Informations consommables (2)", "Alarmes analytiques, Flag (3)",
       "Commentaires « textes codés »", "Commentaires « libres »",
       "Commentaires associés à l'échantillon", "Commentaires associés aux analyses/tests",
       "Graphiques (images, courbes)", "Valeurs CQ", "N° de lots de CQ",
       "Date de péremption lot de CQ", "Intégration des analyses non demandées",
       "Informations de maintenance (4)", "Autres champs (5)"]

# Correspondance ligne -> champs PDF (générée depuis la géométrie du formulaire).
# refs : champ(s) « Réf. dossier test » ; com : champ « Commentaires » ; puis une case par colonne.
G41 = [
    {'refs': ['Text3.0.0'], 'com': 'Text2.0', 'Tr': 'Check Box5.0', 'NA': 'Check Box5.2', 'T': 'Check Box5.3', 'OK': 'Check Box5.4', 'NOK': 'Check Box5.5'},
    {'refs': ['Text3.0.1'], 'com': 'Text2.1', 'Tr': 'Check Box5.1.0', 'NA': 'Check Box5.1.1', 'T': 'Check Box5.1.2', 'OK': 'Check Box5.1.3', 'NOK': 'Check Box5.1.9.1.1'},
    {'refs': ['Text3.0.2'], 'com': 'Text2.2', 'Tr': 'Check Box5.1.4', 'NA': 'Check Box5.1.9.0.0', 'T': 'Check Box5.1.10', 'OK': 'Check Box5.1.9.0.1', 'NOK': 'Check Box5.1.9.1.0'},
    {'refs': ['Text3.0.3'], 'com': 'Text2.3', 'Tr': 'Check Box5.1.5', 'NA': 'Check Box5.1.9.3.0', 'T': 'Check Box5.1.9.3.1', 'OK': 'Check Box5.1.9.2.1', 'NOK': 'Check Box5.1.9.2.0'},
    {'refs': ['Text3.0.4'], 'com': 'Text2.4', 'Tr': 'Check Box5.1.6', 'NA': 'Check Box5.1.9.4.0.0.0', 'T': 'Check Box5.1.9.4.1', 'OK': 'Check Box5.1.9.4.0.0.4', 'NOK': 'Check Box5.1.9.5.0'},
    {'refs': ['Text3.0.5'], 'com': 'Text2.5', 'Tr': 'Check Box5.1.7', 'NA': 'Check Box5.1.9.4.0.0.1', 'T': 'Check Box5.1.9.4.0.1.4', 'OK': 'Check Box5.1.9.4.0.0.3.0.0', 'NOK': 'Check Box5.1.9.4.0.0.3.0.1'},
    {'refs': ['Text3.0.6'], 'com': 'Text2.6', 'Tr': 'Check Box5.1.8', 'NA': 'Check Box5.1.9.4.0.1.2', 'T': 'Check Box5.1.9.4.0.1.5', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.0', 'NOK': 'Check Box5.1.9.4.0.0.3.1.1'},
    {'refs': ['Text3.0.7'], 'com': 'Text2.7', 'Tr': 'Check Box5.1.9.4.0.1.0', 'NA': 'Check Box5.1.9.4.0.0.2', 'T': 'Check Box5.1.9.4.0.0.5', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.0.1', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.0.0'},
    {'refs': ['Text3.0.8.0.0'], 'com': 'Text2.8', 'Tr': 'Check Box5.1.9.4.0.1.1', 'NA': 'Check Box5.1.9.4.0.1.3', 'T': 'Check Box5.1.9.5.1', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.1.1', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.1.0'},
]
G42 = [
    {'refs': ['Text3.0.8.1.0.0.0'], 'com': 'Text3.0.8.1.0.0.1.0', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.0.0', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.0.1', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.0.1', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.0.0', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.1'},
    # (le modèle a ici 2 champs superposés ; on garde celui qui est aligné dans la cellule)
    {'refs': ['Text3.0.8.1.1'], 'com': 'Text3.0.8.1.0.0.1.1', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.0.0', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.2', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.1.0', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.1.1', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.1'},
    {'refs': ['Text3.0.8.0.1.0'], 'com': 'Text3.0.8.1.0.0.1.2', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.3', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.0.0', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.0.3', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.0.4', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.4'},
    {'refs': ['Text3.0.8.0.1.1'], 'com': 'Text3.0.8.1.0.0.1.4', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.0.3', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.0.4', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.1', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.0.2', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.0'},
    {'refs': ['Text3.0.8.0.1.3'], 'com': 'Text3.0.8.1.0.0.1.5', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.0', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.0.1', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.0.2', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.0.3', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.0.5'},
    {'refs': ['Text3.0.8.0.1.4'], 'com': 'Text3.0.8.1.0.0.1.6', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.4', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.0.1', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.1', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.2', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.0.2'},
    {'refs': ['Text3.0.8.0.1.5'], 'com': 'Text3.0.8.1.0.0.1.8', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.0', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.5', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.3', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.2', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.1'},
    {'refs': ['Text3.0.8.0.1.7'], 'com': 'Text3.0.8.1.0.0.1.9', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.4', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.3', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.2', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.1', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.7'},
    {'refs': ['Text3.0.8.0.1.8'], 'com': 'Text3.0.8.1.0.0.1.11', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.5', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.6', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.7', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.8', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.9'},
    {'refs': ['Text3.0.8.0.1.9'], 'com': 'Text3.0.8.1.0.0.1.12', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.0.0', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.2.0', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.1.0', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.1.1', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.0.1'},
    {'refs': ['Text3.0.8.0.1.10'], 'com': 'Text3.0.8.1.0.0.1.13', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.4.1', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.4.0', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.3.0', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.3.1', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.2.1'},
    {'refs': ['Text3.0.8.0.1.11'], 'com': 'Text3.0.8.1.0.0.1.14', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.6.0', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.7.1', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.6.1', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.5.1', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.5.0'},
    {'refs': ['Text3.0.8.0.1.12'], 'com': 'Text3.0.8.1.0.0.1.15', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.7.0', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.8.0', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.8.1', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.9.1', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.1'},
    {'refs': ['Text3.0.8.0.1.13'], 'com': 'Text3.0.8.1.0.0.1.16', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.6.0', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.0.0', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.0.1', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.9.0', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.1.0'},
    {'refs': ['Text3.0.8.0.1.14'], 'com': 'Text3.0.8.1.0.0.1.17', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.2.0', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.1.1', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.2.1', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.3.1', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.5.1'},
    {'refs': ['Text3.0.8.0.1.15'], 'com': 'Text3.0.8.1.0.0.1.18', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.3.0', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.4.0', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.5.0', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.4.1', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.6.1.0.0'},
    {'refs': ['Text3.0.8.0.1.16'], 'com': 'Text3.0.8.1.0.0.1.19', 'Tr': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.6.1.1.0.1.0', 'NA': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.6.1.1.0.1.1', 'T': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.6.1.1.0.0.0', 'OK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.6.1.0.1', 'NOK': 'Check Box5.1.9.4.0.0.3.1.0.0.1.1.0.1.1.0.0.1.3.1.0.6.10.10.0.6.1.1.1'},
    {'refs': [], 'com': 'Text9', 'Tr': 'Check Box10.0', 'NA': 'Check Box10.1', 'T': 'Check Box10.2', 'OK': 'Check Box10.3', 'NOK': 'Check Box10.4'},
]
G43 = [
    {'refs': ['Text14.0'], 'com': 'Text13.0', 'Tr': 'Check Box10.9', 'NA': 'Check Box10.8', 'T': 'Check Box10.7', 'OK': 'Check Box10.6', 'NOK': 'Check Box10.5'},
    {'refs': ['Text14.1.0.0'], 'com': 'Text13.1', 'Tr': 'Check Box10.10', 'NA': 'Check Box10.11', 'T': 'Check Box10.12', 'OK': 'Check Box10.13', 'NOK': 'Check Box10.14'},
    {'refs': ['Text14.1.1.0'], 'com': 'Text13.2.0', 'Tr': 'Check Box10.15.0.0.0', 'NA': 'Check Box10.16.0.0.0', 'T': 'Check Box10.16.0.1.0', 'OK': 'Check Box10.15.1.1.0', 'NOK': 'Check Box10.16.1.1.0'},
    {'refs': ['Text14.1.1.1'], 'com': 'Text13.2.1', 'Tr': 'Check Box10.15.0.0.1.0', 'NA': 'Check Box10.16.0.0.1.0', 'T': 'Check Box10.16.0.1.1.0', 'OK': 'Check Box10.15.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.0'},
    {'refs': ['Text14.2'], 'com': 'Text13.2.2', 'Tr': 'Check Box10.15.0.0.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.0', 'T': 'Check Box10.16.0.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.0'},
    {'refs': ['Text14.3'], 'com': 'Text13.3', 'Tr': 'Check Box10.15.0.0.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.0'},
    {'refs': ['Text14.4'], 'com': 'Text13.4', 'Tr': 'Check Box10.15.0.0.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.0'},
    {'refs': ['Text14.5'], 'com': 'Text13.5', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.6'], 'com': 'Text13.6', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.7'], 'com': 'Text13.7', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.8'], 'com': 'Text13.8', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.9'], 'com': 'Text13.9', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.10'], 'com': 'Text13.10', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.11'], 'com': 'Text13.11', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.12'], 'com': 'Text13.12', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.13'], 'com': 'Text13.13', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.14'], 'com': 'Text13.14', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.15'], 'com': 'Text13.15', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.16'], 'com': 'Text13.16', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.17'], 'com': 'Text13.17', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.18'], 'com': 'Text13.18', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.19'], 'com': 'Text13.19', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.0'},
    {'refs': ['Text14.20'], 'com': 'Text13.20', 'Tr': 'Check Box10.15.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1', 'NA': 'Check Box10.16.0.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1', 'T': 'Check Box10.16.0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1', 'OK': 'Check Box10.15.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1', 'NOK': 'Check Box10.16.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1'},
    {'refs': ['Text10.0.1.0.0'], 'com': 'Text10.0.0', 'Tr': 'Check Box6.0.0.0', 'NA': 'Check Box6.1.0.0', 'T': 'Check Box6.1.1.0', 'OK': 'Check Box6.1.2.0', 'NOK': 'Check Box6.0.2.0'},
    {'refs': ['Text10.0.1.1.0'], 'com': 'Text10.1.0', 'Tr': 'Check Box6.0.0.1.0', 'NA': 'Check Box6.1.0.1.0', 'T': 'Check Box6.1.1.1.0', 'OK': 'Check Box6.1.2.1.0', 'NOK': 'Check Box6.0.2.1.0'},
    {'refs': ['Text10.0.1.1.1'], 'com': 'Text10.1.1.0', 'Tr': 'Check Box6.0.0.1.1.0', 'NA': 'Check Box6.1.0.1.1.0', 'T': 'Check Box6.1.1.1.1.0', 'OK': 'Check Box6.1.2.1.1.0', 'NOK': 'Check Box6.0.2.1.1.0'},
    {'refs': ['Text10.0.1.0.1'], 'com': 'Text10.1.1.1', 'Tr': 'Check Box6.0.0.1.1.1', 'NA': 'Check Box6.1.0.1.1.1', 'T': 'Check Box6.1.1.1.1.1', 'OK': 'Check Box6.1.2.1.1.1', 'NOK': 'Check Box6.0.2.1.1.1'},
]

GRILLES = [
    dict(id="41", titre="4.1 Informations patients (SGL/MW → Instrument)", labels=L41, rows=G41,
         notes=[("Text12", "Vérifier le renvoi vers l'instrument des informations modifiées. "
                           "Noter les particularités")]),
    dict(id="42", titre="4.2 Informations liées à la demande (SGL/MW → DIV)", labels=L42, rows=G42,
         notes=[("Text8", "Vérifier le renvoi vers l'instrument des informations modifiées. "
                          "Noter les particularités"),
                ("Text15", "Zone commentaires additionnels (4.2)")]),
    dict(id="43", titre="4.3 Résultats (DIV → SGL/MW)", labels=L43, rows=G43,
         notes=[("Text16", "Zone commentaires additionnels (4.3)")]),
]
assert all(len(g["labels"]) == len(g["rows"]) for g in GRILLES)


# ---------------------------------------------------------------------------
# Génération du PDF
# ---------------------------------------------------------------------------
def remplir_pdf(textes, cases, modele=MODELE):
    """Remplit le formulaire. textes : {champ: valeur} ; cases : ensemble de champs à cocher.
    Les champs vides sont laissés tels quels. Le PDF reste un formulaire modifiable."""
    valeurs = {n: str(v) for n, v in textes.items() if v is not None and str(v).strip() != ""}
    valeurs.update({n: "/Yes" for n in cases})
    writer = pypdf.PdfWriter(clone_from=pypdf.PdfReader(str(modele)))
    for page in writer.pages:
        if "/Annots" in page:  # la page 1 n'a aucun champ
            writer.update_page_form_field_values(page, valeurs, auto_regenerate=False)
    writer.set_need_appearances_writer(True)  # le lecteur PDF régénère l'affichage
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Interface Streamlit
# ---------------------------------------------------------------------------
def _df_vide(g):
    d = pd.DataFrame({C_LIB: g["labels"], C_REF: ""})
    for c in COLS_CASES:
        d[c] = False
    d[C_COM] = ""
    for i in TR_T.get(g["id"], []):
        d.loc[i, ["Tr", "T"]] = True
    for i in NA_PAR_DEFAUT.get(g["id"], []):  # NA : case cochée, rien écrit dans la réf.
        d.loc[i, "NA"] = True
    return d


def _courant(g):
    return st.session_state.get(f"{P}cur_{g['id']}", st.session_state[f"{P}base_{g['id']}"])


def _modifier(g, fn):
    """Modifie la grille (en conservant la saisie en cours) et force la ré-initialisation de l'éditeur."""
    d = _courant(g).copy()
    fn(d)
    st.session_state[f"{P}base_{g['id']}"] = d
    st.session_state[f"{P}ver_{g['id']}"] += 1


def _tout_cocher(g):
    def f(d):
        for c in ("Tr", "T", "OK"):
            d[c] = True
        for c in ("NA", "NOK"):
            d[c] = False
    _modifier(g, f)


def _tout_vider(g):
    def f(d):
        for c in COLS_CASES:
            d[c] = False
    _modifier(g, f)


def _appliquer_ref():
    ref = str(st.session_state.get(f"{P}ref_globale") or "").strip()
    if not ref:
        return
    for g in GRILLES:
        def f(d, ref=ref):
            d.loc[d[C_REF].fillna("").str.strip() == "", C_REF] = ref
        _modifier(g, f)


def _champ(c):
    cle, label, _, kind = c
    k = P + cle
    if kind == "c":
        st.checkbox(label, key=k)
    elif kind == "a":
        st.text_area(label, key=k, height=90)
    elif kind == "s":  # liste déroulante avec saisie libre possible
        st.selectbox(label, OPTIONS_AUTOMATE, key=k, accept_new_options=True)
    else:
        st.text_input(label, key=k)


def _afficher(c, par_cle):
    """Affiche un champ puis, s'il est coché, ses champs « enfants » en dessous (indentés)."""
    _champ(c)
    enfants = ENFANTS.get(c[0], [])
    if enfants and st.session_state.get(P + c[0]):
        _, col = st.columns([1, 14])
        with col:
            for e in enfants:
                _afficher(par_cle[e], par_cle)


def _bloc(sections):
    par_cle = {c[0]: c for c in TOUS_CHAMPS}
    for titre, champs in sections:
        st.markdown(f"**{titre}**")
        for c in champs:
            if c[0] not in PARENT:  # les enfants sont affichés sous leur parent
                _afficher(c, par_cle)


def _grille(g):
    st.markdown(f"**{g['titre']}**")
    b1, b2, _ = st.columns([1, 1, 2])
    b1.button("✅ Tout : Tr + T + OK", key=f"{P}ok_{g['id']}", on_click=_tout_cocher, args=(g,),
              width="stretch")
    b2.button("↺ Décocher tout", key=f"{P}rz_{g['id']}", on_click=_tout_vider, args=(g,),
              width="stretch")
    cfg = {C_LIB: st.column_config.TextColumn(C_LIB, disabled=True, width="medium"),
           C_REF: st.column_config.TextColumn(C_REF, width="small"),
           C_COM: st.column_config.TextColumn(C_COM, width="medium")}
    for c in COLS_CASES:
        cfg[c] = st.column_config.CheckboxColumn(c, width="small")
    gid = g["id"]
    version = st.session_state[P + "ver_" + gid]
    edite = st.data_editor(st.session_state[P + "base_" + gid], column_config=cfg, hide_index=True,
                           width="stretch", num_rows="fixed",
                           key=P + "ed_" + gid + "_" + str(version))
    st.session_state[f"{P}cur_{g['id']}"] = edite
    for nom, label in g["notes"]:
        st.text_area(label, key=f"{P}note_{nom}", height=80)


def _actif(cle):
    """Un champ enfant n'est pris en compte que si toute sa chaîne de parents est cochée."""
    parent = PARENT.get(cle)
    while parent:
        if not st.session_state.get(P + parent):
            return False
        parent = PARENT.get(parent)
    return True


def _collecter():
    textes, cases = {}, set()
    for cle, _, nom, kind in TOUS_CHAMPS:
        if not _actif(cle):
            continue
        v = st.session_state.get(P + cle)
        if kind == "c":
            if v:
                cases.add(nom)
        elif v is not None and str(v).strip():
            textes[nom] = v
    for g in GRILLES:
        d = _courant(g)
        for (_, row), spec in zip(d.iterrows(), g["rows"]):
            for c in COLS_CASES:
                if bool(row[c]):
                    cases.add(spec[c])
            ref = str(row[C_REF] or "").strip()
            for nom in spec["refs"]:
                if ref:
                    textes[nom] = ref
            com = str(row[C_COM] or "").strip()
            if spec["com"] and com:
                textes[spec["com"]] = com
        for nom, _ in g["notes"]:
            v = st.session_state.get(f"{P}note_{nom}")
            if v and str(v).strip():
                textes[nom] = v
    return textes, cases


def _init(tubes):
    if f"{P}init" in st.session_state:
        return
    st.session_state[f"{P}init"] = True
    st.session_state[P + "date_verif"] = datetime.date.today().strftime("%d/%m/%Y")
    for cle, valeur in DEFAUTS.items():
        st.session_state[P + cle] = valeur
    for g in GRILLES:
        st.session_state[f"{P}base_{g['id']}"] = _df_vide(g)
        st.session_state[f"{P}ver_{g['id']}"] = 0


def _prefill_extraction(tubes, nom_csv, df_mpl=None):
    """Pré-remplit à partir de ce que l'outil a extrait (sans écraser une saisie de l'utilisateur) :
    - réf. dossier test (n° de tubes) dans les grilles 4.1 / 4.2, en proposition globale, et
      dossiers MPL à seuil / alphanumérique en 4.3 ;
    - automate et version du driver, d'après le nom du CSV d'analyses de l'étape 2."""
    if tubes and st.session_state.get(P + "tubes_vus") != tubes:
        st.session_state[P + "tubes_vus"] = tubes
        if not str(st.session_state.get(P + "ref_globale") or "").strip():
            st.session_state[P + "ref_globale"] = tubes[0]
        seuil, alpha = dossiers_mpl(df_mpl)
        for g in GRILLES:
            def f(d, g=g):
                # un n° de dossier différent par ligne testée (on boucle s'il y en a moins que de lignes)
                for k, (gid, i) in enumerate(LIGNES_AVEC_DOSSIER):
                    if gid == g["id"] and not str(d.loc[i, C_REF] or "").strip():
                        d.loc[i, C_REF] = tubes[k % len(tubes)]
                if g["id"] == "43":
                    if seuil and not str(d.loc[IDX_43_SEUILS, C_REF] or "").strip():
                        d.loc[IDX_43_SEUILS, C_REF] = seuil
                    if alpha:  # sinon : on ne coche rien pour les valeurs alphanumériques
                        if not str(d.loc[IDX_43_ALPHA, C_REF] or "").strip():
                            d.loc[IDX_43_ALPHA, C_REF] = alpha
                        d.loc[IDX_43_ALPHA, ["Tr", "T"]] = True
            _modifier(g, f)
    if nom_csv and st.session_state.get(P + "csv_vu") != nom_csv:
        st.session_state[P + "csv_vu"] = nom_csv
        automate, version = analyser_nom_csv(nom_csv)
        if automate:
            st.session_state[P + "automate"] = automate
        if version:
            st.session_state[P + "v_driver_auto"] = version


def afficher_section_sidiv(tubes=None, nom_csv_driver=None, df_mpl=None):
    """Section optionnelle (repliée) : saisie de la fiche SIDIV et génération du PDF modifiable.

    tubes          : liste facultative de n° de tubes/dossiers détectés par le compilateur
                     (proposés comme « Réf. dossier test »).
    nom_csv_driver : nom du CSV d'analyses (Driver Manager) déposé à l'étape 2, d'où l'on déduit
                     l'automate et la version du driver.
    df_mpl         : extraction MPL (pour trouver un dossier à seuil < / > et un dossier alphanumérique)."""
    tubes = [str(t) for t in (tubes or []) if str(t).strip()]
    with st.expander("📝 Fiche SIDIV – Vérification de connexion (optionnel)", expanded=False):
        if not MODELE.exists():
            st.error(f"Modèle introuvable : {MODELE.name}")
            return
        _init(tubes)
        _prefill_extraction(tubes, nom_csv_driver, df_mpl)
        st.caption("Facultatif : indépendant du compilateur ci-dessus. Remplissez ce que vous voulez, "
                   "puis générez le PDF : il reste modifiable (champs de formulaire) et les signatures "
                   "restent à faire.")
        t1, t2, t3, t4, t5 = st.tabs(["1. Informations générales", "2. Périmètre",
                                      "3. Description de la connexion", "4. Tests effectués",
                                      "Remarques & dates"])
        with t1:
            _bloc(SEC1)
        with t2:
            _bloc(SEC2)
        with t3:
            _bloc(SEC3)
        with t4:
            st.caption("Légende : Tr = Transmis / NA = Non applicable / T = Testé / OK = Test OK / "
                       "NOK = Test non OK")
            if tubes:
                st.info("Dossiers tests détectés dans l'extraction : " + ", ".join(tubes[:12])
                        + (" …" if len(tubes) > 12 else ""))
            c1, c2 = st.columns([3, 1])
            c1.text_input("Réf. dossier test à reporter sur les lignes vides", key=P + "ref_globale",
                          help="Par ex. le n° de tube / dossier test utilisé pour la vérification.")
            c2.button("Appliquer", on_click=_appliquer_ref, width="stretch")
            for g in GRILLES:
                _grille(g)
        with t5:
            _bloc(SEC_REM)

        st.divider()
        if st.button("📄 Générer la fiche SIDIV (PDF modifiable)", type="primary", key=P + "gen"):
            try:
                textes, cases = _collecter()
                st.session_state[P + "pdf"] = remplir_pdf(textes, cases)
            except Exception as e:  # ne doit jamais gêner le reste de l'outil
                st.session_state.pop(P + "pdf", None)
                st.error(f"Échec de la génération de la fiche SIDIV : {e}")
        if st.session_state.get(P + "pdf"):
            suffixe = str(st.session_state.get(P + "commande") or "").strip().replace(" ", "_").replace("/", "-")
            st.download_button("⬇️ Télécharger la fiche SIDIV (PDF)", data=st.session_state[P + "pdf"],
                               file_name="Doc_SIDIV_Verification" + (f"_{suffixe}" if suffixe else "") + ".pdf",
                               mime="application/pdf", key=P + "dl")
