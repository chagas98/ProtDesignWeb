from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from Bio.PDB import PDBParser, PPBuilder
import pandas as pd

app = Flask(__name__)

# Carrega a lookup table de estabilidade
with open("data/stability_lookup.json") as f:
    stability_data = json.load(f)

df = pd.read_csv("data/GH1_mpnn_probs_diff.csv", index_col=0)

print(df)
convert_aa_names = {
    "ALA": "A",
    "ARG": "R",
    "ASN": "N",
    "ASP": "D",
    "CYS": "C",
    "GLU": "E",
    "GLN": "Q",
    "GLY": "G",
    "HIS": "H",
    "ILE": "I",
    "LEU": "L",
    "LYS": "K",
    "MET": "M",
    "PHE": "F",
    "PRO": "P",
    "SER": "S",
    "THR": "T",
    "TRP": "W",
    "TYR": "Y",
    "VAL": "V"
}

THRESHOLD = 0.0  # valor fictício de threshold para decidir entre estável/instável
TOPOL_FILE = "GH1_AF_renum.pdb"  # arquivo PDB original
STABLE_FILE = "stable_rebuilt_trajectory.pdb"
UNSTABLE_FILE = "unstable_rebuilt_trajectory.pdb"  # arquivo PDB para mutações instáveis

@app.route("/", methods=["GET"])
def index():
    # The initial page with only the "Iniciar" button
    return render_template("index.html")

@app.route("/start", methods=["GET", "POST"])
def start():
    def get_sequence_from_pdb(filename):
        # If needed, adjust the path; if the file is in "static/data", you could do:
        filepath = os.path.join('data', filename)
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure("structure", filepath)
        ppb = PPBuilder()
        # Concatenate sequences from all polypeptides found in the structure (using the first peptide)
        pp = ppb.build_peptides(structure[0])
        return str(pp[0].get_sequence())

    mutation_result = None
    sequence = get_sequence_from_pdb(TOPOL_FILE)
    mutation_aa = request.form.get("data-mutation")
    bar_value = 0
    redirect_page = None
    if mutation_aa:
        # If the mutation is selected, get the corresponding value from the DataFrame
        mutation_aa = convert_aa_names[mutation_aa] if mutation_aa in convert_aa_names else None
        print(f"Mutation AA: {mutation_aa}")
    else:
        mutation_aa = None
    
    if request.method == "POST":
        aa_name = str(request.form.get("data-mutation"))
        position = int(request.form.get("data-position"))
        print(f"Position: {position}, Mutation AA: {mutation_aa}")

        if  mutation_aa:
            print(f"Mutation AA2: {mutation_aa}")
            # Get the corresponding row (position) and column (mutation amino acid)
            row = df.iloc[position]
            aa_value = row[mutation_aa]  # Get the value from the DataFrame cell
            print(f"AA Value: {aa_value}")
            # Determine if the mutation is stabilizing or destabilizing
            if aa_value > 0:
                mutation_result = f"A mutação {position}{mutation_aa} é **ESTABILIZANTE** (ΔΔG={aa_value:.2f})"
                bar_value = aa_value  # Positive value indicates stabilizing
                return redirect(url_for("stable", bar_value=bar_value))
                #return render_template("stable.html", mutation_result=mutation_result, bar_value=bar_value, pdb_file=pdb_file, sequence=sequence, redirect_page=redirect_page)
            elif aa_value < 0:
                mutation_result = f"A mutação {position}{mutation_aa} é **DESESTABILIZANTE** (ΔΔG={aa_value:.2f})"
                bar_value = aa_value  # Negative value indicates stabilizing
                return redirect(url_for("unstable", bar_value=bar_value))
                #return render_template("unstable.html", mutation_result=mutation_result, bar_value=bar_value, pdb_file=pdb_file, sequence=sequence, redirect_page=redirect_page)
            else:
                mutation_result = f"A mutação {position}{mutation_aa} tem ΔΔG de 0, não é nem estabilizante nem destabilizante."
                bar_value = 0
                redirect_page = None

    return render_template("start.html", pdb_file=TOPOL_FILE)

@app.route("/stable")
def stable():
    bar_value = request.args.get("bar_value", default=0, type=float)
    return render_template("stable.html", stable_file=STABLE_FILE, bar_value=bar_value)


@app.route("/unstable")
def unstable():
    bar_value = request.args.get("bar_value", default=0, type=float)
    return render_template("unstable.html", unstable_file=UNSTABLE_FILE, bar_value=bar_value)


if __name__ == "__main__":
    app.run(debug=True)
