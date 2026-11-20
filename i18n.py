"""Traductions de l'interface (FR / EN / DE / ES / IT).

Usage : t("cle", n=3) -> texte dans la langue choisie (st.session_state["lang"]).
Le français sert de langue de secours si une clé manque dans une langue.
Les colonnes de l'Excel généré et le formulaire PDF SIDIV restent en français."""
import streamlit as st

LANGUES = {"fr": "🇫🇷 Français", "en": "🇬🇧 English", "de": "🇩🇪 Deutsch",
           "es": "🇪🇸 Español", "it": "🇮🇹 Italiano"}

TR = {
# ---------------------------------------------------------------- titre / aide
"dark": {
    "fr": "🌙 Mode Sombre", "en": "🌙 Dark mode", "de": "🌙 Dunkelmodus",
    "es": "🌙 Modo oscuro", "it": "🌙 Modalità scura"},
"lang": {
    "fr": "🌐 Langue", "en": "🌐 Language", "de": "🌐 Sprache",
    "es": "🌐 Idioma", "it": "🌐 Lingua"},
"title": {
    "fr": "🧪 Compilateur de Résultats Cobas & MPL vers Excel (Version {v})",
    "en": "🧪 Cobas & MPL Results Compiler to Excel (Version {v})",
    "de": "🧪 Cobas- & MPL-Ergebnis-Compiler für Excel (Version {v})",
    "es": "🧪 Compilador de resultados Cobas y MPL a Excel (Versión {v})",
    "it": "🧪 Compilatore di risultati Cobas e MPL in Excel (Versione {v})"},
"howto_title": {
    "fr": "📖 Comment utiliser l'outil ?", "en": "📖 How to use the tool?",
    "de": "📖 Wie wird das Tool verwendet?", "es": "📖 ¿Cómo usar la herramienta?",
    "it": "📖 Come usare lo strumento?"},
"howto": {
    "fr": """
1. **Fichiers Cobas et MPL** : déposez dans la case 1️⃣ les rapports Cobas (PDF) ainsi que les PDF MPL, obtenus depuis le **dossier patient** en cliquant sur l'icône **imprimante** 🖨️.
2. **Export Driver Manager** (obligatoire) : dans **Driver Manager**, allez dans l'onglet **Analyse**, puis cliquez sur **Exporter**. Déposez le CSV obtenu dans la case 2️⃣.
3. **Export MPL** (optionnel) : dans **MPL**, allez dans **Analyse**, puis cliquez sur **Exporter**. Déposez le CSV obtenu dans la case 3️⃣.
4. Lancez l'extraction, vérifiez la correspondance des analyses, puis téléchargez le fichier Excel.
5. ⚠️ **À la fin**, partagez le document **au format Google Sheet** avec le **bio responsable du plateau**.
""",
    "en": """
1. **Cobas and MPL files**: drop into box 1️⃣ the Cobas reports (PDF) and the MPL PDFs, obtained from the **patient record** by clicking the **printer** icon 🖨️.
2. **Driver Manager export** (mandatory): in **Driver Manager**, open the **Analysis** tab, then click **Export**. Drop the resulting CSV into box 2️⃣.
3. **MPL export** (optional): in **MPL**, go to **Analysis**, then click **Export**. Drop the resulting CSV into box 3️⃣.
4. Run the extraction, check the test matching, then download the Excel file.
5. ⚠️ **At the end**, share the document **as a Google Sheet** with the **laboratory section's responsible biologist**.
""",
    "de": """
1. **Cobas- und MPL-Dateien**: Legen Sie in Feld 1️⃣ die Cobas-Berichte (PDF) sowie die MPL-PDFs ab, die Sie aus der **Patientenakte** über das **Drucker**-Symbol 🖨️ erhalten.
2. **Driver-Manager-Export** (obligatorisch): Öffnen Sie im **Driver Manager** den Reiter **Analyse** und klicken Sie auf **Exportieren**. Legen Sie die CSV-Datei in Feld 2️⃣ ab.
3. **MPL-Export** (optional): Gehen Sie in **MPL** zu **Analyse** und klicken Sie auf **Exportieren**. Legen Sie die CSV-Datei in Feld 3️⃣ ab.
4. Starten Sie die Extraktion, prüfen Sie die Zuordnung der Analysen und laden Sie die Excel-Datei herunter.
5. ⚠️ **Zum Schluss** teilen Sie das Dokument **als Google Sheet** mit dem **verantwortlichen Biologen des Bereichs**.
""",
    "es": """
1. **Archivos Cobas y MPL**: deposite en la casilla 1️⃣ los informes Cobas (PDF) y los PDF de MPL, obtenidos desde el **expediente del paciente** pulsando el icono de **impresora** 🖨️.
2. **Exportación de Driver Manager** (obligatoria): en **Driver Manager**, abra la pestaña **Análisis** y pulse **Exportar**. Deposite el CSV obtenido en la casilla 2️⃣.
3. **Exportación de MPL** (opcional): en **MPL**, vaya a **Análisis** y pulse **Exportar**. Deposite el CSV obtenido en la casilla 3️⃣.
4. Lance la extracción, verifique la correspondencia de los análisis y descargue el archivo Excel.
5. ⚠️ **Al final**, comparta el documento **en formato Google Sheet** con el **biólogo responsable de la sección**.
""",
    "it": """
1. **File Cobas e MPL**: carichi nella casella 1️⃣ i rapporti Cobas (PDF) e i PDF MPL, ottenuti dalla **cartella del paziente** cliccando sull'icona **stampante** 🖨️.
2. **Esportazione Driver Manager** (obbligatoria): in **Driver Manager**, apra la scheda **Analisi** e clicchi su **Esporta**. Carichi il CSV ottenuto nella casella 2️⃣.
3. **Esportazione MPL** (facoltativa): in **MPL**, vada su **Analisi** e clicchi su **Esporta**. Carichi il CSV ottenuto nella casella 3️⃣.
4. Avvii l'estrazione, verifichi la corrispondenza delle analisi, poi scarichi il file Excel.
5. ⚠️ **Alla fine**, condivida il documento **in formato Google Sheet** con il **biologo responsabile del settore**.
"""},
"sidiv_info": {
    "fr": "📝 **Fiche SIDIV (optionnelle)** : tout en bas de la page, une fiche SIDIV de vérification de connexion se **pré-remplit partiellement** une fois les fichiers déposés et les données extraites (automate, version du driver, dossiers de test, cases cochées par défaut…). **Il reste des informations à saisir à la main** (LBM, intervenants, numéro de commande, versions des logiciels, remarques…) et à vérifier avant de générer le PDF. Elle n'est pas obligatoire et n'a aucun effet sur le compilateur.",
    "en": "📝 **SIDIV form (optional)**: at the very bottom of the page, a SIDIV connection-verification form is **partially pre-filled** once the files are dropped and the data extracted (analyzer, driver version, test records, default ticked boxes…). **Some information must still be entered by hand** (lab, participants, order number, software versions, remarks…) and checked before generating the PDF. It is not mandatory and has no effect on the compiler. The PDF form itself stays in French.",
    "de": "📝 **SIDIV-Formular (optional)**: ganz unten auf der Seite wird ein SIDIV-Formular zur Verbindungsprüfung **teilweise vorausgefüllt**, sobald die Dateien abgelegt und die Daten extrahiert sind (Analysegerät, Treiberversion, Testfälle, standardmäßig angekreuzte Felder…). **Einige Angaben müssen von Hand ergänzt werden** (Labor, Beteiligte, Bestellnummer, Softwareversionen, Bemerkungen…) und vor der PDF-Erstellung geprüft werden. Es ist nicht obligatorisch und hat keinen Einfluss auf den Compiler. Das PDF-Formular selbst bleibt auf Französisch.",
    "es": "📝 **Ficha SIDIV (opcional)**: al final de la página, una ficha SIDIV de verificación de conexión se **rellena parcialmente** una vez depositados los archivos y extraídos los datos (analizador, versión del driver, expedientes de prueba, casillas marcadas por defecto…). **Quedan datos por introducir a mano** (laboratorio, intervinientes, número de pedido, versiones de software, observaciones…) y por verificar antes de generar el PDF. No es obligatoria y no afecta al compilador. El formulario PDF en sí permanece en francés.",
    "it": "📝 **Scheda SIDIV (facoltativa)**: in fondo alla pagina, una scheda SIDIV di verifica della connessione viene **precompilata parzialmente** dopo il caricamento dei file e l'estrazione dei dati (analizzatore, versione del driver, cartelle di test, caselle spuntate di default…). **Restano dati da inserire a mano** (laboratorio, partecipanti, numero d'ordine, versioni dei software, osservazioni…) e da verificare prima di generare il PDF. Non è obbligatoria e non influisce sul compilatore. Il modulo PDF resta in francese."},
"no_ocr": {
    "fr": "⚠️ Module `pytesseract` ou `Pillow` non détecté. L'extraction depuis des images sera désactivée.",
    "en": "⚠️ `pytesseract` or `Pillow` module not detected. Extraction from images will be disabled.",
    "de": "⚠️ Modul `pytesseract` oder `Pillow` nicht gefunden. Die Extraktion aus Bildern wird deaktiviert.",
    "es": "⚠️ Módulo `pytesseract` o `Pillow` no detectado. La extracción desde imágenes estará desactivada.",
    "it": "⚠️ Modulo `pytesseract` o `Pillow` non rilevato. L'estrazione dalle immagini sarà disattivata."},
"blank_tip": {
    "fr": "💡 **Astuce :** Vous pouvez générer un fichier Excel d'analyses vierges dès maintenant (sans déposer de fichier) si vous souhaitez faire une saisie entièrement manuelle.",
    "en": "💡 **Tip:** You can generate a blank Excel analysis file right now (without dropping any file) if you prefer fully manual entry.",
    "de": "💡 **Tipp:** Sie können sofort eine leere Excel-Analysedatei erzeugen (ohne Dateien abzulegen), wenn Sie die Daten komplett manuell eingeben möchten.",
    "es": "💡 **Consejo:** Puede generar ahora un archivo Excel de análisis vacío (sin depositar ningún archivo) si prefiere una introducción totalmente manual.",
    "it": "💡 **Suggerimento:** può generare subito un file Excel di analisi vuoto (senza caricare file) se preferisce un inserimento interamente manuale."},
"blank_btn": {
    "fr": "⬇️ Télécharger la trame vierge", "en": "⬇️ Download the blank template",
    "de": "⬇️ Leere Vorlage herunterladen", "es": "⬇️ Descargar la plantilla vacía",
    "it": "⬇️ Scarica il modello vuoto"},
# ---------------------------------------------------------------- étape 1
"step1": {
    "fr": "Étape 1 : Dépôt des fichiers", "en": "Step 1: Drop the files",
    "de": "Schritt 1: Dateien ablegen", "es": "Paso 1: Depósito de archivos",
    "it": "Passo 1: Caricamento dei file"},
"up1": {
    "fr": "1️⃣ Déposez les fichiers PDF ou IMAGES (png, jpg)",
    "en": "1️⃣ Drop the PDF or IMAGE files (png, jpg)",
    "de": "1️⃣ PDF- oder BILD-Dateien ablegen (png, jpg)",
    "es": "1️⃣ Deposite los archivos PDF o IMÁGENES (png, jpg)",
    "it": "1️⃣ Carichi i file PDF o IMMAGINI (png, jpg)"},
"n_files": {
    "fr": "📂 **{n} fichier(s) prêt(s) pour l'extraction**",
    "en": "📂 **{n} file(s) ready for extraction**",
    "de": "📂 **{n} Datei(en) bereit zur Extraktion**",
    "es": "📂 **{n} archivo(s) listo(s) para la extracción**",
    "it": "📂 **{n} file pronti per l'estrazione**"},
"up2": {
    "fr": "2️⃣ Obligatoire : Export Driver Manager (onglet Analyse)",
    "en": "2️⃣ Mandatory: Driver Manager export (Analysis tab)",
    "de": "2️⃣ Obligatorisch: Driver-Manager-Export (Reiter Analyse)",
    "es": "2️⃣ Obligatorio: exportación de Driver Manager (pestaña Análisis)",
    "it": "2️⃣ Obbligatorio: esportazione Driver Manager (scheda Analisi)"},
"up3": {
    "fr": "3️⃣ Optionnel : Export analyse MPL (CSV)", "en": "3️⃣ Optional: MPL analysis export (CSV)",
    "de": "3️⃣ Optional: MPL-Analyse-Export (CSV)", "es": "3️⃣ Opcional: exportación de análisis MPL (CSV)",
    "it": "3️⃣ Facoltativo: esportazione analisi MPL (CSV)"},
"extract_btn": {
    "fr": "📥 Extraire les données des fichiers", "en": "📥 Extract data from the files",
    "de": "📥 Daten aus den Dateien extrahieren", "es": "📥 Extraer los datos de los archivos",
    "it": "📥 Estrai i dati dai file"},
"err_swap": {
    "fr": "❌ La case 2️⃣ doit contenir le driver MPL : colonnes \"Nom de l'analyse\" et \"Code ACN\" introuvables. Les deux CSV sont-ils inversés ?",
    "en": "❌ Box 2️⃣ must contain the MPL driver: columns \"Nom de l'analyse\" and \"Code ACN\" not found. Are the two CSVs swapped?",
    "de": "❌ Feld 2️⃣ muss den MPL-Treiber enthalten: Spalten \"Nom de l'analyse\" und \"Code ACN\" nicht gefunden. Sind die beiden CSV-Dateien vertauscht?",
    "es": "❌ La casilla 2️⃣ debe contener el driver MPL: columnas \"Nom de l'analyse\" y \"Code ACN\" no encontradas. ¿Están invertidos los dos CSV?",
    "it": "❌ La casella 2️⃣ deve contenere il driver MPL: colonne \"Nom de l'analyse\" e \"Code ACN\" non trovate. I due CSV sono scambiati?"},
"warn_mpl_cols": {
    "fr": "⚠️ La case 3️⃣ ne contient pas les colonnes \"LibelLong\" et \"Nom\" : les libellés MPL ne seront pas traduits en codes.",
    "en": "⚠️ Box 3️⃣ does not contain the \"LibelLong\" and \"Nom\" columns: MPL labels will not be translated into codes.",
    "de": "⚠️ Feld 3️⃣ enthält die Spalten \"LibelLong\" und \"Nom\" nicht: MPL-Bezeichnungen werden nicht in Codes übersetzt.",
    "es": "⚠️ La casilla 3️⃣ no contiene las columnas \"LibelLong\" y \"Nom\": las etiquetas MPL no se traducirán a códigos.",
    "it": "⚠️ La casella 3️⃣ non contiene le colonne \"LibelLong\" e \"Nom\": le etichette MPL non saranno tradotte in codici."},
"spin_extract": {
    "fr": "Lecture et analyse intelligente en cours...", "en": "Smart reading and analysis in progress...",
    "de": "Intelligentes Lesen und Analysieren läuft...", "es": "Lectura y análisis inteligente en curso...",
    "it": "Lettura e analisi intelligente in corso..."},
# ---------------------------------------------------------------- étape 2
"step2": {
    "fr": "Étape 2 : Correspondance des analyses", "en": "Step 2: Test matching",
    "de": "Schritt 2: Zuordnung der Analysen", "es": "Paso 2: Correspondencia de análisis",
    "it": "Passo 2: Corrispondenza delle analisi"},
"err_no_cobas": {
    "fr": "❌ Impossible de passer à l'étape 2 : aucun rapport cobas lisible parmi les fichiers déposés dans la première case.",
    "en": "❌ Cannot go to step 2: no readable Cobas report among the files dropped in the first box.",
    "de": "❌ Schritt 2 nicht möglich: Unter den in Feld 1 abgelegten Dateien befindet sich kein lesbarer Cobas-Bericht.",
    "es": "❌ No se puede pasar al paso 2: ningún informe Cobas legible entre los archivos depositados en la primera casilla.",
    "it": "❌ Impossibile passare al passo 2: nessun rapporto Cobas leggibile tra i file caricati nella prima casella."},
"prefilled": {
    "fr": "🪄 **L'outil a pré-rempli les menus déroulants !** Modifiez-les si besoin.",
    "en": "🪄 **The tool has pre-filled the drop-down menus!** Edit them if needed.",
    "de": "🪄 **Das Tool hat die Auswahlmenüs vorausgefüllt!** Ändern Sie sie bei Bedarf.",
    "es": "🪄 **¡La herramienta ha rellenado los menús desplegables!** Modifíquelos si es necesario.",
    "it": "🪄 **Lo strumento ha precompilato i menu a tendina!** Li modifichi se necessario."},
"s_none": {
    "fr": "🔴 -- Aucune correspondance --", "en": "🔴 -- No match --",
    "de": "🔴 -- Keine Zuordnung --", "es": "🔴 -- Sin correspondencia --",
    "it": "🔴 -- Nessuna corrispondenza --"},
"s_ignore": {
    "fr": "❌ -- Ignorer cette analyse --", "en": "❌ -- Ignore this test --",
    "de": "❌ -- Diese Analyse ignorieren --", "es": "❌ -- Ignorar este análisis --",
    "it": "❌ -- Ignora questa analisi --"},
"filter_label": {
    "fr": "Filtre d'affichage des analyses :", "en": "Test display filter:",
    "de": "Anzeigefilter für Analysen:", "es": "Filtro de visualización de análisis:",
    "it": "Filtro di visualizzazione delle analisi:"},
"f_all": {"fr": "Toutes", "en": "All", "de": "Alle", "es": "Todos", "it": "Tutte"},
"f_todo": {
    "fr": "🔴 À vérifier (Aucune correspondance)", "en": "🔴 To check (No match)",
    "de": "🔴 Zu prüfen (Keine Zuordnung)", "es": "🔴 Por verificar (Sin correspondencia)",
    "it": "🔴 Da verificare (Nessuna corrispondenza)"},
"f_ok": {
    "fr": "✅ Validées", "en": "✅ Validated", "de": "✅ Validiert",
    "es": "✅ Validados", "it": "✅ Validate"},
"f_ign": {
    "fr": "❌ Ignorées", "en": "❌ Ignored", "de": "❌ Ignoriert",
    "es": "❌ Ignorados", "it": "❌ Ignorate"},
"recalc": {
    "fr": "🔄 Recalculer les liens automatiques", "en": "🔄 Recompute automatic links",
    "de": "🔄 Automatische Zuordnungen neu berechnen", "es": "🔄 Recalcular los vínculos automáticos",
    "it": "🔄 Ricalcola i collegamenti automatici"},
"showing": {
    "fr": "Affichage de **{n}** analyse(s) sur {total}.", "en": "Showing **{n}** test(s) out of {total}.",
    "de": "Anzeige von **{n}** Analyse(n) von {total}.", "es": "Mostrando **{n}** análisis de {total}.",
    "it": "Visualizzazione di **{n}** analisi su {total}."},
"gen_btn": {
    "fr": "✅ Générer le tableau final", "en": "✅ Generate the final table",
    "de": "✅ Endgültige Tabelle erzeugen", "es": "✅ Generar la tabla final",
    "it": "✅ Genera la tabella finale"},
"spin_merge": {
    "fr": "Fusion intelligente en cours...", "en": "Smart merge in progress...",
    "de": "Intelligente Zusammenführung läuft...", "es": "Fusión inteligente en curso...",
    "it": "Unione intelligente in corso..."},
# ---------------------------------------------------------------- étape 3
"done": {
    "fr": "✅ Fichier compilé avec succès !", "en": "✅ File compiled successfully!",
    "de": "✅ Datei erfolgreich kompiliert!", "es": "✅ ¡Archivo compilado con éxito!",
    "it": "✅ File compilato con successo!"},
"dl_excel": {
    "fr": "📥 Télécharger le fichier compilé (Excel)", "en": "📥 Download the compiled file (Excel)",
    "de": "📥 Kompilierte Datei herunterladen (Excel)", "es": "📥 Descargar el archivo compilado (Excel)",
    "it": "📥 Scarica il file compilato (Excel)"},
"restart": {
    "fr": "🔄 Recommencer une nouvelle compilation", "en": "🔄 Start a new compilation",
    "de": "🔄 Neue Kompilierung starten", "es": "🔄 Empezar una nueva compilación",
    "it": "🔄 Inizia una nuova compilazione"},
"debug_title": {
    "fr": "🐛 Voir les données brutes extraites (Débogage)", "en": "🐛 View the raw extracted data (Debug)",
    "de": "🐛 Extrahierte Rohdaten anzeigen (Debug)", "es": "🐛 Ver los datos brutos extraídos (Depuración)",
    "it": "🐛 Visualizza i dati grezzi estratti (Debug)"},
"debug_cobas": {
    "fr": "**Données extraites des Fichiers (Cobas) :**", "en": "**Data extracted from the files (Cobas):**",
    "de": "**Aus den Dateien extrahierte Daten (Cobas):**", "es": "**Datos extraídos de los archivos (Cobas):**",
    "it": "**Dati estratti dai file (Cobas):**"},
"debug_mpl": {
    "fr": "**Données extraites des Fichiers (MPL ou Images) :**", "en": "**Data extracted from the files (MPL or images):**",
    "de": "**Aus den Dateien extrahierte Daten (MPL oder Bilder):**", "es": "**Datos extraídos de los archivos (MPL o imágenes):**",
    "it": "**Dati estratti dai file (MPL o immagini):**"},
"debug_nr": {
    "fr": "**Lignes du rapport cobas non reconnues ({n}) :**", "en": "**Unrecognised Cobas report lines ({n}):**",
    "de": "**Nicht erkannte Zeilen des Cobas-Berichts ({n}):**", "es": "**Líneas del informe Cobas no reconocidas ({n}):**",
    "it": "**Righe del rapporto Cobas non riconosciute ({n}):**"},
"sidiv_unavailable": {
    "fr": "Fiche SIDIV indisponible : {e}", "en": "SIDIV form unavailable: {e}",
    "de": "SIDIV-Formular nicht verfügbar: {e}", "es": "Ficha SIDIV no disponible: {e}",
    "it": "Scheda SIDIV non disponibile: {e}"},
# ---------------------------------------------------------------- erreurs d'extraction
"e_pdf_empty": {
    "fr": "⚠️ Le PDF '{f}' ne contient aucun texte lisible (document scanné ?). Fournis-le en image (png/jpg) pour passer par l'OCR.",
    "en": "⚠️ The PDF '{f}' contains no readable text (scanned document?). Provide it as an image (png/jpg) to use OCR.",
    "de": "⚠️ Die PDF '{f}' enthält keinen lesbaren Text (gescanntes Dokument?). Legen Sie sie als Bild (png/jpg) ab, um die OCR zu nutzen.",
    "es": "⚠️ El PDF '{f}' no contiene texto legible (¿documento escaneado?). Proporciónelo como imagen (png/jpg) para usar el OCR.",
    "it": "⚠️ Il PDF '{f}' non contiene testo leggibile (documento scansionato?). Lo fornisca come immagine (png/jpg) per usare l'OCR."},
"e_cobas_empty": {
    "fr": "⚠️ Le rapport cobas '{f}' n'a retourné aucun résultat.",
    "en": "⚠️ The Cobas report '{f}' returned no result.",
    "de": "⚠️ Der Cobas-Bericht '{f}' lieferte kein Ergebnis.",
    "es": "⚠️ El informe Cobas '{f}' no devolvió ningún resultado.",
    "it": "⚠️ Il rapporto Cobas '{f}' non ha restituito alcun risultato."},
"e_mpl_empty": {
    "fr": "⚠️ Le compte rendu MPL '{f}' n'a retourné aucune analyse (ni rapport cobas reconnu, ni ligne de résultat MPL).",
    "en": "⚠️ The MPL report '{f}' returned no test (neither a recognised Cobas report nor an MPL result line).",
    "de": "⚠️ Der MPL-Bericht '{f}' lieferte keine Analyse (weder ein erkannter Cobas-Bericht noch eine MPL-Ergebniszeile).",
    "es": "⚠️ El informe MPL '{f}' no devolvió ningún análisis (ni informe Cobas reconocido, ni línea de resultado MPL).",
    "it": "⚠️ Il referto MPL '{f}' non ha restituito alcuna analisi (né rapporto Cobas riconosciuto, né riga di risultato MPL)."},
"e_img_noocr": {
    "fr": "⚠️ Image '{f}' ignorée : le module OCR (pytesseract / Pillow) n'est pas installé.",
    "en": "⚠️ Image '{f}' ignored: the OCR module (pytesseract / Pillow) is not installed.",
    "de": "⚠️ Bild '{f}' ignoriert: Das OCR-Modul (pytesseract / Pillow) ist nicht installiert.",
    "es": "⚠️ Imagen '{f}' ignorada: el módulo OCR (pytesseract / Pillow) no está instalado.",
    "it": "⚠️ Immagine '{f}' ignorata: il modulo OCR (pytesseract / Pillow) non è installato."},
"e_img_ocr": {
    "fr": "⚠️ Image '{f}' non lue par l'OCR ({err}). Le programme Tesseract est-il installé sur ce poste ?",
    "en": "⚠️ Image '{f}' not read by the OCR ({err}). Is the Tesseract program installed on this machine?",
    "de": "⚠️ Bild '{f}' von der OCR nicht gelesen ({err}). Ist das Programm Tesseract auf diesem Rechner installiert?",
    "es": "⚠️ Imagen '{f}' no leída por el OCR ({err}). ¿Está instalado el programa Tesseract en este equipo?",
    "it": "⚠️ Immagine '{f}' non letta dall'OCR ({err}). Il programma Tesseract è installato su questo computer?"},
# ---------------------------------------------------------------- avancement des tests
"prog_title": {
    "fr": "📊 Avancement des tests (ACN du CSV de l'étape 2)", "en": "📊 Test progress (ACNs from the step 2 CSV)",
    "de": "📊 Testfortschritt (ACN aus der CSV von Schritt 2)", "es": "📊 Avance de las pruebas (ACN del CSV del paso 2)",
    "it": "📊 Avanzamento dei test (ACN del CSV del passo 2)"},
"prog_help": {
    "fr": "Tous les codes ACN présents dans le CSV Driver Manager (case 2️⃣) sont considérés comme **à tester**. Un ACN est **testé** s'il est présent dans les rapports Cobas ou les résultats MPL extraits (hors analyses ignorées).",
    "en": "All ACN codes in the Driver Manager CSV (box 2️⃣) are considered **to be tested**. An ACN is **tested** if it appears in the extracted Cobas reports or MPL results (ignored tests excluded).",
    "de": "Alle ACN-Codes der Driver-Manager-CSV (Feld 2️⃣) gelten als **zu testen**. Ein ACN gilt als **getestet**, wenn er in den extrahierten Cobas-Berichten oder MPL-Ergebnissen vorkommt (ignorierte Analysen ausgenommen).",
    "es": "Todos los códigos ACN presentes en el CSV de Driver Manager (casilla 2️⃣) se consideran **por probar**. Un ACN está **probado** si aparece en los informes Cobas o resultados MPL extraídos (excluidos los análisis ignorados).",
    "it": "Tutti i codici ACN presenti nel CSV di Driver Manager (casella 2️⃣) sono considerati **da testare**. Un ACN è **testato** se compare nei rapporti Cobas o nei risultati MPL estratti (escluse le analisi ignorate)."},
"prog_metric": {
    "fr": "Avancement", "en": "Progress", "de": "Fortschritt", "es": "Avance", "it": "Avanzamento"},
"prog_tested": {
    "fr": "ACN testés", "en": "ACNs tested", "de": "ACN getestet", "es": "ACN probados", "it": "ACN testati"},
"prog_total": {
    "fr": "ACN à tester", "en": "ACNs to test", "de": "ACN zu testen", "es": "ACN por probar", "it": "ACN da testare"},
"prog_missing_n": {
    "fr": "ACN manquants", "en": "Missing ACNs", "de": "Fehlende ACN", "es": "ACN faltantes", "it": "ACN mancanti"},
"prog_all": {
    "fr": "🎉 Tous les ACN du CSV ont été testés.", "en": "🎉 All ACNs of the CSV have been tested.",
    "de": "🎉 Alle ACN der CSV wurden getestet.", "es": "🎉 Todos los ACN del CSV han sido probados.",
    "it": "🎉 Tutti gli ACN del CSV sono stati testati."},
"prog_missing_title": {
    "fr": "📋 Liste des ACN manquants ({n})", "en": "📋 List of missing ACNs ({n})",
    "de": "📋 Liste der fehlenden ACN ({n})", "es": "📋 Lista de ACN faltantes ({n})",
    "it": "📋 Elenco degli ACN mancanti ({n})"},
"prog_col_acn": {"fr": "Code ACN", "en": "ACN code", "de": "ACN-Code", "es": "Código ACN", "it": "Codice ACN"},
"prog_col_mpl": {
    "fr": "Code(s) MPL (driver)", "en": "MPL code(s) (driver)", "de": "MPL-Code(s) (Treiber)",
    "es": "Código(s) MPL (driver)", "it": "Codice/i MPL (driver)"},
"prog_col_cobas": {
    "fr": "Test Cobas connu", "en": "Known Cobas test", "de": "Bekannter Cobas-Test",
    "es": "Prueba Cobas conocida", "it": "Test Cobas noto"},
"prog_dl": {
    "fr": "⬇️ Télécharger la liste des ACN manquants (CSV)", "en": "⬇️ Download the missing ACN list (CSV)",
    "de": "⬇️ Liste der fehlenden ACN herunterladen (CSV)", "es": "⬇️ Descargar la lista de ACN faltantes (CSV)",
    "it": "⬇️ Scarica l'elenco degli ACN mancanti (CSV)"},
"prog_extra": {
    "fr": "ℹ️ {n} ACN testé(s) ne figurent pas dans le CSV du driver (non comptés) : {l}",
    "en": "ℹ️ {n} tested ACN(s) are not in the driver CSV (not counted): {l}",
    "de": "ℹ️ {n} getestete(r) ACN stehen nicht in der Treiber-CSV (nicht gezählt): {l}",
    "es": "ℹ️ {n} ACN probado(s) no figuran en el CSV del driver (no contados): {l}",
    "it": "ℹ️ {n} ACN testati non sono nel CSV del driver (non conteggiati): {l}"},
# ---------------------------------------------------------------- SIDIV (interface seulement)
"sd_title": {
    "fr": "📝 Fiche SIDIV – Vérification de connexion (optionnel)", "en": "📝 SIDIV form – Connection verification (optional)",
    "de": "📝 SIDIV-Formular – Verbindungsprüfung (optional)", "es": "📝 Ficha SIDIV – Verificación de conexión (opcional)",
    "it": "📝 Scheda SIDIV – Verifica della connessione (facoltativa)"},
"sd_missing": {
    "fr": "Modèle introuvable : {f}", "en": "Template not found: {f}", "de": "Vorlage nicht gefunden: {f}",
    "es": "Plantilla no encontrada: {f}", "it": "Modello non trovato: {f}"},
"sd_caption": {
    "fr": "Facultatif : indépendant du compilateur ci-dessus. Remplissez ce que vous voulez, puis générez le PDF : il reste modifiable (champs de formulaire) et les signatures restent à faire.",
    "en": "Optional: independent from the compiler above. Fill in what you want, then generate the PDF: it stays editable (form fields) and the signatures are still to be done. (Form content stays in French.)",
    "de": "Optional: unabhängig vom Compiler oben. Füllen Sie aus, was Sie möchten, und erzeugen Sie dann das PDF: Es bleibt bearbeitbar (Formularfelder), die Unterschriften stehen noch aus. (Formularinhalt bleibt auf Französisch.)",
    "es": "Opcional: independiente del compilador de arriba. Rellene lo que desee y genere el PDF: sigue siendo editable (campos de formulario) y las firmas quedan pendientes. (El contenido del formulario sigue en francés.)",
    "it": "Facoltativo: indipendente dal compilatore qui sopra. Compili ciò che vuole, poi generi il PDF: resta modificabile (campi del modulo) e le firme sono ancora da apporre. (Il contenuto del modulo resta in francese.)"},
"sd_tab1": {"fr": "1. Informations générales", "en": "1. General information", "de": "1. Allgemeine Angaben",
            "es": "1. Información general", "it": "1. Informazioni generali"},
"sd_tab2": {"fr": "2. Périmètre", "en": "2. Scope", "de": "2. Umfang", "es": "2. Alcance", "it": "2. Perimetro"},
"sd_tab3": {"fr": "3. Description de la connexion", "en": "3. Connection description",
            "de": "3. Beschreibung der Verbindung", "es": "3. Descripción de la conexión",
            "it": "3. Descrizione della connessione"},
"sd_tab4": {"fr": "4. Tests effectués", "en": "4. Tests performed", "de": "4. Durchgeführte Tests",
            "es": "4. Pruebas realizadas", "it": "4. Test eseguiti"},
"sd_tab5": {"fr": "Remarques & dates", "en": "Remarks & dates", "de": "Bemerkungen & Daten",
            "es": "Observaciones y fechas", "it": "Osservazioni e date"},
"sd_legend": {
    "fr": "Légende : Tr = Transmis / NA = Non applicable / T = Testé / OK = Test OK / NOK = Test non OK",
    "en": "Legend: Tr = Transmitted / NA = Not applicable / T = Tested / OK = Test OK / NOK = Test not OK",
    "de": "Legende: Tr = Übertragen / NA = Nicht anwendbar / T = Getestet / OK = Test OK / NOK = Test nicht OK",
    "es": "Leyenda: Tr = Transmitido / NA = No aplicable / T = Probado / OK = Prueba OK / NOK = Prueba no OK",
    "it": "Legenda: Tr = Trasmesso / NA = Non applicabile / T = Testato / OK = Test OK / NOK = Test non OK"},
"sd_detected": {
    "fr": "Dossiers tests détectés dans l'extraction : {l}", "en": "Test records detected in the extraction: {l}",
    "de": "In der Extraktion erkannte Testfälle: {l}", "es": "Expedientes de prueba detectados en la extracción: {l}",
    "it": "Cartelle di test rilevate nell'estrazione: {l}"},
"sd_ref": {
    "fr": "Réf. dossier test à reporter sur les lignes vides", "en": "Test record ref. to copy onto empty lines",
    "de": "Testfall-Ref. für leere Zeilen", "es": "Ref. del expediente de prueba a copiar en las líneas vacías",
    "it": "Rif. cartella di test da riportare sulle righe vuote"},
"sd_ref_help": {
    "fr": "Par ex. le n° de tube / dossier test utilisé pour la vérification.",
    "en": "E.g. the tube / test record number used for the verification.",
    "de": "Z. B. die für die Prüfung verwendete Röhrchen-/Testfallnummer.",
    "es": "Por ej. el n.º de tubo / expediente de prueba usado para la verificación.",
    "it": "Ad es. il n. di provetta / cartella di test usato per la verifica."},
"sd_apply": {"fr": "Appliquer", "en": "Apply", "de": "Anwenden", "es": "Aplicar", "it": "Applica"},
"sd_gen": {
    "fr": "📄 Générer la fiche SIDIV (PDF modifiable)", "en": "📄 Generate the SIDIV form (editable PDF)",
    "de": "📄 SIDIV-Formular erzeugen (bearbeitbares PDF)", "es": "📄 Generar la ficha SIDIV (PDF editable)",
    "it": "📄 Genera la scheda SIDIV (PDF modificabile)"},
"sd_fail": {
    "fr": "Échec de la génération de la fiche SIDIV : {e}", "en": "SIDIV form generation failed: {e}",
    "de": "Erzeugung des SIDIV-Formulars fehlgeschlagen: {e}", "es": "Error al generar la ficha SIDIV: {e}",
    "it": "Generazione della scheda SIDIV non riuscita: {e}"},
"sd_dl": {
    "fr": "⬇️ Télécharger la fiche SIDIV (PDF)", "en": "⬇️ Download the SIDIV form (PDF)",
    "de": "⬇️ SIDIV-Formular herunterladen (PDF)", "es": "⬇️ Descargar la ficha SIDIV (PDF)",
    "it": "⬇️ Scarica la scheda SIDIV (PDF)"},
# ---------------------------------------------------------------- bandeau (charte Roche)
"app_name": {
    "fr": "Compilateur Cobas & MPL", "en": "Cobas & MPL Compiler", "de": "Cobas- & MPL-Compiler",
    "es": "Compilador Cobas y MPL", "it": "Compilatore Cobas e MPL"},
"step1_short": {"fr": "Fichiers", "en": "Files", "de": "Dateien", "es": "Archivos", "it": "File"},
"step2_short": {"fr": "Correspondance", "en": "Matching", "de": "Zuordnung", "es": "Correspondencia",
                "it": "Corrispondenza"},
"step3_short": {"fr": "Résultat", "en": "Result", "de": "Ergebnis", "es": "Resultado", "it": "Risultato"},
"step3": {
    "fr": "Étape 3 : Résultat", "en": "Step 3: Result", "de": "Schritt 3: Ergebnis",
    "es": "Paso 3: Resultado", "it": "Passo 3: Risultato"},
"steps_aria": {"fr": "Étapes", "en": "Steps", "de": "Schritte", "es": "Pasos", "it": "Passi"},
"dark_tip": {
    "fr": "Mode sombre / mode clair", "en": "Dark / light mode", "de": "Dunkel-/Hellmodus",
    "es": "Modo oscuro / claro", "it": "Modalità scura / chiara"},
"foot": {
    "fr": "Outil d'aide à la vérification des connexions Cobas ↔ MPL",
    "en": "Helper tool for verifying Cobas ↔ MPL connections",
    "de": "Hilfswerkzeug zur Prüfung von Cobas-↔-MPL-Verbindungen",
    "es": "Herramienta de ayuda para verificar conexiones Cobas ↔ MPL",
    "it": "Strumento di supporto alla verifica delle connessioni Cobas ↔ MPL"},
}


def langue():
    return st.session_state.get("lang", "fr")


def t(cle, **kw):
    """Texte traduit (repli : français, puis la clé elle-même)."""
    d = TR.get(cle)
    if d is None:
        return cle
    txt = d.get(langue()) or d["fr"]
    return txt.format(**kw) if kw else txt
