from flask import Flask, jsonify, render_template, request
import mysql.connector

app = Flask(__name__)

DB_CONFIG = {
    'host': '127.0.0.1', 
    'user': 'feliperibeiro',
    'password': 'substituir_senha',
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
    
    dados = {
        "paciente": None,
        "posicao": None,       
        "total_setor": None,   
        "tempo_estimado": None,
        "risco": {
            "emergencia": {"qtd": 0, "tempo": ""},
            "muitoUrgente": {"qtd": 0, "tempo": ""},
            "urgente": {"qtd": 0, "tempo": ""},
            "poucoUrgente": {"qtd": 0, "tempo": ""},
            "naoUrgente": {"qtd": 0, "tempo": ""}
        },
        "setores": {
            "recepcao": {"qtd": 0, "tempo": ""},
            "classificacao": {"qtd": 0, "tempo": ""},
            "clinico": {"qtd": 0, "tempo": ""},
            "pediatra": {"qtd": 0, "tempo": ""},
            "ortopedia": {"qtd": 0, "tempo": ""},
            "odonto": {"qtd": 0, "tempo": ""},
            "medicacao": {"qtd": 0, "tempo": ""}
        }
    }

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Puxa os dados do paciente com campos necessários para a regra de negócio
        pac = None
        if protocolo:
            query_paciente = """
                SELECT a.id, a.paciente_nome, a.status_atual, a.especialidade, a.chegada_em, 
                       cr.nome as classificacao_nome, cr.ordem_prioridade, a.prioridade_legal
                FROM upa_atendimentos a 
                LEFT JOIN upa_classificacoes_risco cr ON a.classificacao_risco_id = cr.id 
                WHERE a.protocolo = %s
            """
            cursor.execute(query_paciente, (protocolo,))
            pac = cursor.fetchone()
            
            if pac:
                # Valores para a regra de negócio
                ordem_p = pac.get("ordem_prioridade") or 99
                prioridade_leg = pac.get("prioridade_legal") or 0
                
                # Calcula Posição usando Manchester > Preferencial > Chegada
                query_posicao = """
                    SELECT COUNT(*) as pos 
                    FROM upa_atendimentos a2
                    LEFT JOIN upa_classificacoes_risco cr2 ON a2.classificacao_risco_id = cr2.id
                    WHERE a2.status_atual = %s 
                      AND a2.id != %s
                      AND (
                          (COALESCE(cr2.ordem_prioridade, 99) < %s) OR
                          (COALESCE(cr2.ordem_prioridade, 99) = %s AND a2.prioridade_legal > %s) OR
                          (COALESCE(cr2.ordem_prioridade, 99) = %s AND a2.prioridade_legal = %s AND a2.chegada_em < %s)
                      )
                """
                cursor.execute(query_posicao, (
                    pac["status_atual"], pac["id"], 
                    ordem_p, 
                    ordem_p, prioridade_leg, 
                    ordem_p, prioridade_leg, pac["chegada_em"]
                ))
                res_pos = cursor.fetchone()
                pessoas_na_frente = res_pos['pos'] if res_pos else 0
                
                dados["paciente"] = {
                    "paciente_nome": pac.get("paciente_nome", ""),
                    "status_atual": pac.get("status_atual", ""),
                    "especialidade": pac.get("especialidade", ""),
                    "classificacao_nome": pac.get("classificacao_nome") or "Aguardando Classificação"
                }
                dados["posicao"] = pessoas_na_frente + 1
                dados["tempo_estimado"] = pessoas_na_frente * 5

        # 2. Puxa TODOS os pacientes para preencher os Cards
        query_todos = """
            SELECT a.status_atual, a.especialidade, cr.nome as classificacao_nome 
            FROM upa_atendimentos a 
            LEFT JOIN upa_classificacoes_risco cr ON a.classificacao_risco_id = cr.id 
            WHERE a.status_atual NOT IN ('FINALIZADO', 'EVASAO', 'CANCELADO')
        """
        cursor.execute(query_todos)
        todos = cursor.fetchall()
        
        for p in todos:
            status = p.get('status_atual', '')
            espec = p.get('especialidade', '')
            risco = str(p.get('classificacao_nome', '')).lower()
            
            # Contagem de Setores
            if status == 'AGUARDANDO_RECEPCAO': 
                dados['setores']['recepcao']['qtd'] += 1
            elif status == 'EM_TRIAGEM': 
                dados['setores']['classificacao']['qtd'] += 1
            elif status in ['AGUARDANDO_ATENDIMENTO', 'EM_ATENDIMENTO']:
                if espec == 'Clínico Geral': dados['setores']['clinico']['qtd'] += 1
                elif espec == 'Pediatria': dados['setores']['pediatra']['qtd'] += 1
                elif espec == 'Ortopedia': dados['setores']['ortopedia']['qtd'] += 1
                elif espec == 'Odontologia': dados['setores']['odonto']['qtd'] += 1
            elif status == 'AGUARDANDO_MEDICACAO': 
                dados['setores']['medicacao']['qtd'] += 1

            # Conta Riscos
            if 'emerg' in risco: dados['risco']['emergencia']['qtd'] += 1
            elif 'muito urgente' in risco: dados['risco']['muitoUrgente']['qtd'] += 1
            elif 'pouco urgente' in risco: dados['risco']['poucoUrgente']['qtd'] += 1
            elif 'urgente' in risco: dados['risco']['urgente']['qtd'] += 1
            elif 'não' in risco or 'nao' in risco: dados['risco']['naoUrgente']['qtd'] += 1

        # 3. Define total_setor do paciente lido
        if protocolo and pac:
            s_pac = pac.get("status_atual", "")
            e_pac = pac.get("especialidade", "")
            if s_pac == 'AGUARDANDO_RECEPCAO': dados["total_setor"] = dados['setores']['recepcao']['qtd']
            elif s_pac == 'EM_TRIAGEM': dados["total_setor"] = dados['setores']['classificacao']['qtd']
            elif s_pac in ['AGUARDANDO_ATENDIMENTO', 'EM_ATENDIMENTO']:
                if e_pac == 'Clínico Geral': dados["total_setor"] = dados['setores']['clinico']['qtd']
                elif e_pac == 'Pediatria': dados["total_setor"] = dados['setores']['pediatra']['qtd']
                elif e_pac == 'Ortopedia': dados["total_setor"] = dados['setores']['ortopedia']['qtd']
                elif e_pac == 'Odontologia': dados["total_setor"] = dados['setores']['odonto']['qtd']
            elif s_pac == 'AGUARDANDO_MEDICACAO': dados["total_setor"] = dados['setores']['medicacao']['qtd']

        cursor.close()
        conn.close()
    except Exception as e:
        print("Erro no banco:", e)

    return jsonify(dados)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
