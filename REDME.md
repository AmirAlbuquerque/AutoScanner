# 🚗 AutoScanner

Sistema estruturado para **planejamento, captura, consolidação e consulta de preços de veículos**, com controle de usuários, governança regional e rastreabilidade completa das operações.

---

## 📌 Visão Geral

O **AutoScanner** organiza o ciclo completo de coleta de preços automotivos:

1. Gestão de usuários e perfis de acesso  
2. Cadastro e aprovação de lojas  
3. Estruturação de marcas, modelos e versões  
4. Planejamento semanal de pesquisas  
5. Captura de veículos em campo  
6. Consolidação mensal de preços  
7. Registro de consultas públicas  

O sistema é baseado em banco relacional (SQLite) e arquitetura modular em Python.

---

## 🏗️ Arquitetura

O projeto segue separação clara de responsabilidades:

- **Camada de Regras (`rules`)**  
  Responsável por validações e controle de autorização.

- **Camada de Serviços (`services`)**  
  Orquestra regras e persistência.

- **Camada de Persistência (`database`)**  
  Responsável pela criação das tabelas e operações no banco.

---

## 🗄️ Estrutura do Banco de Dados

O sistema cria automaticamente as seguintes tabelas:

- `users`
- `stores`
- `brands`
- `models`
- `versions`
- `captures`
- `vehicle_captures`
- `weekly_plannings`
- `planning_assignments`
- `price_snapshots`
- `public_queries`

Cada tabela possui integridade referencial via **Foreign Keys** e restrições de validação (`CHECK`, `UNIQUE`).

---

## 👥 Perfis de Usuário

O sistema suporta os seguintes papéis:

- `ADMIN`
- `GERENTE`
- `COORDENADOR`
- `PESQUISADOR`
- `LOJISTA`

O controle de acesso é aplicado por meio das regras implementadas no módulo `rules`.

---

## 📊 Fluxo Operacional Simplificado

1. Usuários são cadastrados.
2. Lojas são cadastradas e aprovadas.
3. Coordenadores criam planejamentos semanais.
4. Pesquisadores realizam capturas nas lojas designadas.
5. Veículos e preços são registrados.
6. Snapshots mensais consolidam os dados.
7. Consultas públicas são registradas.

---

## ⚙️ Inicialização do Banco

O banco é inicializado pela função:

```python
init_db()
```
Ela executa:

- create_tables() → cria todas as tabelas

- seed_admin() → cria usuário ADMIN padrão (caso não exista)

Usuário inicial:

Email: admin@autoscanner.local
Senha: admin123

⚠ Recomenda-se alterar a senha em ambiente real.

---

## 🧪 Testes

O projeto utiliza pytest para testes unitários.

Para executar os testes:

- pytest


Os testes estão organizados em:

tests/unit/


Cobrem:

- Regras de negócio

- Serviços

---

## 🔐 Segurança

- Senhas armazenadas com bcrypt

- Controle de perfil via campo role

- Restrições de integridade no banco

- Validações centralizadas no módulo de regras

```
📁 Estrutura do Projeto

AutoScanner/
|─ .github/
│  └─ workflows/
│     └─ (pipelines CI/CD do GitHub Actions)
│
|─ ─ pages/
│
|─ ─ src/
│  |── database/
│  │  |── infrastructure/
|  |  |  |── repositories/
|  |  │  │  |── brands_db.py                        # SQL de brands
|  |  │  │  |── models_db.py                        # SQL de models
|  |  │  │  |── versions_db.py                      # SQL de versions
|  |  │  │  |── stores_db.py                        # SQL de stores
|  |  │  │  |── weekly_plannings_db.py              # SQL de planejamento semanal
|  |  │  │  |── planning_assignments_db.py          # SQL de atribuições
|  |  │  │  |── captures_db.py                      # SQL de capturas
|  |  │  │  |── vehicle_captures_db.py              # SQL de veículos capturados
|  |  │  │  |── public_queries_db.py                # SQL de consulta pública (avg + preços + log)
|  |  │  │  └─ user_db.py                           # SQL de users
|  |  |  |  
│  │  │  |── connection.py                          # conexão SQLite
│  │  │  └─  init_db.py                             # criação do schema
|  |  |  
│  │  |── data/
│  │  │  └─ seed.py                                 # seed local para popular o banco (dev/demo)
│  │
│  |── rules/                                       # validações/regras
│  │  |── user_rules.py
│  │  |── store_rules.py
│  │  |── catalog_rules.py
│  │  |── capture_rules.py
│  │  |── planning_rules.py
│  │  └─ public_queries_rules.py
│  │
│  |── services/
│  │  |── auth_service.py                           # login/PyJWT
│  │  |── user_service.py                           # casos de uso de usuários (admin)
│  │  |── store_service.py                          # casos de uso de lojas (aprovação/cadastro)
│  │  |── catalog_service.py                        # casos de uso do catálogo (marca/modelo/versão)
│  │  |── capture_service.py                        # casos de uso de captura (pesquisador)
│  │  |── planning_service.py                       # casos de uso de planejamento (coordenador)
│  │  └─ public_queries_service.py                  # consulta pública + log em public_queries
│  │
│  └─ ui/
│     |── session.py                                # controle de sessão do Streamlit (login/logout)
│     └─ layout.py
│
|── tests/
│  |── unit/
│  |── test_rules.py
│  |── test_store_service.py
│  |── test_user_service.py
│  └─ (demais testes unitários)
│
|── app.py                                          # entrada principal do Streamlit
|── REDME.md
└─ requirements.txt                                 # dependências
```

---

## 🛠️ Tecnologias Utilizadas

- Python
- SQLite
- Pytest
- bcrypt
- PyJWT
