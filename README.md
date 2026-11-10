\# 🛡️ Laboratório de Fundamentos de Cibersegurança (Red, Blue \& AppSec)



\*\*Autor:\*\* Laboratório Prático de Cibersegurança  

\*\*Orientação Técnica:\*\* Arquiteto de Cibersegurança \& Ethical Hacker  

\*\*Data:\*\* Novembro de 2026  

\*\*Ambiente:\*\* Windows 10/11 | Python 3 | SQLite3 | PowerShell  



\---



\## 📌 1. Visão Geral do Projeto



Este projeto documenta o ciclo completo de segurança cibernética (construção, ataque, monitoramento e correção) executado em ambiente de laboratório isolado (`127.0.0.1`). 



O laboratório adotou a metodologia de \*\*Engenharia Tridimensional\*\*:

1\. \*\*Application Security (AppSec):\*\* Como o software é construído e protegido.

2\. \*\*Red Team (Segurança Ofensiva):\*\* Como as vulnerabilidades são mapeadas e exploradas.

3\. \*\*Blue Team (Segurança Defensiva):\*\* Como as anomalias são detectadas em logs e bloqueadas em tempo real.



\---



\## 🏗️ 2. Arquitetura do Ambiente



\* \*\*Host Alvo:\*\* `127.0.0.1` (Loopback Local).

\* \*\*Porta de Aplicação:\*\* `8080/TCP` (Serviço HTTP customizado em Python).

\* \*\*Banco de Dados:\*\* SQLite3 em memória com persistência volátil para isolamento de testes.

\* \*\*Ferramental Desenvolvido:\*\*

&#x20; \* `servidor.py`: Backend web com logging de auditoria, banco SQLite e rate limiting.

&#x20; \* `scanner.py`: Scanner de portas TCP baseado na biblioteca nativa de sockets.

&#x20; \* `cracker.py`: Utilitário de quebra de hashes SHA-256 via ataque de dicionário.

&#x20; \* `brute\_force.py`: Script de ataque de dicionário online contra formulário de login.



\---



\## ⚔️ 3. Módulo Red Team (Segurança Ofensiva)



\### 3.1. Varredura de Portas (Port Scanning)

\* \*\*Objetivo:\*\* Mapear a superfície de ataque da máquina local.

\* \*\*Implementação:\*\* Criação de sockets TCP (`SOCK\_STREAM`) e verificação do Three-Way Handshake via `connect\_ex()`.

\* \*\*Portas Identificadas:\*\*

&#x20; \* `135/TCP` (RPC Endpoint Mapper do Windows)

&#x20; \* `7680/TCP` (Windows Update Delivery Optimization - WUDO)

&#x20; \* `8080/TCP` (Servidor de aplicação do laboratório)



\### 3.2. Enumeração de Serviços (Banner Grabbing)

\* \*\*Comando:\*\* `curl -I http://127.0.0.1:8080`

\* \*\*Vazamento Identificado (CWE-200):\*\* O servidor expôs nos cabeçalhos HTTP sua identidade completa: `Server: SimpleHTTP/0.6 Python/3.14.7`.



\### 3.3. Quebra de Hashes Criptográficos (Offline Cracking)

\* \*\*Hash Alvo:\*\* `240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9` (SHA-256).

\* \*\*Resultado:\*\* Senha `admin123` identificada em \*\*0.0008 segundos\*\* via comparação determinística com wordlist.



\### 3.4. Bypass de Autenticação via SQL Injection

\* \*\*Vetor:\*\* Injeção de caracteres de escape e comentários SQL no parâmetro `user`.

\* \*\*Payload Utilizado:\*\* `admin'--`

\* \*\*Resultado:\*\* Anulação da verificação de senha (`AND senha = ...`) no banco de dados SQLite, concedendo acesso de administrador sem conhecimento da credencial legítima.



\---



\## 🛡️ 4. Módulo Blue Team (Segurança Defensiva e Forense)



\### 4.1. Auditoria e Rastreamento de Processos

\* Mapeamento de portas abertas e identificação do PID do processo correspondente via `netstat -ano`.

\* Associação do PID ao executável do sistema (`svchost.exe`) via `tasklist /svc`.



\### 4.2. Análise Forense de Logs de Acesso

\* Identificação de tráfego de exploração através da conversão de caracteres em \*\*URL Encoding\*\* (`%3C`, `%20`, etc.).

\* Detecção de padrões de automação (requisições múltiplas no mesmo segundo: `20:15:01`).



\### 4.3. Implementação de Defesa Ativa (Rate Limiting)

\* Regra implementada: Limite máximo de \*\*3 falhas consecutivas de login por IP\*\*.

\* Resposta do sistema: Bloqueio dinâmico temporário (20 segundos) com emissão de código de status \*\*HTTP 429 (Too Many Requests)\*\*.

\* \*\*Resultado:\*\* Neutralização completa do script de força bruta antes que a senha correta (5ª da lista) fosse testada.



\---



\## 💻 5. Módulo Application Security (Engenharia Segura)



\### 5.1. Remediação de Cross-Site Scripting (XSS / HTML Injection)

\* \*\*Causa Raiz:\*\* Reflexão direta de dados controlados pelo usuário no corpo da resposta HTML sem sanitização.

\* \*\*Correção Aplicada:\*\* Codificação contextual de entidades HTML (\*Context-aware HTML Entity Encoding\*) via `html.escape()`. O payload `<h1...>` passou a ser renderizado estritamente como texto inofensivo (`\&lt;h1...\&gt;`).



\### 5.2. Remediação de SQL Injection (SQLi)

\* \*\*Causa Raiz:\*\* Interpolação/concatenação direta de strings de entrada na query SQL (`f"SELECT ... '{usuario}'"`).

\* \*\*Correção Aplicada:\*\* Utilização de \*\*Prepared Statements (Consultas Parametrizadas)\*\* com marcadores `?`. A lógica estrutural do SQL é compilada previamente pelo banco e os parâmetros de entrada são tratados exclusivamente como dados puros, neutralizando completamente o escape de aspas e comentários.



\---



\## 📊 6. Matriz de Vulnerabilidades e Remediações



| Vulnerabilidade | Classificação OWASP | Severidade | Vetor | Correção Definitiva |

| :--- | :--- | :--- | :--- | :--- |

| \*\*Reflected HTML/XSS\*\* | A03:2021 — Injection | Média (CVSS 6.1) | `?busca=` | Sanitização de saída via `html.escape()` |

| \*\*Information Disclosure\*\* | CWE-200 | Baixa (CVSS 3.7) | Cabeçalho `Server:` | Ocultação de versão em proxy reverso/WAF |

| \*\*Força Bruta Online\*\* | A07:2021 — Auth Failures | Alta (CVSS 7.5) | `?user=\&pass=` | Rate Limiting (HTTP 429) e bloqueio por IP |

| \*\*SQL Injection (SQLi)\*\* | A03:2021 — Injection | Crítica (CVSS 9.8) | Parâmetro de login | Consultas Parametrizadas (\*Prepared Statements\*) |



\---



\## 🎯 7. Conclusão



O laboratório comprovou que a segurança eficaz não se baseia em segredos ou ferramentas complexas, mas na aplicação rigorosa de princípios de engenharia:

1\. \*Nunca confiar na entrada do usuário.\*

2\. \*Separar a instrução de código dos dados manipulados.\*

3\. \*Implementar defesa em camadas (código seguro + monitoramento de tráfego + limitação ativa de taxa).\*



\---

