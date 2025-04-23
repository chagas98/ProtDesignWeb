from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Carrega a lookup table de estabilidade
with open("data/stability_lookup.json") as f:
    stability_data = json.load(f)

THRESHOLD = 0.0  # valor fictício de threshold para decidir entre estável/instável

@app.route("/", methods=["GET", "POST"])
def index():
    mutation_result = None
    if request.method == "POST":
        position = request.form["position"]
        original = request.form["original"]
        mutant = request.form["mutant"]

        key = f"{original}{position}{mutant}"  # Ex: A123V
        stability = stability_data.get(key)

        if stability is not None:
            if stability >= THRESHOLD:
                pdb_file = "topol.pdb"
                mutation_result = f"A mutação {key} é considerada **ESTÁVEL** (ΔΔG={stability})"
            else:
                pdb_file = "unstable.pdb"
                mutation_result = f"A mutação {key} é considerada **INSTÁVEL** (ΔΔG={stability})"
        else:
            pdb_file = "topol.pdb"
            mutation_result = f"Mutação {key} não encontrada. Exibindo estrutura original."

        return render_template("index.html", pdb_file=pdb_file, mutation_result=mutation_result)

    return render_template("index.html", pdb_file="topol.pdb")

if __name__ == "__main__":
    app.run(debug=True)