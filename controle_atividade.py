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
    return render_template("index.html", tarefas=df, pd=pd)

@app.route("/iniciar", methods=["POST"])
def iniciar():
    atividade = request.form["atividade"]
    numero_sap = request.form["numero_sap"]
    df = ler_tarefas()

    if not ((df["Numero SAP"] == numero_sap) & (df["Atividade"] == atividade) & (df["Fim"].isnull())).any():
        nova_tarefa = {"Numero SAP": numero_sap, "Atividade": atividade, "Inicio": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "Fim": None}
        df = pd.concat([df, pd.DataFrame([nova_tarefa])], ignore_index=True)
        salvar_tarefas(df)

        # Criar arquivo individual para a tarefa
        nome_arquivo = f"{numero_sap}_{atividade}.txt"
        with open(nome_arquivo, "w") as arquivo_tarefa:
            arquivo_tarefa.write(f"Numero SAP: {numero_sap}\n")
            arquivo_tarefa.write(f"Atividade: {atividade}\n")
            arquivo_tarefa.write(f"Inicio: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            arquivo_tarefa.write("Fim: None\n")

        return redirect(url_for("home"))
    else:
        return "Tarefa já em andamento"

@app.route("/finalizar", methods=["POST"])
def finalizar():
    numero_sap = request.form["numero_sap"]
    atividade = request.form["atividade"]
    df = ler_tarefas()

    df['Numero SAP'] = df['Numero SAP'].astype(str)

    if ((df["Numero SAP"] == numero_sap) & (df["Atividade"] == atividade) & (df["Fim"].isnull())).any():
        df.loc[(df["Numero SAP"] == numero_sap) & (df["Atividade"] == atividade) & (df["Fim"].isnull()), "Fim"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        salvar_tarefas(df)

        nome_arquivo = f"{numero_sap}_{atividade}.txt"
        if os.path.exists(nome_arquivo):
            with open(nome_arquivo, "a") as arquivo_tarefa:
                arquivo_tarefa.write(f"Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="192.168.221.32", port=5000)