import customtkinter as ctk
import re
import mysql.connector
from datetime import datetime
import uuid
#import qrcode          # NOVO
#from PIL import Image  # NOVO


# CONFIGURAÇÃO DA TELA

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

def formatar_data(event):
    if event.keysym in ("BackSpace", "Delete", "Left", "Right"): return
    campo = event.widget
    texto = campo.get()
    numeros = "".join(filter(str.isdigit, texto))[:8]
    resultado = ""
    for i, char in enumerate(numeros):
        if i in (2, 4): resultado += "/"
        resultado += char
    campo.delete(0, "end")
    campo.insert(0, resultado)

def formatar_decimal(event):
    campo = event.widget
    texto = campo.get()
    texto = re.sub(r"[^0-9.]", "", texto)
    if texto.count(".") > 1:
        partes = texto.split(".")
        texto = partes[0] + "." + "".join(partes[1:])
    padrao = r'^\d{0,3}(\.\d{0,2})?$'
    if not re.match(padrao, texto):
        if "." in texto:
            inteiro, decimal = texto.split(".", 1)
            texto = inteiro[:2] + "." + decimal[:2]
        else:
            texto = texto[:2]
    campo.delete(0, "end")
    campo.insert(0, texto)

def formatar_hora(event):
    if event.keysym in ("BackSpace", "Delete", "Left", "Right"): return
    campo = event.widget
    texto = campo.get()
    numeros = "".join(filter(str.isdigit, texto))[:4]
    resultado = ""
    for i, char in enumerate(numeros):
        if i == 2: resultado += ":"
        resultado += char
    if len(numeros) >= 2 and int(numeros[:2]) > 23: resultado = "23:"
    if len(numeros) == 4 and int(numeros[2:4]) > 59: resultado = numeros[:2] + ":59"
    campo.delete(0, "end")
    campo.insert(0, resultado)

# SALVAR NO DB
def store_database():
    nome = entry_nome.get()
    idade = entry_idade.get()
    risco = risco_var.get()
    hora = entry_hora.get()
    
    if not (nome and idade and risco and hora):
        feedback_label.configure(text="PREENCHA TODOS OS CAMPOS OBRIGATÓRIOS!", text_color="#D32F2F")
        return

    try:
        data_nasc = datetime.strptime(idade, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        feedback_label.configure(text="DATA DE NASCIMENTO INVÁLIDA!", text_color="#D32F2F")
        return

    try:
        mapa_risco = {"Vermelho": 1, "Laranja": 2, "Amarelo": 3, "Verde": 4, "Azul": 5}
        risco_id = mapa_risco.get(risco, 5)
        comorb_map = {item[0]: (1 if item[1].get() else 0) for item in variaveis1}

        conexao = mysql.connector.connect(host="163.176.235.85",port=3306,database="filago",user="substituir_usuario",password="substituir_senha")
        cursor = conexao.cursor()

        # INSERT DE PAC
        sql_atendimento = """
            INSERT INTO upa_atendimentos 
            (unidade_id, protocolo, senha, numero_senha, paciente_nome, paciente_data_nascimento, classificacao_risco_id, status_atual) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        proto = f"UPA1-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        senha_gerada = f"P-{str(uuid.uuid4())[:3].upper()}"
        
        cursor.execute(sql_atendimento, (1, proto, senha_gerada, 1, nome, data_nasc, risco_id, 'EM_TRIAGEM'))
        atendimento_id = cursor.lastrowid

        def clean_float(val):
            val = val.strip()
            return float(val) if val else None

        # INSERT DE TRIAGEM
        sql_triagem = """
            INSERT INTO upa_triagem 
            (atendimento_id, gestante, nivel_dor, saturacao, temperatura, pressao_arterial, peso, frequencia_cardiaca, alergias, queixa_observacao, hipertenso, diabetes, cancer, pneumopatia, tosse, outros_sintomas, prioridade_clinica) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        triagem_vals = (
            atendimento_id,
            1 if var_gestante.get() == "S" else 0,
            int(combobox_dor.get()) if combobox_dor.get().isdigit() else None,
            clean_float(entry_saturacao.get()),
            clean_float(entry_temp.get()),
            entry_pa.get(),
            clean_float(entry_peso.get()),
            clean_float(entry_fa.get()),
            entry_Alergia.get("1.0", "end-1c"),
            entry_Antecedentes.get("1.0", "end-1c"),
            comorb_map.get("hipertenso", 0),
            comorb_map.get("diabetes", 0),
            comorb_map.get("cancer", 0),
            comorb_map.get("pneumopatia", 0),
            comorb_map.get("tosse", 0),
            comorb_map.get("outros", 0),
            comorb_map.get("PRIORIDADE", 0)
        )

        cursor.execute(sql_triagem, triagem_vals)
        conexao.commit()
        
        feedback_label.configure(text="✔️ CADASTRO REALIZADO COM SUCESSO!", text_color="#15803D")

        # GERA QR CODE
        url_paciente = f"http://163.176.235.85:5000/?protocolo={proto}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url_paciente)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        janela_qr = ctk.CTkToplevel(app) 
        janela_qr.title(f"Protocolo - {nome}")
        janela_qr.geometry("400x450")
        janela_qr.attributes("-topmost", True)
        
        ctk_img = ctk.CTkImage(light_image=img_qr.get_image(), dark_image=img_qr.get_image(), size=(300, 300))
        lbl_qr = ctk.CTkLabel(janela_qr, image=ctk_img, text="")
        lbl_qr.pack(pady=20)
        
        lbl_info = ctk.CTkLabel(janela_qr, text=f"Protocolo: {proto}\nEntregue ao paciente para scanear.", font=("Arial", 14, "bold"), text_color="#1E293B")
        lbl_info.pack()

        # Limpar os campos principais - opcional
        entry_nome.delete(0, 'end')
        entry_idade.delete(0, 'end')
        
    except Exception as e:
        if 'conexao' in locals(): conexao.rollback()
        feedback_label.configure(text=f"❌ ERRO: {str(e)}", text_color="#D32F2F")
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()

# INTERFACE GRÁFICA
app = ctk.CTk()
app.title("Cadastro de Paciente")
app.geometry("1100x700")

header_frame = ctk.CTkFrame(app, height=60, corner_radius=0, fg_color="#1E293B")
header_frame.pack(fill="x", side="top")

header_title = ctk.CTkLabel(header_frame, text="NOVO CADASTRO", font=("Arial", 16, "bold"), text_color="#F8FAFC")
header_title.pack(side="left", padx=20, pady=15)

scroll_frame = ctk.CTkScrollableFrame(app, fg_color="transparent")
scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

scroll_frame.columnconfigure(0, weight=1)
scroll_frame.columnconfigure(1, weight=1)

# DADOS DO PACIENTE
card_paciente = ctk.CTkFrame(scroll_frame, corner_radius=12, fg_color="#F1F5F9", border_width=1, border_color="#E2E8F0")
card_paciente.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

ctk.CTkLabel(card_paciente, text="DADOS DO PACIENTE", font=("Arial", 14, "bold"), text_color="#334155").grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")

ctk.CTkLabel(card_paciente, text="Nome Completo*", font=("Arial", 12, "bold"), text_color="#64748B").grid(row=1, column=0, padx=15, pady=(5,0), sticky="w")
entry_nome = ctk.CTkEntry(card_paciente, width=300, height=35)
entry_nome.grid(row=2, column=0, columnspan=2, padx=15, pady=(0,10), sticky="w")

ctk.CTkLabel(card_paciente, text="Nascimento (DD/MM/AAAA)*", font=("Arial", 12, "bold"), text_color="#64748B").grid(row=3, column=0, padx=15, pady=(5,0), sticky="w")
entry_idade = ctk.CTkEntry(card_paciente, width=140, height=35)
entry_idade.grid(row=4, column=0, padx=15, pady=(0,10), sticky="w")
entry_idade.bind("<KeyRelease>", formatar_data)

ctk.CTkLabel(card_paciente, text="Hora Chegada*", font=("Arial", 12, "bold"), text_color="#64748B").grid(row=3, column=1, padx=15, pady=(5,0), sticky="w")
entry_hora = ctk.CTkEntry(card_paciente, width=140, height=35, placeholder_text="00:00")
entry_hora.grid(row=4, column=1, padx=15, pady=(0,10), sticky="w")
entry_hora.bind("<KeyRelease>", formatar_hora)

ctk.CTkLabel(card_paciente, text="Paciente Gestante?", font=("Arial", 12, "bold"), text_color="#64748B").grid(row=5, column=0, padx=15, pady=(5,0), sticky="w")
var_gestante = ctk.StringVar(value="N")
frame_gestante = ctk.CTkFrame(card_paciente, fg_color="transparent")
frame_gestante.grid(row=6, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="w")
ctk.CTkRadioButton(frame_gestante, text='Não', variable=var_gestante, value="N").pack(side="left", padx=(0, 15))
ctk.CTkRadioButton(frame_gestante, text='Sim', variable=var_gestante, value="S").pack(side="left")

# INFORMAÇÕES
card_sinais = ctk.CTkFrame(scroll_frame, corner_radius=12, fg_color="#F1F5F9", border_width=1, border_color="#E2E8F0")
card_sinais.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

ctk.CTkLabel(card_sinais, text="INFORMAÇÕES", font=("Arial", 14, "bold"), text_color="#334155").grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")

ctk.CTkLabel(card_sinais, text="Nível de Dor (0-10)", font=("Arial", 12, "bold"), text_color="#64748B").grid(row=1, column=0, padx=15, pady=(5,0), sticky="w")
combobox_dor = ctk.CTkComboBox(card_sinais, values=["0","1","2","3","4","5","6","7","8","9","10"], width=140, height=35)
combobox_dor.grid(row=2, column=0, padx=15, pady=(0,10), sticky="w")

ctk.CTkLabel(card_sinais, text="Saturação (%)", font=("Arial", 12, "bold"), text_color="#64748B").grid(row=1, column=1, padx=15, pady=(5,0), sticky="w")
entry_saturacao = ctk.CTkEntry(card_sinais, width=140, height=35)
entry_saturacao.grid(row=2, column=1, padx=15, pady=(0,10), sticky="w")
entry_saturacao.bind("<KeyRelease>", formatar_decimal)

ctk.CTkLabel(card_sinais, text="Temp. (°C)", font=("Arial", 12, "bold"), text_color="#64748B").grid(row=3, column=0, padx=15, pady=(5,0), sticky="w")
entry_temp = ctk.CTkEntry(card_sinais, width=140, height=35)
entry_temp.grid(row=4, column=0, padx=15, pady=(0,10), sticky="w")
entry_temp.bind("<KeyRelease>", formatar_decimal)

ctk.CTkLabel(card_sinais, text="Pressão Arterial", font=("Arial", 12, "bold"), text_color="#64748B").grid(row=3, column=1, padx=15, pady=(5,0), sticky="w")
entry_pa = ctk.CTkEntry(card_sinais, width=140, height=35, placeholder_text="Ex: 120/80")
entry_pa.grid(row=4, column=1, padx=15, pady=(0,10), sticky="w")
entry_pa.bind("<KeyRelease>", formatar_decimal) # Opcional: ajustar regex se PA usar barra (/)

ctk.CTkLabel(card_sinais, text="Peso (Kg)", font=("Arial", 12, "bold"), text_color="#64748B").grid(row=5, column=0, padx=15, pady=(5,0), sticky="w")
entry_peso = ctk.CTkEntry(card_sinais, width=140, height=35)
entry_peso.grid(row=6, column=0, padx=15, pady=(0,15), sticky="w")
entry_peso.bind("<KeyRelease>", formatar_decimal)

ctk.CTkLabel(card_sinais, text="Freq. Cardíaca", font=("Arial", 12, "bold"), text_color="#64748B").grid(row=5, column=1, padx=15, pady=(5,0), sticky="w")
entry_fa = ctk.CTkEntry(card_sinais, width=140, height=35)
entry_fa.grid(row=6, column=1, padx=15, pady=(0,15), sticky="w")
entry_fa.bind("<KeyRelease>", formatar_decimal)


#HISTÓRICO E COMORBIDADES
card_historico = ctk.CTkFrame(scroll_frame, corner_radius=12, fg_color="#F1F5F9", border_width=1, border_color="#E2E8F0")
card_historico.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

ctk.CTkLabel(card_historico, text="HISTÓRICO E QUEIXAS", font=("Arial", 14, "bold"), text_color="#334155").pack(anchor="w", padx=15, pady=(15, 10))

frame_checks = ctk.CTkFrame(card_historico, fg_color="transparent")
frame_checks.pack(fill="x", padx=15, pady=(0, 10))

variaveis1 = []
comorbidades = ["hipertenso", "alergia", "diabetes", "tosse", "cancer", "outros", "pneumopatia", "PRIORIDADE"]

for idx, item in enumerate(comorbidades):
    var_chk = ctk.BooleanVar()
    chk = ctk.CTkCheckBox(frame_checks, text=item.capitalize(), variable=var_chk)
    chk.grid(row=idx // 2, column=idx % 2, padx=10, pady=5, sticky="w")
    variaveis1.append((item, var_chk))

ctk.CTkLabel(card_historico, text="Alergias (Descrição)", font=("Arial", 12, "bold"), text_color="#64748B").pack(anchor="w", padx=15, pady=(5,0))
entry_Alergia = ctk.CTkTextbox(card_historico, height=45)
entry_Alergia.pack(fill="x", padx=15, pady=(0, 10))

ctk.CTkLabel(card_historico, text="Queixa Principal / Observações", font=("Arial", 12, "bold"), text_color="#64748B").pack(anchor="w", padx=15, pady=(5,0))
entry_Antecedentes = ctk.CTkTextbox(card_historico, height=65)
entry_Antecedentes.pack(fill="x", padx=15, pady=(0, 15))


#CLASSIFICAÇÃO DE RISCO
card_risco = ctk.CTkFrame(scroll_frame, corner_radius=12, fg_color="#F1F5F9", border_width=1, border_color="#E2E8F0")
card_risco.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

ctk.CTkLabel(card_risco, text="CLASSIFICAÇÃO DE RISCO (MANCHESTER)", font=("Arial", 14, "bold"), text_color="#334155").pack(anchor="w", padx=15, pady=(15, 15))

risco_var = ctk.StringVar(value="")
opcoes_risco = [
    ("VERMELHO - Necessidade de atendimento imediato", "Vermelho", "#DC2626"),
    ("LARANJA - Muito urgente", "Laranja", "#EA580C"),
    ("AMARELO - Necessita de atendimento rápido", "Amarelo", "#CA8A04"),
    ("VERDE - Pouco urgente", "Verde", "#16A34A"),
    ("AZUL - Não urgente", "Azul", "#2563EB")
]

for texto, valor, cor in opcoes_risco:
    ctk.CTkRadioButton(card_risco,text=texto,variable=risco_var,value=valor,fg_color=cor,hover_color=cor,font=("Arial", 13)).pack(anchor="w", padx=20, pady=8)


# BOTÃO AÇÕES E FEEDBACK
bottom_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
bottom_frame.grid(row=2, column=0, columnspan=2, pady=20)

feedback_label = ctk.CTkLabel(bottom_frame, text="", font=("Arial", 14, "bold"))
feedback_label.pack(pady=(0, 10))

btn_confirmar = ctk.CTkButton(bottom_frame,text="SALVAR CADASTRO E GERAR QR CODE",height=45,width=350,font=("Arial", 14, "bold"),command=store_database,fg_color="#16A34A",hover_color="#15803D")
btn_confirmar.pack()

app.mainloop()