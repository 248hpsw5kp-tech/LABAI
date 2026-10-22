import sys

# ==========================
# CACHE
# ==========================
gel_cache = None
primer_cache = None
notes_cache = ""

# ==========================
# BANNER & HELP
# ==========================
def banner():
    print("="*60)
    print("          LAB AI — Fast Advanced Molecular Biology Assistant")
    print("Commands: gel | primer | advisor | report | log | help | exit")
    print("="*60)

def help_menu():
    print("""
Available Commands:

gel <image_path> [ladder]   → Analyze gel image (optional ladder comma-separated)
primer <sequence>           → Analyze primer/sequence (GC%, Tm, ORF, warnings)
advisor <question>          → Ask AI lab assistant for advice
log <text>                  → Log experiment note
report <name>               → Generate PDF report with notes, gel, primer results
help                        → Show this menu
exit                        → Close LabAI
""")

# ==========================
# SEQUENCE UTILITIES (lazy-loaded)
# ==========================
def reverse_complement(seq):
    from Bio.Seq import Seq
    return str(Seq(seq).reverse_complement())

def translate_dna(seq):
    from Bio.Seq import Seq
    return str(Seq(seq).translate())

def primer_analysis(seq):
    # Lazy imports for speed
    from calculators import melting_temp
    from dna_tools import gc_content, find_orfs
    
    seq = seq.upper()
    gc = gc_content(seq)
    tm = melting_temp(seq)
    rev = reverse_complement(seq)
    frames = find_orfs(seq)
    
    warning = ""
    if "ATAT" in seq or "TATA" in seq:
        warning += "Warning: Possible hairpin/dimer.\n"
    
    result = f"""
Sequence Analysis:
Sequence: {seq}
Length: {len(seq)}
GC%: {gc:.2f}
Tm (°C): {tm}
Reverse Complement: {rev}
{warning}
Reading Frames: {frames}
"""
    return result

# ==========================
# GEL ANALYSIS (lazy-loaded)
# ==========================
def analyze_gel_lazy(img_path, ladder=None):
    global gel_cache
    if gel_cache:
        return gel_cache  # reuse previous result
    from gel_tools import analyze_gel
    gel_cache = analyze_gel(img_path, ladder)
    return gel_cache

# ==========================
# AI ADVISOR (lazy-loaded)
# ==========================
def ai_advisor(question):
    import ollama
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': 'You are a professional molecular biology lab assistant.'},
            {'role': 'user', 'content': question}
        ]
    )
    return response['message']['content']

# ==========================
# REPORT GENERATOR (lazy-loaded)
# ==========================
def generate_report(name, gel_results=None, primer_results=None, notes=None):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Lab AI Experiment Report: {name}", ln=True, align="C")
    
    pdf.set_font("Arial", "", 12)
    if notes:
        pdf.ln(5)
        pdf.cell(0, 10, "Notes:", ln=True)
        pdf.multi_cell(0, 8, notes)
    if primer_results:
        pdf.ln(5)
        pdf.cell(0, 10, "Primer Analysis:", ln=True)
        pdf.multi_cell(0, 8, primer_results)
    if gel_results:
        pdf.ln(5)
        pdf.cell(0, 10, "Gel Analysis:", ln=True)
        pdf.multi_cell(0, 8, str(gel_results))
    pdf.output(f"{name}.pdf")
    print(f"Report generated: {name}.pdf")

# ==========================
# MAIN LOOP
# ==========================
banner()

while True:
    try:
        user_input = input("LabAI> ").strip()
        if not user_input:
            continue

        parts = user_input.split()
        command = parts[0].lower()
        args = parts[1:]

        if command == "gel":
            if not args:
                print("Usage: gel <image_path> [optional ladder]")
                continue
            img_path = args[0]
            ladder = [int(x) for x in args[1].split(',')] if len(args) > 1 else None
            result = analyze_gel_lazy(img_path, ladder)
            print("Gel Analysis Result:", result)

        elif command == "primer":
            if not args:
                print("Usage: primer <DNA_sequence>")
                continue
            seq = args[0]
            primer_cache = primer_analysis(seq)
            print(primer_cache)

        elif command == "advisor":
            if not args:
                print("Usage: advisor <question>")
                continue
            print(ai_advisor(" ".join(args)))

        elif command == "log":
            note = " ".join(args)
            if not note:
                print("Usage: log <text>")
                continue
            from lab_notebook import log_experiment
            log_experiment(note)
            notes_cache += note + "\n"
            print("Note logged.")

        elif command == "report":
            if not args:
                print("Usage: report <name>")
                continue
            generate_report(args[0], gel_results=gel_cache, primer_results=primer_cache, notes=notes_cache)

        elif command == "help":
            help_menu()

        elif command == "exit":
            print("Closing LabAI.")
            sys.exit()

        else:
            print(ai_advisor(user_input))

    except Exception as e:
        print("Error:", e)
