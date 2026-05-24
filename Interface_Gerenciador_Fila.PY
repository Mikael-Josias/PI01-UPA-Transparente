import customtkinter as ctk
import mysql.connector
from tkinter import messagebox

paciente_id = None

# CONFIGURAÇÃO DA TELA

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# BANCO DE DADOS
def get_db_connection():
    return mysql.connector.connect(host="163.176.235.85",port=3306,database="filago",user="substituir_usuario",password="substituir_senha")

# FUNÇÕES DE BUSCA E ATUALIZAÇÃO DE STATUS E SETOR
def buscar_paciente():
    global paciente_id
    nome_busca = entry_nome.get().strip()
    
    if not nome_busca:
        feedback_label.configure(text="Digite um nome para pesquisar!", text_color="#D32F2F")
        return
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT id, paciente_nome, status_atual, especialidade 
            FROM upa_atendimentos 
            WHERE paciente_nome LIKE %s 
            ORDER BY chegada_em DESC LIMIT 1
        """
        cursor.execute(query, (f"%{nome_busca}%",))
        paciente = cursor.fetchone()
        
        if paciente:
            paciente_id = paciente['id']
            
            # Atualiza os blocos do cartão visual de dados de forma limpa
            lbl_info_nome.configure(text=f"{paciente['paciente_nome']}", text_color="#1E293B")
            lbl_info_status.configure(text=f"{paciente['status_atual']}", text_color="#2563EB")
            lbl_info_espec.configure(text=f"{paciente['especialidade'] or 'Não definida'}", text_color="#475569")
            
            feedback_label.configure(text="Paciente localizado!", text_color="#15803D")
        else:
            paciente_id = None
            limpar_card_paciente()
            feedback_label.configure(text="Paciente não encontrado.", text_color="#D32F2F")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        feedback_label.configure(text=f"Erro no banco: {e}", text_color="#D32F2F")


def atualizar_fila():
    global paciente_id
    if not paciente_id:
        feedback_label.configure(text="Selecione um paciente primeiro!", text_color="#D32F2F")
        return
        
    setor_selecionado = combobox_FILA.get()
    status_novo = ""
    especialidade_nova = "Clínico Geral" 
    
    if setor_selecionado == 'RECEPÇÃO':
        status_novo = 'AGUARDANDO_RECEPCAO'
    elif setor_selecionado == 'CLASSIFICAÇÃO':
        status_novo = 'EM_TRIAGEM'
    elif setor_selecionado == 'CLÍNICO':
        status_novo = 'AGUARDANDO_ATENDIMENTO'
        especialidade_nova = 'Clínico Geral'
    elif setor_selecionado == 'PEDIATRA':
        status_novo = 'AGUARDANDO_ATENDIMENTO'
        especialidade_nova = 'Pediatria'
    elif setor_selecionado == 'ORTOPEDIA':
        status_novo = 'AGUARDANDO_ATENDIMENTO'
        especialidade_nova = 'Ortopedia'
    elif setor_selecionado == 'PEDIATRA':
        status_novo = 'AGUARDANDO_ATENDIMENTO'
        especialidade_nova = 'Pediatria'
    elif setor_selecionado == 'ODONTO':
        status_novo = 'AGUARDANDO_ATENDIMENTO'
        especialidade_nova = 'Odontologia'
    elif setor_selecionado == 'MEDICAÇÃO':
        status_novo = 'AGUARDANDO_MEDICACAO'
    else:
        feedback_label.configure(text="Selecione um setor válido.", text_color="#D32F2F")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query_update = """
            UPDATE upa_atendimentos 
            SET status_atual = %s, especialidade = %s 
            WHERE id = %s
        """
        cursor.execute(query_update, (status_novo, especialidade_nova, paciente_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # POP UP
        messagebox.showinfo("Setor Atualizado", f"O setor do paciente foi atualizado com sucesso para: {setor_selecionado}")
        
        feedback_label.configure(text=f"Movido para {setor_selecionado}", text_color="#15803D")
        buscar_paciente()
        
    except Exception as e:
        feedback_label.configure(text=f"Erro ao atualizar: {e}", text_color="#D32F2F")


def finalizar_atendimento():
    global paciente_id
    if not paciente_id:
        feedback_label.configure(text="Selecione um paciente primeiro!", text_color="#D32F2F")
        return
        
    resposta = messagebox.askyesno(
        "Confirmar Encerramento", 
        "Tem certeza que deseja FINALIZAR o atendimento deste paciente?\nEle sairá do painel público em tempo real."
    )
    
    if resposta:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query_update = """
                UPDATE upa_atendimentos 
                SET status_atual = 'FINALIZADO'
                WHERE id = %s
            """
            cursor.execute(query_update, (paciente_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            messagebox.showinfo("Atendimento Encerrado", "O atendimento do paciente foi finalizado e arquivado.")
            feedback_label.configure(text="✔️ Atendimento FINALIZADO!", text_color="#15803D")
            
            entry_nome.delete(0, 'end')
            limpar_card_paciente()
            paciente_id = None
            
        except Exception as e:
            feedback_label.configure(text=f"Erro ao finalizar: {e}", text_color="#D32F2F")

def limpar_card_paciente():
    lbl_info_nome.configure(text="Nenhum paciente selecionado", text_color="#94A3B8")
    lbl_info_status.configure(text="-", text_color="#94A3B8")
    lbl_info_espec.configure(text="-", text_color="#94A3B8")

# INTERFACE
app = ctk.CTk()
app.title("Gerenciador de atendimento")
app.geometry("980x540")
app.resizable(False, False)

# FRAME
header_frame = ctk.CTkFrame(app, height=60, corner_radius=0, fg_color="#1E293B")
header_frame.pack(fill="x", side="top")

header_title = ctk.CTkLabel(header_frame,text="PAINEL DE ATENDIMENTO",font=("Arial", 16, "bold"),text_color="#F8FAFC")
header_title.pack(side="left", padx=20, pady=15)

#CONTAINER
main_container = ctk.CTkFrame(app, fg_color="transparent")
main_container.pack(fill="both", expand=True, padx=20, pady=20)

# EXIBIÇÃO DE PAINEL

left_panel = ctk.CTkFrame(main_container, width=420, corner_radius=12, fg_color="#F1F5F9", border_width=1, border_color="#E2E8F0")
left_panel.pack(side="left", fill="both", expand=False, padx=(0, 10))
left_panel.pack_propagate(False)

#Pesquisa
lbl_section1 = ctk.CTkLabel(left_panel, text="LOCALIZAR PACIENTE", font=("Arial", 13, "bold"), text_color="#334155")
lbl_section1.pack(anchor="w", padx=20, pady=(20, 5))

entry_nome = ctk.CTkEntry(left_panel, width=380, height=38, placeholder_text="Digite o nome completo do paciente...", font=("Arial", 13))
entry_nome.pack(padx=20, pady=5)
entry_nome.bind("<Return>", lambda e: buscar_paciente())

btn_pesquisar = ctk.CTkButton(left_panel, text="BUSCAR CADASTRO", height=38, font=("Arial", 12, "bold"), command=buscar_paciente, fg_color="#2563EB", hover_color="#1D4ED8")
btn_pesquisar.pack(fill="x", padx=20, pady=(5, 10))

feedback_label = ctk.CTkLabel(left_panel, text="Aguardando pesquisa...", font=("Arial", 12, "italic"), text_color="#64748B")
feedback_label.pack(anchor="w", padx=23, pady=0)

divider = ctk.CTkFrame(left_panel, height=2, fg_color="#E2E8F0")
divider.pack(fill="x", padx=20, pady=20)

lbl_section2 = ctk.CTkLabel(left_panel, text="ALTERAR SETOR", font=("Arial", 13, "bold"), text_color="#334155")
lbl_section2.pack(anchor="w", padx=20, pady=(0, 5))

combobox_FILA = ctk.CTkComboBox(left_panel,width=380,height=38,font=("Arial", 13),values=['RECEPÇÃO', 'CLASSIFICAÇÃO', 'CLÍNICO', 'PEDIATRA', 'ORTOPEDIA', 'ODONTO', 'MEDICAÇÃO'])
combobox_FILA.pack(padx=20, pady=5)

btn_atualizar = ctk.CTkButton(left_panel,text="MUDAR SETOR DO PACIENTE",height=40,font=("Arial", 12, "bold"),command=atualizar_fila,fg_color="#16A34A",hover_color="#15803D")
btn_atualizar.pack(fill="x", padx=20, pady=(10, 5))

# INFO PACIENTE


right_panel = ctk.CTkFrame(main_container, corner_radius=12, fg_color="#FFFFFF", border_width=1, border_color="#E2E8F0")
right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

card_paciente = ctk.CTkFrame(right_panel, corner_radius=10, fg_color="#F8FAFC", border_width=1, border_color="#E2E8F0")
card_paciente.pack(fill="both", expand=True, padx=20, pady=20)

lbl_card_title = ctk.CTkLabel(card_paciente, text="PRONTUÁRIO SELECIONADO", font=("Arial", 11, "bold"), text_color="#94A3B8")
lbl_card_title.pack(anchor="w", padx=20, pady=(20, 10))

#Nome
lbl_tag_nome = ctk.CTkLabel(card_paciente, text="NOME COMPLETO DO PACIENTE", font=("Arial", 11, "bold"), text_color="#64748B")
lbl_tag_nome.pack(anchor="w", padx=20, pady=(10, 0))

lbl_info_nome = ctk.CTkLabel(card_paciente, text="Nenhum paciente selecionado", font=("Arial", 18, "bold"), text_color="#475569")
lbl_info_nome.pack(anchor="w", padx=20, pady=(0, 15))

#Status
lbl_tag_status = ctk.CTkLabel(card_paciente, text="STATUS ATUAL NO FLUXO", font=("Arial", 11, "bold"), text_color="#64748B")
lbl_tag_status.pack(anchor="w", padx=20, pady=(10, 0))

lbl_info_status = ctk.CTkLabel(card_paciente, text="-", font=("Arial", 15, "bold"), text_color="#475569")
lbl_info_status.pack(anchor="w", padx=20, pady=(0, 15))

# SETOR
lbl_tag_espec = ctk.CTkLabel(card_paciente, text="ESPECIALIDADE MÉDICA DESIGNADA", font=("Arial", 11, "bold"), text_color="#64748B")
lbl_tag_espec.pack(anchor="w", padx=20, pady=(10, 0))

lbl_info_espec = ctk.CTkLabel(card_paciente, text="-", font=("Arial", 15, "bold"), text_color="#475569")
lbl_info_espec.pack(anchor="w", padx=20, pady=(0, 20))

# Botão DE ENCERRAMENTO DE ATENDIMENTO
btn_finalizar = ctk.CTkButton(card_paciente,text="FINALIZAR ATENDIMENTO (ALTA/ENCERRAMENTO)",height=42,font=("Arial", 12, "bold"),command=finalizar_atendimento,fg_color="#DC2626",hover_color="#B91C1C")
btn_finalizar.pack(fill="x", side="bottom", padx=20, pady=20)

#ABRE A INTERFACE
app.mainloop()