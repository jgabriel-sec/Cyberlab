# 🛡️ Cyberlab — Laboratório Integrado de Cibersegurança & Engenharia Segura

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)
![Nmap](https://img.shields.io/badge/Tools-Nmap%207.80%20%7C%20Wireshark-green)
![Security](https://img.shields.io/badge/Architecture-Red%20%7C%20Blue%20%7C%20AppSec-red)
![OWASP](https://img.shields.io/badge/Compliance-OWASP%20Top%2010-orange)
![Degree](https://img.shields.io/badge/Curso-Análise%20e%20Desenvolvimento%20de%20Sistemas-blueviolet)

**Autor:** José Gabriel Martins Batista  
**Curso:** Análise e Desenvolvimento de Sistemas (ADS)  
**Orientação Técnica:** Arquiteto de Cibersegurança & Especialista Sênior em Ethical Hacking  
**LinkedIn:** [linkedin.com/in/josé-gabriel-martins-batista-19b6b344a/](https://www.linkedin.com/in/jos%C3%A9-gabriel-martins-batista-19b6b344a/)  
**GitHub:** [github.com/jgabriel-sec/Cyberlab](https://github.com/jgabriel-sec/Cyberlab)  

---

## 📌 1. Visão Geral do Projeto

Este repositório documenta a concepção, exploração ofensiva, monitoramento defensivo e remediação arquitetural de redes e aplicações, executado em ambiente de laboratório isolado.

O projeto adota a metodologia de **Engenharia Tridimensional**:
1. **Application Security (AppSec):** Desenvolvimento de software seguro, validação de entradas, criptografia em trânsito e integridade de APIs REST.
2. **Red Team (Segurança Ofensiva):** Reconhecimento de ativos, scanning industrial, banner grabbing, injeção de código e evasão de controles.
3. **Blue Team (Segurança Defensiva e Forense):** Deep Packet Inspection (DPI), análise de tráfego de rede, auditoria de logs e implementação de defesas ativas (Rate Limiting).

---

## 🏗️ 2. Arquitetura do Ambiente e Ferramental

* **Hosts de Teste:** `127.0.0.1` (Loopback Local) e interfaces de rede ativas (Wi-Fi/Ethernet).
* **Portas de Serviço:** `8080/TCP` (Aplicações Web e APIs REST), `135/TCP` (RPC) e `445/TCP` (SMB).
* **Bancos de Dados:** SQLite3 em memória com tabelas de usuários e credenciais.
* **Ferramentas Desenvolvidas e Empregadas:**
  * `servidor.py`: Backend defensivo com banco SQLite, auditoria em tempo real, rate limiting e gestão de sessões via cookies (`HttpOnly`).
  * `api_jwt.py`: API REST moderna que implementa autenticação *stateless* com tokens JWT assinados criptograficamente com **HMAC-SHA256**.
  * `scanner.py`: Port scanner em Python utilizando sockets nativos TCP (`SOCK_STREAM`) e detecção de handshake via `connect_ex()`.
  * `cracker.py`: Utilitário de quebra de hashes SHA-256 via ataque de dicionário determinístico offline.
  * `brute_force.py`: Script de automação de força bruta online contra formulários de autenticação.
  * **Nmap 7.80:** Varredura furtiva (SYN Scan), fingerprinting de sistema operacional (TTL) e detecção de versões de serviço (`-sV`).
  * **Wireshark:** Sniffer de rede, análise de protocolos (TCP vs UDP/DNS), reconstrução de fluxos (Follow Stream) e Deep Packet Inspection.

---

## ⚔️ 3. Módulo Red Team (Segurança Ofensiva)

### 3.1. Reconhecimento e Varredura de Portas
* **Scanner Próprio (`scanner.py`):** Mapeamento do Three-Way Handshake via código numérico de retorno (`0` = SYN-ACK recebido / Porta Aberta).
* **Varredura Industrial (Nmap):** Execução de scans rápidos nas Top 1.000 portas (`nmap 127.0.0.1`), identificando as portas críticas `135/TCP` (MSRPC) e `445/TCP` (SMB - vetor histórico de ataques como WannaCry/EternalBlue).
* **Service Probing (`-sV`):** Disparo de sondas agressivas do Nmap para forçar respostas de erro e capturar a impressão digital (*Service Fingerprint*) da aplicação Python na porta 8080.

### 3.2. Quebra de Hashes Criptográficos (Offline Cracking)
* **Hash Alvo:** `240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9` (SHA-256).
* **Resultado:** Senha `admin123` recuperada em **0.0008 segundos** via comparação direta em wordlist.

### 3.3. Bypass de Autenticação via SQL Injection
* **Vetor:** Injeção de caracteres de escape e comentários SQL no parâmetro de login.
* **Payload:** `admin'--`
* **Resultado:** Truncamento da query SQL no SQLite, anulando a checagem de senha e concedendo acesso com privilégios máximos de administrador.

### 3.4. Sequestro de Sessão (Session Hijacking)
* **Vetor:** Reutilização não autorizada de token de sessão legítimo (`session_id`).
* **Execução:** Injeção do cookie via cabeçalho HTTP:
  ```powershell
  curl -H "Cookie: session_id=<TOKEN_ROUBADO>" http://127.0.0.1:8080/painel-admin
  ```
* **Resultado:** Acesso imediato aos dados confidenciais do painel administrativo sem conhecimento de credenciais e sem passar por 2FA.

### 3.5. Falsificação de Tokens JWT (Privilege Escalation)
* **Vetor:** Desmistificação do Base64URL e adulteração do Payload de `{"role": "user"}` para `{"role": "admin"}`.
* **Resultado:** Tentativa de burlar o controle de acesso por papel (RBAC) enviando um token forjado para o endpoint protegido `/api/cofre`.

---

## 🛡️ 4. Módulo Blue Team (Segurança Defensiva e Forense)

### 4.1. Defesa Ativa: Rate Limiting e Bloqueio Dinâmico
* **Regra:** Máximo de 3 falhas de login consecutivas por endereço IP.
* **Ação:** Bloqueio temporário (20s) com emissão de status **HTTP 429 (Too Many Requests)**, neutralizando o script de força bruta antes da senha correta ser alcançada.

### 4.2. Detecção de Assinaturas de Port Scan (IDS Simulation)
* **Análise no Wireshark:** Filtragem com `tcp.flags.syn == 1 && tcp.flags.ack == 0` para isolar a rajada de pacotes disparada pelo Nmap, replicando a regra de detecção de assinaturas de sistemas IDS/IPS (como Snort e Suricata).

### 4.3. Deep Packet Inspection (DPI) & WAF Simulation
* **Análise no Wireshark:** Filtragem de tráfego com `http contains "admin'--"`, localizando o pacote exato de injeção SQL no tráfego bruto e inspecionando o payload em hexadecimal e ASCII.

### 4.4. Análise de Protocolos de Transporte (TCP vs UDP)
* **Handshake TCP:** Visualização pacote por pacote do Three-Way Handshake (`[SYN]`, `[SYN, ACK]`, `[ACK]`) antes do envio de dados da camada de aplicação.
* **Protocolo UDP (DNS):** Captura de consultas de resolução de nomes (`nslookup github.com`) na porta **53/UDP**, comprovando o funcionamento veloz e sem conexão do User Datagram Protocol.

---

## 💻 5. Módulo Application Security (Engenharia Segura)

### 5.1. Remediação de XSS e SQL Injection
* **XSS:** Codificação contextual de entidades HTML (*Context-aware HTML Entity Encoding*) via `html.escape()`.
* **SQLi:** Adoção estrita de **Prepared Statements (Consultas Parametrizadas)** com marcadores `?`, tornando a estrutura lógica imutável e tratando entradas estritamente como dados literais.

### 5.2. Hardening de Cookies de Sessão
* **Flag `HttpOnly`:** Bloqueio de leitura de tokens via JavaScript (`document.cookie`), neutralizando exfiltração de credenciais via XSS.
* **Flags Complementares:** Adoção de `Secure` (obrigatoriedade de transporte HTTPS) e `SameSite=Strict` (mitigação de CSRF).

### 5.3. Integridade Criptográfica em APIs REST (JWT + HMAC-SHA256)
* **Assinatura Digital:** Validação de integridade onde a assinatura é gerada via `HMAC-SHA256(Header + Payload, CHAVE_SECRETA)`.
* **Detecção de Fraude:** Quando o token adulterado com `"role": "admin"` foi enviado, o backend recalculou a assinatura e detectou a divergência imediatamente, barrando o acesso com **HTTP 401 Unauthorized**.

### 5.4. Criptografia em Trânsito (TLS / HTTPS)
* Substituição do transporte em texto puro pela criptografia híbrida TLS, garantindo **Confidencialidade**, **Integridade** e **Autenticidade** (inspeção de PKI e certificados de domínio DV emitidos por autoridades raiz).

---

## 📊 6. Matriz Consolidada de Vulnerabilidades e Controles

| Vulnerabilidade | Classificação OWASP / CWE | Severidade | Vetor de Ataque | Controle de Segurança Aplicado |
| :--- | :--- | :--- | :--- | :--- |
| **Reflected XSS / HTMLi** | OWASP A03:2021 — Injection | Média (CVSS 6.1) | Parâmetro `?busca=` | Sanitização contextual com `html.escape()` |
| **Information Disclosure** | CWE-200 | Baixa (CVSS 3.7) | Cabeçalho `Server:` | Ocultação de versão em proxy reverso/WAF |
| **Força Bruta Online** | OWASP A07:2021 — Auth Failures | Alta (CVSS 7.5) | Rota `/login` | Rate Limiting (HTTP 429) e bloqueio por IP |
| **SQL Injection (SQLi)** | OWASP A03:2021 — Injection | Crítica (CVSS 9.8) | Parâmetro `?user=` | Consultas Parametrizadas (*Prepared Statements*) |
| **Session Hijacking** | CWE-384 / Session Fixation | Alta (CVSS 8.8) | Cabeçalho `Cookie:` | Flag `HttpOnly` + Expiração de Sessão |
| **Token Tampering (JWT)** | OWASP A01:2021 — Broken Access | Alta (CVSS 8.5) | Payload Base64 | Assinatura Criptográfica com HMAC-SHA256 |
| **Tráfego em Texto Puro** | CWE-319 | Alta (CVSS 7.4) | Protocolo HTTP | Criptografia TLS (HTTPS) + Cabeçalho HSTS |
| **Port Scanning Não Detectado** | MITRE ATT&CK T1046 | Baixa / Recon | TCP SYN Burst | Monitoramento de assinaturas em IDS/IPS (Wireshark/Snort) |

---

## 🎯 7. Conclusões de Engenharia

O projeto comprova que a resiliência de um ambiente computacional moderno não é alcançada através de uma única ferramenta, mas sim pela aplicação de princípios de **Defesa em Camadas (Defense in Depth)**:
1. *Validação e Sanitização na Entrada (Input Handling).*
2. *Separação absoluta entre Instrução de Código e Dado Manipulado (Prepared Statements).*
3. *Garantia de Integridade e Autenticidade em Comunicações Stateless (Assinaturas Criptográficas em APIs).*
4. *Proteção de Identidade e Sessões contra Exfiltração Client-Side (Cookies HttpOnly).*
5. *Visibilidade e Auditoria Contínua em Nível de Pacotes e Logs (DPI com Wireshark e Monitoramento Ativo).*

---