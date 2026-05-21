from flask import Flask, jsonify, render_template, request
import mysql.connector

app = Flask(__name__)

DB_CONFIG = {
    'host': '127.0.0.1', 
    'user': 'SUBSTITUIR USUARIO',
    'password': 'SUBSTITUIR SENHA!',
    'database': 'filago'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dados')
def api_dados():
    protocolo = request.args.get('protocolo')
    
    # Estrutura base de dados enviada para o Frontend
    dados = {
        "paciente": None,
        "posicao": None,       
        "total_setor": None,   
        "tempo_estimado": None,  # NOVO: Tempo estimado calculado no Backend
        "risco": {
            "emergencia": {"qtd": 0, "tempo": 0},
            "muitoUrgente": {"qtd": 0, "tempo": 0},
            "urgente": {"qtd": 0, "tempo": 0},
            "poucoUrgente": {"qtd": 0, "tempo": 0},
            "naoUrgente": {"qtd": 0, "tempo": 0}
        },
        "setores": {
            "recepcao": {"qtd": 0, "tempo": 0},
            "classificacao": {"qtd": 0, "tempo": 0},
            "clinico": {"qtd": 0, "tempo": 0},
            "pediatra": {"qtd": 0, "tempo": 0},
            "ortopedia": {"qtd": 0, "tempo": 0},
            "medicacao": {"qtd": 0, "tempo": 0}
        }
    }

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Puxa os dados do paciente lido no QR Code (se houver protocolo)
        if protocolo:
            query_paciente = """
                SELECT a.paciente_nome, a.status_atual, a.especialidade, a.chegada_em, cr.nome as classificacao_nome 
                FROM upa_atendimentos a 
                LEFT JOIN upa_classificacoes_risco cr ON a.classificacao_risco_id = cr.id 
                WHERE a.protocolo = %s
            """
            cursor.execute(query_paciente, (protocolo,))
            pac = cursor.fetchone()
            
            if pac:
                status_paciente = pac.get("status_atual", "")
                chegada_paciente = pac.get("chegada_em")
                
                posicao_fila = 1
                total_fila = 1
                tempo_estimado = 0
                
                # Calcula Posição e Total do Setor
                if status_paciente and chegada_paciente:
                    # Conta quem chegou antes no mesmo status (pessoas na frente)
                    cursor.execute("""
                        SELECT COUNT(*) as pos 
                        FROM upa_atendimentos 
                        WHERE status_atual = %s AND chegada_em < %s
                    """, (status_paciente, chegada_paciente))
                    res_pos = cursor.fetchone()
                    pessoas_na_frente = res_pos['pos'] if res_pos else 0
                    
                    posicao_fila = pessoas_na_frente + 1
                    # AJUSTE: Tempo estimado = Pessoas na frente x 5 minutos
                    tempo_estimado = pessoas_na_frente * 5
                    
                    # Conta o total inicial de pessoas nesse status específico
                    cursor.execute("""
                        SELECT COUNT(*) as tot 
                        FROM upa_atendimentos 
                        WHERE status_atual = %s
                    """, (status_paciente,))
                    res_tot = cursor.fetchone()
                    total_fila = res_tot['tot'] if res_tot else 1

                # Salva no dicionário final
                dados["paciente"] = {
                    "paciente_nome": pac.get("paciente_nome", ""),
                    "status_atual": status_paciente,
                    "especialidade": pac.get("especialidade", ""),
                    "classificacao_nome": pac.get("classificacao_nome") or "Aguardando Classificação"
                }
                dados["posicao"] = posicao_fila
                dados["total_setor"] = total_fila
                dados["tempo_estimado"] = tempo_estimado

        # 2. Puxa TODOS os pacientes ativos e cruza com a tabela de classificação de risco real
        query_todos = """
            SELECT a.status_atual, a.especialidade, cr.nome as classificacao_nome 
            FROM upa_atendimentos a 
            LEFT JOIN upa_classificacoes_risco cr ON a.classificacao_risco_id = cr.id 
            WHERE a.status_atual NOT IN ('FINALIZADO', 'EVASAO', 'CANCELADO')
        """
        cursor.execute(query_todos)
        todos = cursor.fetchall()
        
        for p in todos:
            status = str(p.get('status_atual', '')).lower()
            espec = str(p.get('especialidade', '')).lower()
            risco = str(p.get('classificacao_nome', '')).lower()
            
            # Conta Setores
            if 'recep' in status: 
                dados['setores']['recepcao']['qtd'] += 1
            elif 'triagem' in status or 'classifica' in status: 
                dados['setores']['classificacao']['qtd'] += 1
            elif 'atendimento' in status or 'medico' in status or 'médico' in status:
                if 'ped' in espec: dados['setores']['pediatra']['qtd'] += 1
                elif 'orto' in espec: dados['setores']['ortopedia']['qtd'] += 1
                else: dados['setores']['clinico']['qtd'] += 1
            elif 'medica' in status or 'observa' in status: 
                dados['setores']['medicacao']['qtd'] += 1

            # Conta Riscos
            if 'emerg' in risco: 
                dados['risco']['emergencia']['qtd'] += 1
            elif 'muito urgente' in risco: 
                dados['risco']['muitoUrgente']['qtd'] += 1
            elif 'pouco urgente' in risco: 
                dados['risco']['poucoUrgente']['qtd'] += 1
            elif 'urgente' in risco:  
                dados['risco']['urgente']['qtd'] += 1
            elif 'não' in risco or 'nao' in risco: 
                dados['risco']['naoUrgente']['qtd'] += 1

        # MODIFICAÇÃO COM O QUE CONVERSAMOS:
        # Se houver um paciente ativo, vincula o total_setor diretamente com a contagem real agrupada do setor dele
        if protocolo and pac:
            status_limpo = status_paciente.lower()
            espec_limpa = str(pac.get("especialidade", "")).lower()
            
            if 'recep' in status_limpo:
                dados["total_setor"] = dados['setores']['recepcao']['qtd']
            elif 'triagem' in status_limpo or 'classifica' in status_limpo:
                dados["total_setor"] = dados['setores']['classificacao']['qtd']
            elif 'atendimento' in status_limpo or 'medico' in status_limpo or 'médico' in status_limpo:
                if 'ped' in espec_limpa: dados["total_setor"] = dados['setores']['pediatra']['qtd']
                elif 'orto' in espec_limpa: dados["total_setor"] = dados['setores']['ortopedia']['qtd']
                else: dados["total_setor"] = dados['setores']['clinico']['qtd']
            elif 'medica' in status_limpo or 'observa' in status_limpo:
                dados["total_setor"] = dados['setores']['medicacao']['qtd']

        cursor.close()
        conn.close()
    except Exception as e:
        print("Erro no banco:", e)

    return jsonify(dados)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
