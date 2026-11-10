import socket

# Alvo da varredura (127.0.0.1 = nosso laboratório local)
ALVO = "127.0.0.1"

# Portas comuns que queremos investigar
# 21 (FTP), 22 (SSH), 80 (HTTP), 135 (RPC Windows), 443 (HTTPS), 7680 (WUDO), 8080 (Nosso Servidor)
PORTAS = [21, 22, 80, 135, 443, 7680, 8080, 8443]

print(f"=====================================================")
print(f"[*] ARQUITETO DE CIBERSEGURANÇA — RED TEAM SCANNER")
print(f"[*] Alvo: {ALVO}")
print(f"[*] Investigando {len(PORTAS)} portas...")
print(f"=====================================================")

for porta in PORTAS:
    # 1. Cria um socket IPv4 (AF_INET) usando protocolo TCP (SOCK_STREAM)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. Timeout de 0.5s para não travar em portas filtradas/silenciosas
    s.settimeout(0.5)
    
    # 3. Tenta o Handshake TCP. Retorna 0 se conectou com sucesso!
    resultado = s.connect_ex((ALVO, porta))
    
    if resultado == 0:
        print(f"  [+] Porta {porta:<5} : ABERTA (Serviço ativo detectado!)")
    else:
        print(f"  [-] Porta {porta:<5} : Fechada")
        
    # 4. Fecha a conexão para liberar o canal
    s.close()

print(f"=====================================================")
print(f"[*] Varredura concluída.")