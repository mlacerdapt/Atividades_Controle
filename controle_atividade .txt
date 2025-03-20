from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

EXCEL_FILE = "tarefas.xlsx"

def ler_tarefas():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["Numero SAP", "Atividade", "Inicio", "Fim"])
        df.to_excel(EXCEL_FILE, index=False)
    return pd.read_excel(EXCEL_FILE)

def salvar_tarefas(df):
    df.to_excel(EXCEL_FILE, index=False)

@app.route("/")
def home():
    df = ler_tarefas()
    return render_template("index.html", tarefas=df, pd=pd) # Passa 'pd' para o template

@app.route("/iniciar", methods=["POST"])
def iniciar():
    numero_sap = request.form["numero_sap"]
    atividade = request.form["atividade"]
    df = ler_tarefas()

    if not ((df["Numero SAP"] == numero_sap) & (df["Fim"].isnull())).any():
        nova_tarefa = {"Numero SAP": numero_sap, "Atividade": atividade, "Inicio": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "Fim": None}
        df = pd.concat([df, pd.DataFrame([nova_tarefa])], ignore_index=True)
        salvar_tarefas(df)
        return redirect(url_for("home"))
    else:
        return "Tarefa já em andamento"

@app.route("/finalizar", methods=["POST"])
def finalizar():
    numero_sap = request.form["numero_sap"]
    df = ler_tarefas()

    print(f"Número SAP: {numero_sap}")

    # Converta a coluna 'Numero SAP' para string para garantir a comparação correta
    df['Numero SAP'] = df['Numero SAP'].astype(str)

    if ((df["Numero SAP"] == numero_sap) & (df["Fim"].isnull())).any():
        print("Tarefa encontrada e em andamento.")
        df.loc[(df["Numero SAP"] == numero_sap) & (df["Fim"].isnull()), "Fim"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        salvar_tarefas(df)
        print("Tarefa finalizada e salva.")
    else:
        print("Tarefa não encontrada ou já finalizada.")
        # Adicione esta verificação para depuração
        if (df["Numero SAP"] == numero_sap).any():
            print("Tarefa encontrada, mas já finalizada.")
        else:
            print("Tarefa não encontrada.")

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="192.168.221.32", port=5000)