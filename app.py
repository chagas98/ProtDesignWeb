from flask import Flask, render_template, request, jsonify
import json
import os
from Bio.PDB import PDBParser, PPBuilder

app = Flask(__name__)

# Carrega a lookup table de estabilidade
with open("data/stability_lookup.json") as f:
    stability_data = json.load(f)

THRESHOLD = 0.0  # valor fictício de threshold para decidir entre estável/instável
TOPOL_FILE = "topol.pdb"  # arquivo PDB original
UNSTABLE_FILE = "unstable.pdb"  # arquivo PDB para mutações instáveis

@app.route("/", methods=["GET", "POST"])
def index():

        # Define the sequence extraction function locally in the route.
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
    if request.method == "POST":
        position = request.form["position"]

        key = f"{position}"  # Ex: A123V
        stability = stability_data.get(key)

        if stability is not None:
            if stability >= THRESHOLD:
                pdb_file = TOPOL_FILE
                mutation_result = f"A mutação {key} é considerada **ESTÁVEL** (ΔΔG={stability})"
            else:
                pdb_file = UNSTABLE_FILE
                mutation_result = f"A mutação {key} é considerada **INSTÁVEL** (ΔΔG={stability})"
        else:
            pdb_file = TOPOL_FILE
            mutation_result = f"Mutação {key} não encontrada. Exibindo estrutura original."

        return render_template("index.html", pdb_file=pdb_file, mutation_result=mutation_result, sequence=sequence)

    return render_template("index.html", pdb_file=TOPOL_FILE, sequence=sequence)

if __name__ == "__main__":
    app.run(debug=True)