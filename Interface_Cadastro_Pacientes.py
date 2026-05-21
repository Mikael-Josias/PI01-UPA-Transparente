import customtkinter as ctk
import re
import mysql.connector
from datetime import datetime
import uuid
import qrcode          # NOVO
from PIL import Image  # NOVO

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

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

def store_database():
    nome = entry_nome.get()
    idade = entry_idade.get()
    risco = risco_var.get()
    hora = entry_hora.get()
   
    if not (nome and idade and risco and hora):
        feedback_label.configure(text="PREENCHA TODOS OS CAMPOS OBRIGATÓRIOS!", text_color="red")
        return

    try:
        data_nasc = datetime.strptime(idade, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        feedback_label.configure(text="DATA DE NASCIMENTO INVÁLIDA!", text_color="red")
        return

    try:
        mapa_risco = {"Vermelho": 1, "Laranja": 2, "Amarelo": 3, "Verde": 4, "Azul": 5}
        risco_id = mapa_risco.get(risco, 5)
        comorb_map = {item[0]: (1 if item[1].get() else 0) for item in variaveis1}

        conexao = mysql.connector.connect(
            host="163.176.235.85",
            port=3306,
            database="filago",
            user="PREENCHER USUARIO",
            password="PREENCHER SENHA!"
        )
        cursor = conexao.cursor()

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

        sql_triagem = """
            INSERT INTO upa_triagem 
            (atendimento_id, gestante, nivel_dor, saturacao, temperatura, pressao_arterial, peso, frequencia_cardiaca, alergias, queixa_observacao, hipertenso, diabetes, cancer, pneumopatia, tosse, outros_sintomas, prioridade_clinica) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        triagem_vals = (
            atendimento_id,
            1 if var.get() == "S" else 0,
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
        
        feedback_label.configure(text="PACIENTE INSERIDO NO BANCO", text_color="green")

        # =========================================================
        # GERAÇÃO DO QR CODE E ABERTURA DO POP-UP
        # =========================================================
        url_paciente = f"http://163.176.235.85:5000/?protocolo={proto}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url_paciente)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        # Cria a janela pop-up
        janela_qr = ctk.CTkToplevel(app) # amarrado à janela principal 'app'
        janela_qr.title(f"Protocolo - {nome}")
        janela_qr.geometry("400x450")
        janela_qr.attributes("-topmost", True) # Mantém por cima
        
        # Exibe a imagem
        ctk_img = ctk.CTkImage(light_image=img_qr.get_image(), dark_image=img_qr.get_image(), size=(300, 300))
        lbl_qr = ctk.CTkLabel(janela_qr, image=ctk_img, text="")
        lbl_qr.pack(pady=20)
        
        # Texto de instrução
        lbl_info = ctk.CTkLabel(janela_qr, text=f"Protocolo: {proto}\nMostre ao paciente ou imprima.", font=("Roboto", 14, "bold"))
        lbl_info.pack()
        # =========================================================

    except Exception as e:
        if 'conexao' in locals(): conexao.rollback()
        feedback_label.configure(text=f"ERRO: {str(e)}", text_color="red")
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()

app = ctk.CTk()
app.title("CADASTRO DE PACIENTE")
app.geometry("890x490")

scroll_frame = ctk.CTkScrollableFrame(app)
scroll_frame.pack(fill="both", expand=True)

label_nome = ctk.CTkLabel(scroll_frame, text="NOME DO PACIENTE / SENHA",font=("Roboto", 13, "bold"))
label_nome.grid(row=0,column=0, padx=1, pady=(1,0))

entry_nome = ctk.CTkEntry(scroll_frame, width=200, placeholder_text="Nome completo")
entry_nome.grid(row=1,column=0, padx=1, pady=(0,1))

label_idade = ctk.CTkLabel(scroll_frame, text="DATA DE NASCIMENTO",font=("Roboto", 13, "bold"))
label_idade.grid(row=2,column=0, padx=1, pady=(1,0),sticky="w")

entry_idade = ctk.CTkEntry(scroll_frame, placeholder_text="Data de nascimento")
entry_idade.grid(row=3,column=0, padx=1, pady=(0,1),sticky="w")
entry_idade.bind("<KeyRelease>", formatar_data)

label_hora = ctk.CTkLabel(scroll_frame, text="HORÁRIO DE CHEGADA",font=("Roboto", 13, "bold"))
label_hora.grid(row=4,column=0, padx=1, pady=(1,0),sticky="w")

entry_hora = ctk.CTkEntry(scroll_frame, placeholder_text="Ex: 14:30")
entry_hora.grid(row=5,column=0, padx=1,pady=(0,1),sticky="w")
entry_hora.bind("<KeyRelease>", formatar_hora)

label_gestante = ctk.CTkLabel(scroll_frame, text="GESTANTE",font=("Roboto", 13, "bold"))
label_gestante.grid(row=6,column=0, padx=1, pady=(1,0),sticky="w")

var = ctk.StringVar(value="")
gestantey = ctk.CTkRadioButton(scroll_frame, text='Sim', variable = var, value = "S")
gestantey.grid(row=7,column=0,padx=1,pady=(0,1),sticky="w")

gestanten = ctk.CTkRadioButton(scroll_frame, text='Nao', variable = var, value = "N")
gestanten.grid(row=8,column=0,padx=1,pady=(0,1),sticky="w")

label_dor = ctk.CTkLabel(scroll_frame, text="NÍVEL DE DOR",font=("Roboto", 13, "bold"))
label_dor.grid(row=0, column=3, padx=1,pady=(1,0))

combobox_dor = ctk.CTkComboBox(scroll_frame,values=["1","2","3","4","5","6","7","8","9","10"] )
combobox_dor.grid(row=1, column=3, padx=1, pady=(0,1))

label_saturacao = ctk.CTkLabel(scroll_frame, text="SATURAÇÃO",font=("Roboto", 13, "bold"))
label_saturacao.grid(row=2, column=3, padx=1,pady=(1,0))

entry_saturacao = ctk.CTkEntry(scroll_frame, placeholder_text="Saturação")
entry_saturacao.grid(row=3, column=3, padx=1,pady=(0,1))
entry_saturacao.bind("<KeyRelease>", formatar_decimal)

label_temp = ctk.CTkLabel(scroll_frame, text="TEMPERATURA EM CELSIUS",font=("Roboto", 13, "bold"))
label_temp.grid(row=0, column=4, padx=1,pady=(1,0))

entry_temp = ctk.CTkEntry(scroll_frame, placeholder_text="temperatura em celsius")
entry_temp.grid(row=1, column=4, padx=1,pady=(0,1))
entry_temp.bind("<KeyRelease>", formatar_decimal)

label_pa = ctk.CTkLabel(scroll_frame, text="PRESSÃO ARTERIAL",font=("Roboto", 13, "bold"))
label_pa.grid(row=2, column=4, padx=1,pady=(1,0))

entry_pa = ctk.CTkEntry(scroll_frame, placeholder_text="Pressão arterial")
entry_pa.grid(row=3, column=4, padx=1,pady=(0,1))
entry_pa.bind("<KeyRelease>", formatar_decimal)

label_peso = ctk.CTkLabel(scroll_frame, text="PESO",font=("Roboto", 13, "bold"))
label_peso.grid(row=4, column=3, padx=1,pady=(1,0))

entry_peso = ctk.CTkEntry(scroll_frame, placeholder_text="Peso")
entry_peso.grid(row=5, column=3, padx=1,pady=(0,1))
entry_peso.bind("<KeyRelease>", formatar_decimal)

label_fa = ctk.CTkLabel(scroll_frame, text="FREQUÊNCIA CARDÍACA",font=("Roboto", 13, "bold"))
label_fa.grid(row=4, column=4, padx=1,pady=(1,0))

entry_fa = ctk.CTkEntry(scroll_frame, placeholder_text="Frequência cardíaca")
entry_fa.grid(row=5, column=4, padx=1,pady=(0,1))
entry_fa.bind("<KeyRelease>", formatar_decimal)

label_Alergia = ctk.CTkLabel(scroll_frame, text="ALERGIAS",font=("Roboto", 13, "bold"))
label_Alergia.grid(row=6, column=3,columnspan=2, padx=1,pady=(1,0))

entry_Alergia = ctk.CTkTextbox(scroll_frame, height=5)
entry_Alergia.grid(row=7, column=3,columnspan=2,sticky="ew", padx=1,pady=(0,1))

label_Antecedentes = ctk.CTkLabel(scroll_frame, text="QUEIXA/OBSERVAÇÃO",font=("Roboto", 13, "bold"))
label_Antecedentes.grid(row=8, column=3,columnspan=2, padx=1,pady=(1,0))

entry_Antecedentes = ctk.CTkTextbox(scroll_frame, height=50)
entry_Antecedentes.grid(row=9, column=3,columnspan=2,sticky="ew", padx=1,pady=(0,1))

btn_confirmar = ctk.CTkButton(scroll_frame, text="CONFIRMAR", command=store_database)
btn_confirmar.grid(row=11,column=3,columnspan=2, padx=1, pady=1, sticky="ew")

label_comorbidades = ctk.CTkLabel(scroll_frame, text = "COMORBIDADES",font=("Roboto", 13, "bold"))
label_comorbidades.grid(row=9, column=0, padx=1, pady=1)

comorbidades1 = ["hipertenso","diabetes","cancer","pneumopatia"]
variaveis1 = []

for idx, i in enumerate(comorbidades1):
    var2 = ctk.BooleanVar()
    chk = ctk.CTkCheckBox(scroll_frame, text=i, variable=var2)
    chk.grid(row =idx+ 10, column = 0, padx=1,pady=(0,1) , sticky="w")
    variaveis1.append((i, var2))

comorbidades2 = ["alergia","tosse","outros", "PRIORIDADE"]

for idx, i in enumerate(comorbidades2):
    var3 = ctk.BooleanVar()
    chk = ctk.CTkCheckBox(scroll_frame, text=i, variable=var3)
    chk.grid(row =idx+ 10, column = 1, padx=1,pady=(0,1), sticky="w")
    variaveis1.append((i, var3))

label_risco = ctk.CTkLabel(scroll_frame, text="CLASSIFICAÇÃO DE RISCO",font=("Roboto", 13, "bold"))
label_risco.grid(row=1,column=1, padx=1, pady=(1,0))
risco_var = ctk.StringVar(value="")

ctk.CTkRadioButton(scroll_frame,text="VERMELHO - Necessidade de atendimento imediato",variable=risco_var,value="Vermelho",fg_color="red").grid(row=2,column=1, padx=1, pady=1, sticky="w")
ctk.CTkRadioButton(scroll_frame,text="LARANJA - Muito urgente",variable=risco_var,value="Laranja",fg_color="orange").grid(row=3,column=1, padx=1, pady=1, sticky="w")
ctk.CTkRadioButton(scroll_frame,text="AMARELO - Necessita de atendimento rápido",variable=risco_var,value="Amarelo",fg_color="yellow").grid(row=4,column=1, padx=1, pady=1, sticky="w")
ctk.CTkRadioButton(scroll_frame,text="VERDE - Pouco urgente",variable=risco_var,value="Verde",fg_color="green").grid(row=5,column=1, padx=1, pady=1, sticky="w")
ctk.CTkRadioButton(scroll_frame,text="AZUL - Não urgente",variable=risco_var,value="Azul",fg_color="blue").grid(row=6,column=1, padx=1, pady=1, sticky="w")

feedback_label = ctk.CTkLabel(scroll_frame, text="")
feedback_label.grid(row=15,column=1,columnspan=2, padx=1,pady=(10,10),sticky="w")

app.mainloop()