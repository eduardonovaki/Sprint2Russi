import os
from dataclasses import dataclass

LIMITE_CONTRATADO = 500
NUM_CARREGADORES = 8
POTENCIA_MAX_CARREGADOR = 22

@dataclass
class Veiculo:
    id: int
    soc: float
    bateria_kwh: float
    potencia_atual: float = 0

carregadores = [None] * NUM_CARREGADORES
contador_veiculos = 1
hora = 0
consumo_predio = 350

def limpar():
    os.system("cls" if os.name == "nt" else "clear")

def adicionar_veiculo():
    global contador_veiculos

    vagas_livres = [i for i, v in enumerate(carregadores) if v is None]

    if not vagas_livres:
        print("Não há carregadores disponíveis.")
        return

    try:
        soc = float(input("SoC inicial (%): "))
        bateria = float(input("Capacidade da bateria (kWh): "))
    except ValueError:
        print("Valor inválido.")
        return

    vaga = vagas_livres[0]

    carregadores[vaga] = Veiculo(
        id=contador_veiculos,
        soc=soc,
        bateria_kwh=bateria
    )

    contador_veiculos += 1
    print("Veículo adicionado.")

def remover_veiculo():
    if contador_veiculos == 1:
        print("Não há nenhum veículo carregando no momento.")
        return
    try:
        id_remover = int(input("ID do veículo: "))
    except ValueError:
        print("ID inválido.")
        return

    for i, v in enumerate(carregadores):
        if v and v.id == id_remover:
            carregadores[i] = None
            print("Veículo removido.")
            return

    print("Veículo não encontrado.")

def distribuir_potencia():

    for v in carregadores:
        if v and v.soc >= 100:
            v.potencia_atual = 0

    evs = [
        v for v in carregadores
        if v and v.soc < 100
    ]

    if not evs:
        return

    potencia_disponivel = max(
        0,
        LIMITE_CONTRATADO - consumo_predio
    )

    demanda_total = len(evs) * POTENCIA_MAX_CARREGADOR

    if demanda_total <= potencia_disponivel:
        for v in evs:
            v.potencia_atual = POTENCIA_MAX_CARREGADOR
        return

    pesos = [101 - v.soc for v in evs]
    soma_pesos = sum(pesos)

    for v, peso in zip(evs, pesos):
        v.potencia_atual = min(
            POTENCIA_MAX_CARREGADOR,
            potencia_disponivel * peso / soma_pesos
        )



def avancar_uma_hora():
    global hora

    distribuir_potencia()

    for v in carregadores:
        if v is None:
            continue

        ganho = (v.potencia_atual / v.bateria_kwh) * 100

        v.soc += ganho

        if v.soc > 100:
            v.soc = 100

    hora += 1

    print(f"\nHora {hora} concluída.")

def alterar_consumo():
    global consumo_predio

    try:
        consumo_predio = float(
            input("Novo consumo do prédio (kW): ")
        )
    except ValueError:
        print("Valor inválido.")

def mostrar_painel():
    limpar()

    print("=" * 70)
    print("GERENCIAMENTO DINÂMICO DE CARGA")
    print("=" * 70)

    print(f"Hora Simulada      : {hora}")
    print(f"Limite Contratado  : {LIMITE_CONTRATADO} kW")
    print(f"Consumo do Prédio  : {consumo_predio} kW")

    total_ev = sum(
        v.potencia_atual
        for v in carregadores
        if v
    )

    print(f"Carga EVs          : {total_ev:.1f} kW")
    print(f"Total Utilizado    : {consumo_predio + total_ev:.1f} kW")

    print("\nCARREGADORES")
    print("-" * 70)

    for i, v in enumerate(carregadores, start=1):

        if v is None:
            print(f"C{i}: LIVRE")

        else:
            print(
                f"C{i}: EV-{v.id} | "
                f"SoC={v.soc:.1f}% | "
                f"Potência={v.potencia_atual:.1f} kW"
            )

    print("-" * 70)

while True:

    mostrar_painel()

    print("\n1 - Adicionar veículo")
    print("2 - Remover veículo")
    print("3 - Alterar consumo do prédio")
    print("X - Avançar 1 hora")
    print("0 - Sair")

    opcao = input("\nEscolha: ").upper()

    if opcao == "1":
        adicionar_veiculo()

    elif opcao == "2":
        remover_veiculo()

    elif opcao == "3":
        alterar_consumo()

    elif opcao == "X":
        avancar_uma_hora()

    elif opcao == "0":
        break

    input("\nPressione ENTER para continuar...")