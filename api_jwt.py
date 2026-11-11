import http.server
import socketserver
import json
import base64
import hmac
import hashlib

HOST = "127.0.0.1"
PORTA = 8080

# Chave secreta do servidor (SÓ O BACKEND CONHECE ESTE SEGREDO!)
CHAVE_SECRETA = b"ChaveMestraUltraSecretaDeSeguranca2026!"

def b64url_encode(dados_bytes):
    """Converte bytes para Base64URL sem preenchimento '='"""
    return base64.urlsafe_b64encode(dados_bytes).rstrip(b'=').decode('utf-8')

def b64url_decode(texto_str):
    """Decodifica Base64URL adicionando preenchimento '=' quando necessario"""
    padding = len(texto_str) % 4
    if padding:
        texto_str += '=' * (4 - padding)
    return base64.urlsafe_b64decode(texto_str)

def criar_jwt(usuario, role):
    # 1. Header
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = b64url_encode(json.dumps(header).encode('utf-8'))

    # 2. Payload
    payload = {"usuario": usuario, "role": role}
    payload_b64 = b64url_encode(json.dumps(payload).encode('utf-8'))

    # 3. Assinatura HMAC-SHA256
    mensagem = f"{header_b64}.{payload_b64}".encode('utf-8')
    assinatura = hmac.new(CHAVE_SECRETA, mensagem, hashlib.sha256).digest()
    assinatura_b64 = b64url_encode(assinatura)

    # Token completo montado com os dois pontos
    return f"{header_b64}.{payload_b64}.{assinatura_b64}"

def validar_jwt(token):
    try:
        partes = token.split('.')
        if len(partes) != 3:
            return False, "Estrutura invalida"

        header_b64, payload_b64, assinatura_recebida_b64 = partes

        # Recalcula a assinatura com a nossa chave secreta
        mensagem = f"{header_b64}.{payload_b64}".encode('utf-8')
        assinatura_esperada = hmac.new(CHAVE_SECRETA, mensagem, hashlib.sha256).digest()
        assinatura_esperada_b64 = b64url_encode(assinatura_esperada)

        # COMPARAÇÃO CRIPTOGRÁFICA SEGURA: As assinaturas batem?
        if hmac.compare_digest(assinatura_recebida_b64, assinatura_esperada_b64):
            dados_payload = json.loads(b64url_decode(payload_b64).decode('utf-8'))
            return True, dados_payload
        else:
            return False, "FALSIFICACAO DETECTADA! A assinatura nao corresponde."
    except Exception as e:
        return False, str(e)

class APIHandler(http.server.SimpleHTTPRequestHandler):
    def responder_json(self, status, dados):
        self.send_response(status)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(dados, indent=2).encode('utf-8'))

    def do_POST(self):
        # ROTA DE LOGIN: /api/login
        if self.path == "/api/login":
            tamanho = int(self.headers.get('Content-Length', 0))
            corpo = self.rfile.read(tamanho).decode('utf-8')
            dados = json.loads(corpo)

            usuario = dados.get("user")
            senha = dados.get("pass")

            if usuario == "gabriel" and senha == "123":
                # Gabriel e um usuario comum (role: user)
                token = criar_jwt(usuario, role="user")
                print(f"\n[API - LOGIN] Usuario '{usuario}' autenticado com sucesso.")
                print(f"  [+] Token JWT Emitido: {token}")
                self.responder_json(200, {"mensagem": "Login OK", "token": token})
            else:
                self.responder_json(401, {"erro": "Credenciais incorretas"})

    def do_GET(self):
        # ROTA PROTEGIDA: /api/cofre
        if self.path == "/api/cofre":
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith("Bearer "):
                self.responder_json(401, {"erro": "Cabecalho Authorization com Bearer token e obrigatorio!"})
                return

            token = auth_header.split(" ")[1]
            valido, resultado = validar_jwt(token)

            if not valido:
                print(f"\n[BLUE TEAM - ALERTA DE SEGURANCA] Tentativa de fraude de token!")
                print(f"  [!] Motivo da recusa: {resultado}")
                self.responder_json(401, {"status": "Acesso Negado", "motivo": resultado})
                return

            payload = resultado
            print(f"\n[API - ACESSO AUTORIZADO] Token valido de '{payload['usuario']}' (Papel: {payload['role']})")

            if payload.get("role") == "admin":
                self.responder_json(200, {
                    "status": "Acesso Administrativo Liberado",
                    "cofre_da_empresa": "R$ 15.000.000,00",
                    "segredos": ["Projeto Apollo", "Senhas Mestras AWS"]
                })
            else:
                self.responder_json(403, {
                    "status": "Acesso Proibido",
                    "mensagem": f"Ola {payload['usuario']}, seu papel e 'user'. Apenas 'admin' pode acessar o cofre!"
                })

    def log_message(self, format, *args):
        return

print("=====================================================")
print("[*] ARQUITETO DE CIBERSEGURANÇA — LAB 06: API REST & JWT")
print(f"[*] API rodando em http://{HOST}:{PORTA}")
print("=====================================================")

with socketserver.TCPServer((HOST, PORTA), APIHandler) as httpd:
    httpd.serve_forever()