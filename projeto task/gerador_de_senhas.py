import random
import string
import argparse
from datetime import datetime

def gerar_senha(tamanho=12, usar_simbolos=True, usar_numeros=True):
    caracteres = string.ascii_letters
    if usar_numeros:
        caracteres += string.digits
    if usar_simbolos:
        caracteres += string.punctuation
    return ''.join(random.choice(caracteres) for _ in range(tamanho))

def main():
    parser = argparse.ArgumentParser(description="🔐 Gerador de Senhas")
    parser.add_argument("-t", "--tamanho", type=int, default=12, help="Tamanho da senha")
    parser.add_argument("-q", "--quantidade", type=int, default=1, help="Quantas senhas gerar")
    parser.add_argument("--sem-simbolos", action="store_true", help="Sem símbolos especiais")
    parser.add_argument("--sem-numeros", action="store_true", help="Sem números")
    parser.add_argument("-s", "--salvar", action="store_true", help="Salva as senhas em arquivo")
    args = parser.parse_args()

    senhas = [gerar_senha(args.tamanho, not args.sem_simbolos, not args.sem_numeros)
              for _ in range(args.quantidade)]

    print(f"\n🔐 {args.quantidade} senha(s) gerada(s):\n")
    for i, senha in enumerate(senhas, 1):
        print(f"  {i}. {senha}")

    if args.salvar:
        nome = f"senhas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(nome, "w") as f:
            f.write("\n".join(senhas))
        print(f"\n✅ Salvo em: {nome}")

main()