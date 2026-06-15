import os
from dataclasses import dataclass

LIMITE_CONTRATADO = 500
NUM_CARREGADORES = 8
POTENCIA_MAX_CARREGADOR = 22
energia_v2x = 0


@dataclass
class Veiculo:
    id: int
    soc: float
    bateria_kwh: float
    v2x_habilitado: bool
    potencia_atual: float = 0


carregadores = [None] * NUM_CARREGADORES

contador_veiculos = 1
hora = 0

consumo_predio = 350
geracao_solar = 120


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

    v2x = input("Permitir V2X? (s/n): ").lower() == "s"

    vaga = vagas_livres[0]

    carregadores[vaga] = Veiculo(
        id=contador_veiculos,
        soc=soc,
        bateria_kwh=bateria,
        v2x_habilitado=v2x
    )

    contador_veiculos += 1
    print("Veículo adicionado.")


def remover_veiculo():
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
        if v:
            v.potencia_atual = 0

    evs = [v for v in carregadores if v and v.soc < 100]

    if not evs:
        return

    # O V2X entra somando na potência disponível para os carros
    potencia_disponivel = max(
        0,
        LIMITE_CONTRATADO + geracao_solar + energia_v2x - consumo_predio
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
    global energia_v2x

    # 1. Distribui a potência usando a energia_v2x calculada no comando 6
    distribuir_potencia()

    # 2. Atualiza o SoC dos veículos com base na potência distribuída
    for v in carregadores:
        if v is None:
            continue

        ganho = (v.potencia_atual / v.bateria_kwh) * 100
        v.soc += ganho

        if v.soc > 100:
            v.soc = 100

    # 3. ALERTA CRÍTICO: Se mesmo com o V2X o prédio ficou no vermelho
    saldo_total = (LIMITE_CONTRATADO + geracao_solar + energia_v2x) - consumo_predio
    if saldo_total < 0:
        print("\n" + "!" * 60)
        print(" ALERTA CRÍTICO: CAPACIDADE INTERROMPIDA POR CONSUMO ELEVADO! ")
        print(f" O prédio ultrapassou os limites em {abs(saldo_total):.1f} kW.")
        print(" Os veículos não receberão carga e o V2X foi insuficiente.")
        print("!" * 60)

    # 4. Reseta a contribuição do V2X para o próximo ciclo/hora
    energia_v2x = 0
    hora += 1
    print(f"\nHora {hora} concluída.")


def alterar_consumo():
    global consumo_predio
    try:
        consumo_predio = float(input("Novo consumo do prédio (kW): "))
    except ValueError:
        print("Valor inválido.")


def alterar_solar():
    global geracao_solar
    try:
        geracao_solar = float(input("Nova geração solar (kW): "))
    except ValueError:
        print("Valor inválido.")


def assistente():
    saldo = LIMITE_CONTRATADO + geracao_solar + energia_v2x - consumo_predio

    print("\nASSISTENTE CHARGEGRID")
    print("-" * 40)

    if saldo < 0:
        print(f"Déficit energético detectado: {abs(saldo):.1f} kW")
        print("Recomendação: ativar V2X urgentemente.")
    elif saldo < 50:
        print("Margem operacional baixa.")
        print("Recomendação: monitorar consumo do prédio.")
    else:
        print("Operação dentro da faixa ideal.")


def executar_v2x():
    global energia_v2x
    energia_v2x = 0

    deficit = consumo_predio - geracao_solar - LIMITE_CONTRATADO

    if deficit < 0:
        print("\nNão há necessidade de V2X. O sistema está estável.")
        return

    print("\nATIVAÇÃO V2X")
    print(f"Déficit detectado no prédio: {deficit:.1f} kW")

    energia_total = 0

    # Seleciona e ordena veículos aptos (SoC > 40% e V2X ligado)
    veiculos = sorted(
        [v for v in carregadores if v and v.v2x_habilitado and v.soc > 40],
        key=lambda x: x.soc,
        reverse=True
    )

    if not veiculos:
        print("Nenhum veículo com SoC > 40% disponível para injetar V2X.")
        return

    for v in veiculos:
        if deficit <= 0:
            break

        # Cada carro pode ceder no máximo 10 kW por ciclo ou o que resta do déficit
        energia = min(10, deficit)
        perda_soc = (energia / v.bateria_kwh) * 100

        v.soc -= perda_soc
        if v.soc < 0:
            v.soc = 0

        deficit -= energia
        energia_total += energia

        print(f"-> EV-{v.id} forneceu {energia:.1f} kW (Novo SoC: {v.soc:.1f}%)")

    # Injeta a energia gerada na variável global para o cálculo de potência
    energia_v2x = energia_total
    economia = energia_total * 0.90

    print("\nResultado do V2X:")
    print(f"Energia total injetada: {energia_total:.1f} kW")
    print(f"Economia estimada: R$ {economia:.2f}")

    saldo_final = LIMITE_CONTRATADO + geracao_solar + energia_v2x - consumo_predio
    if saldo_final >= 0:
        print("Status: Rede estabilizada com sucesso pelo V2X.")
    else:
        print(f"Status: V2X insuficiente. Déficit restante: {abs(saldo_final):.1f} kW")


def mostrar_painel():
    distribuir_potencia()
    limpar()

    total_ev = sum(v.potencia_atual for v in carregadores if v)

    print("=" * 70)
    print("CHARGEGRID INTELLIGENCE")
    print("=" * 70)
    print(f"Hora Simulada      : {hora}")
    print(f"Limite Contratado  : {LIMITE_CONTRATADO} kW")
    print(f"Geração Solar      : {geracao_solar} kW")
    print(f"Contribuição V2X   : {energia_v2x:.1f} kW")
    print(f"Consumo do Prédio  : {consumo_predio} kW")
    print(f"Carga Total EVs    : {total_ev:.1f} kW")
    print(f"Total Geral Usado  : {consumo_predio + total_ev:.1f} kW")

    saldo = LIMITE_CONTRATADO + geracao_solar + energia_v2x - consumo_predio
    print(f"Saldo Energético   : {saldo:.1f} kW")
    print("\nCARREGADORES")
    print("-" * 70)

    for i, v in enumerate(carregadores, start=1):
        if v is None:
            print(f"C{i}: LIVRE")
        else:
            v2x = "SIM" if v.v2x_habilitado else "NÃO"
            print(
                f"C{i}: EV-{v.id} | SoC={v.soc:.1f}% | Pot Cedida/Recebida={v.potencia_atual:.1f} kW | V2X_Habilitado={v2x}")
    print("-" * 70)


while True:
    mostrar_painel()

    print("\n1 - Adicionar veículo")
    print("2 - Remover veículo")
    print("3 - Alterar consumo do prédio")
    print("4 - Alterar geração solar")
    print("5 - Assistente Inteligente")
    print("6 - Executar V2X")
    print("X - Avançar 1 hora")
    print("0 - Sair")

    opcao = input("\nEscolha: ").upper()

    if opcao == "1":
        adicionar_veiculo()
    elif opcao == "2":
        remover_veiculo()
    elif opcao == "3":
        alterar_consumo()
    elif opcao == "4":
        alterar_solar()
    elif opcao == "5":
        assistente()
    elif opcao == "6":
        executar_v2x()
    elif opcao == "X":
        avancar_uma_hora()
    elif opcao == "0":
        print("\nEncerrando sistema...")
        break

    input("\nPressione ENTER para continuar...")