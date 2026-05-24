# UPA Transparente - Gestão de Filas (Projeto Integrador UNIVESP)

## Sobre o Projeto
O **UPA Transparente** (Projeto Integrador UNIVESP - UPA Jandira) é um sistema integrado de gestão e transparência de filas para Unidades de Pronto Atendimento (UPAs). O objetivo principal é modernizar o fluxo de pacientes, desde o cadastro na recepção até o atendimento médico e medicação. 

O sistema fornece painéis visuais inteligentes para que os pacientes acompanhem sua posição na fila em tempo real e o tempo estimado de espera. A organização das filas ocorre de forma automática e dinâmica, seguindo rigorosamente:
1. **Protocolo de Manchester** (Classificação de Risco Clínico).
2. **Prioridades Legais** (Idosos, Gestantes, etc.).
3. **Ordem de Chegada**.

## Estrutura de Arquivos e Componentes

A arquitetura do sistema foi dividida em Banco de Dados, Backend, Frontend (Painel) e Interfaces Desktop para os funcionários. Abaixo está o que cada arquivo principal faz:

### `Database_FILAGO.sql` (Banco de Dados)
Arquivo de dump/configuração da estrutura do banco de dados relacional (MariaDB/MySQL). Ele cria e gerencia as tabelas fundamentais da aplicação, como:
* `upa_atendimentos`: Registro central dos pacientes, status e classificação de risco.
* `upa_setores`: Mapeamento das áreas da UPA (Recepção, Triagem, Consultórios, etc.).
* `upa_atendimento_eventos`: Histórico de movimentação do paciente para auditoria e cálculo de tempos médios.

### `app.py` (Backend Flask)
Intermedia a comunicação entre o banco de dados e a interface visual web. É uma API leve construída em **Python/Flask**.
* **O que faz:** Recebe requisições HTTP, consulta o banco de dados e executa as regras de negócio de ordenação de fila (risco > prioridade > tempo).
* **Retorno:** Devolve dados no formato JSON com a posição exata do paciente na fila e a contagem total de pessoas por setor para alimentar a TV ou o celular do usuário.

### `index.html` (Frontend / Painel do Paciente)
Painel web dinâmico desenvolvido com **HTML, CSS e JavaScript**.
* **O que faz:** Consome a API do backend (`app.py`) e atualiza as informações na tela sem precisar recarregar a página. Ele exibe a contagem de pessoas aguardando nos setores de forma humanizada (sem exibir "0" quando um setor está vazio) e calcula estimativas de tempo baseadas na posição real da pessoa na fila.

### `Interface_Cadastro_Pacientes.py` (App Desktop - Recepção)
Interface gráfica para a equipe da recepção da UPA, desenvolvida em **Python usando CustomTkinter**.
* **O que faz:** Permite que o funcionário insira os dados do paciente recém-chegado (nome, antecedentes, classificação preliminar, etc.) e o injete diretamente no banco de dados com o status de "Aguardando Recepção".

### `Interface_Gerenciador_Fila.py` (App Desktop - Enfermagem/Médicos)
Interface gráfica (também em **CustomTkinter**) usada nos consultórios e salas de triagem para movimentar o fluxo.
* **O que faz:** O enfermeiro ou médico pode pesquisar um paciente pelo nome ou protocolo e transferi-lo de setor através de um *dropdown* (ex: de "Classificação" para "Clínico"). O app aplica o *update* no banco de dados mesclando as regras de *Status Atual* + *Especialidade*.

## Tecnologias Utilizadas
* **Backend e Integrações:** Python 3, Flask, bibliotecas `mysql.connector`.
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla).
* **Interfaces GUI Desktop:** CustomTkinter.
* **Banco de Dados:** MariaDB / MySQL.
* **Infraestrutura:** Servidor Ubuntu via SSH, Gunicorn e Systemd (serviço rodando em background).

## Equipe
Projeto desenvolvido para a disciplina de Projeto Integrador (2026) da **UNIVESP** (Zona Oeste de São Paulo) pelos alunos:
* Daniele Hora Nogueira Santos
* Ednéia Rodrigues de Lima Silva
* Felipe Alex Ribeiro
* Jose Valdir Ribeiro
* Kélli do Prado Fernandes
* Matheus Pinheiro de Lima Rodrigues
* Mikael Josias Rodrigues
* Renan Santos Andrade
