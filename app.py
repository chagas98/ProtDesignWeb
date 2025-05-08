from flask import Flask, render_template, request, jsonify, redirect
import json
import os
from Bio.PDB import PDBParser, PPBuilder
import pandas as pd

app = Flask(__name__)

# Carrega a lookup table de estabilidade
with open("data/stability_lookup.json") as f:
    stability_data = json.load(f)

df = pd.read_csv("data/GH1_mpnn_probs_diff.csv", index_col=0)

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
    bar_value = 0.5

    if request.method == "POST":
        position = int(request.form["position"])  # Position is an integer
        mutation_aa = request.form["mutation_aa"]  # Selected amino acid
        reset = request.form["reset"]

        print(f"Received position: {position}, Mutation AA: {mutation_aa}")

        if reset == "1":
            return render_template("index.html", pdb_file=TOPOL_FILE, mutation_result=None, sequence=sequence)

        if position != 'reset' and mutation_aa:
            # Get the corresponding row (position) and column (mutation amino acid)
            row = df.loc[position]
            aa_value = row[mutation_aa]  # Get the value from the DataFrame cell

            # Determine if the mutation is stabilizing or destabilizing
            if aa_value > 0:
                mutation_result = f"A mutação {position}{mutation_aa} é **ESTABILIZANTE** (ΔΔG={aa_value:.2f})"
                bar_value = aa_value  # Positive value indicates stabilizing
                pdb_file = STABLE_FILE
                redirect_page = "stable"
            elif aa_value < 0:
                mutation_result = f"A mutação {position}{mutation_aa} é **DESESTABILIZANTE** (ΔΔG={aa_value:.2f})"
                bar_value = aa_value  # Negative value indicates stabilizing
                pdb_file = UNSTABLE_FILE
                redirect_page = "unstable"
            else:
                mutation_result = f"A mutação {position}{mutation_aa} tem ΔΔG de 0, não é nem estabilizante nem destabilizante."
                bar_value = 0
                redirect_page = None

            # Normalize the bar value between -1 and 1 for display
            bar_value = (bar_value + 1) / 2  # Convert value to [0, 1] range for bar

            if redirect_page:
                return render_template("mutation_process.html", mutation_result=mutation_result, bar_value=bar_value, pdb_file=pdb_file, sequence=sequence, redirect_page=redirect_page)
        #return render_template("mutation_process.html", pdb_file=pdb_file, mutation_result=mutation_result, sequence=sequence, bar_value=bar_value)

    return render_template("start.html", pdb_file=TOPOL_FILE, sequence=sequence)

@app.route("/stable")
def stable():
    return render_template("stable.html", stable_file=STABLE_FILE)

@app.route("/unstable")
def unstable():
    return render_template("unstable.html", unstable_file=UNSTABLE_FILE)


if __name__ == "__main__":
    app.run(debug=True)
