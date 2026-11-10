import hashlib
import time

# O HASH DO ALVO (Este é o hash da senha 'admin123' que geramos antes)
HASH_ALVO = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"

# A nossa lista de palpites (Wordlist / Dicionário de senhas comuns)
PALPITES = [
    "123456",
    "senha",
    "password",
    "qwerty",
    "brasil",
    "admin",
    "root",
    "admin123",
    "mudar123"
]

print("=====================================================")
print("[*] ARQUITETO DE CIBERSEGURANÇA — HASH CRACKER")
print(f"[*] Hash Alvo: {HASH_ALVO}")
print(f"[*] Testando {len(PALPITES)} senhas do dicionário...")
print("=====================================================\n")

inicio = time.time()
sucesso = False

for palpite in PALPITES:
    # 1. Calcula o hash do palpite atual
    hash_palpite = hashlib.sha256(palpite.encode()).hexdigest()
    print(f"[-] Testando: {palpite:<12} -> {hash_palpite[:16]}...")
    
    # 2. Compara com o hash do alvo
    if hash_palpite == HASH_ALVO:
        fim = time.time()
        print("\n" + "="*53)
        print(f"[+] SUCESSO! SENHA QUEBRADA: >>> {palpite} <<<")
        print(f"[+] Tempo gasto: {fim - inicio:.4f} segundos")
        print("="*53)
        sucesso = True
        break

if not sucesso:
    print("\n[-] Falha: Nenhuma senha do dicionário correspondeu ao hash.")