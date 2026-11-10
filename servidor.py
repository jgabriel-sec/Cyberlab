import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import secrets
import datetime

HOST = "127.0.0.1"
PORTA = 8080

# Banco de sessões ativas na memória do servidor: { 'token_secreto': 'usuario' }
sessoes_ativas = {}

class SessionHandler(http.server.SimpleHTTPRequestHandler):
    def extrair_cookie(self):
        """Lê o cabeçalho Cookie enviado pelo navegador e extrai o session_id"""
        cabecalho_cookie = self.headers.get('Cookie', '')
        for item in cabecalho_cookie.split(';'):
            partes = item.strip().split('=')
            if len(partes) == 2 and partes[0] == 'session_id':
                return partes[1]
        return None

    def do_GET(self):
        agora = datetime.datetime.now().strftime("%H:%M:%S")
        caminho = urlparse(self.path).path

        # -------------------------------------------------------------
        # ROTA 1: LOGIN (Emite a "Pulseira VIP" / Cookie de Sessão)
        # -------------------------------------------------------------
        if caminho == "/login":
            params = parse_qs(urlparse(self.path).query)
            usuario = params.get('user', [''])[0]
            senha = params.get('pass', [''])[0]

            # Credencial simples para nosso laboratório
            if usuario == "admin" and senha == "admin123":
                # Gera um token criptograficamente seguro e imprevisível
                novo_token = secrets.token_hex(16)
                sessoes_ativas[novo_token] = usuario

                print(f"\n[BLUE TEAM - SESSÃO CRIADA] {agora}")
                print(f"  [+] Login aprovado para: {usuario}")
                print(f"  [+] Novo Token Emitido: {novo_token}")

                # Resposta HTTP entregando o Cookie para o navegador
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                # CABEÇALHO MÁGICO: Entrega o cookie para o navegador guardar!
                self.send_header("Set-Cookie", f"session_id={novo_token}; Path=/; HttpOnly")
                self.end_headers()

                resposta = f"""
                <body style='font-family: Arial; margin: 40px;'>
                    <h1 style='color: green;'>[SUCESSO] Login Realizado!</h1>
                    <p>O servidor entregou uma <b>Pulseira VIP (Cookie)</b> para o seu navegador.</p>
                    <p>Token da sessão: <code>{novo_token}</code></p>
                    <p><a href='/painel-admin' style='font-size: 18px;'>👉 Clique aqui para ir ao Painel Secreto do Admin</a></p>
                </body>
                """
                self.wfile.write(resposta.encode("utf-8"))
            else:
                self.send_response(401)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<h1>[ERRO] Usuario ou senha incorretos.</h1>")
            return

        # -------------------------------------------------------------
        # ROTA 2: PAINEL SECRETO (Área restrita protegida por Sessão)
        # -------------------------------------------------------------
        if caminho == "/painel-admin":
            cookie_recebido = self.extrair_cookie()

            print(f"\n[BLUE TEAM - AUDITORIA DE ACESSO AO PAINEL] {agora}")
            print(f"  [*] IP: {self.client_address[0]}")
            print(f"  [*] Cookie Apresentado: {cookie_recebido}")

            # O token apresentado é válido e existe no banco de sessões?
            if cookie_recebido and cookie_recebido in sessoes_ativas:
                dono_da_sessao = sessoes_ativas[cookie_recebido]
                print(f"  [+] ACESSO PERMITIDO: Sessao pertence a '{dono_da_sessao}'")

                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()

                resposta = f"""
                <body style='font-family: Arial; margin: 40px; background-color: #f4f6f9;'>
                    <h1 style='color: #2c3e50;'>💎 PAINEL ULTRA SECRETO DO ADMINISTRADOR</h1>
                    <p>Autenticado como: <b>{dono_da_sessao}</b></p>
                    <div style='background: white; padding: 20px; border-left: 5px solid green; border-radius: 4px;'>
                        <h3>Dados Confidenciais da Empresa:</h3>
                        <ul>
                            <li>Saldo em Caixa: R$ 5.420.000,00</li>
                            <li>Chave Mestra de Criptografia: <code>AES-256-SUPER-KEY-XYZ</code></li>
                        </ul>
                    </div>
                </body>
                """
                self.wfile.write(resposta.encode("utf-8"))
            else:
                print(f"  [!] ACESSO BLOQUEADO: Tentativa de entrar sem cookie valido!")

                self.send_response(403)  # 403 Forbidden
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                resposta = """
                <body style='font-family: Arial; margin: 40px;'>
                    <h1 style='color: red;'>⛔ 403 - ACESSO NEGADO!</h1>
                    <p>Você não possui a Pulseira VIP (Cookie de Sessão válido).</p>
                    <p>Você precisa fazer login primeiro em: <code>/login?user=admin&pass=admin123</code></p>
                </body>
                """
                self.wfile.write(resposta.encode("utf-8"))
            return

        # Página padrão
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h1>[LAB] Servidor de Sessoes Ativo!</h1><p>Acesse /painel-admin ou faca login em /login</p>")

    def log_message(self, format, *args):
        return

print("=====================================================")
print("[*] ARQUITETO DE CIBERSEGURANÇA — LAB 04 (SESSÕES E COOKIES)")
print(f"[*] Servidor rodando em: http://{HOST}:{PORTA}")
print("=====================================================")

with socketserver.TCPServer((HOST, PORTA), SessionHandler) as httpd:
    httpd.serve_forever()