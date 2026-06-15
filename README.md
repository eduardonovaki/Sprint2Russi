# Sistema de Gerenciamento Dinâmico de Carga para Veículos Elétricos

## Descrição

Este projeto simula um sistema de gerenciamento dinâmico de carga para carregadores de veículos elétricos em um shopping, condomínio ou edifício comercial.

O objetivo é distribuir a potência disponível entre os veículos conectados sem ultrapassar o limite de energia contratado pelo prédio, priorizando veículos com menor nível de bateria (SoC - State of Charge).

## Funcionalidades

* Cadastro manual de veículos elétricos.
* Remoção manual de veículos.
* Controle do consumo do prédio.
* Simulação do avanço do tempo em intervalos de 1 hora.
* Distribuição automática da potência disponível.
* Priorização de veículos com menor nível de bateria.
* Exibição do status de todos os carregadores.
* Interrupção automática da carga quando o veículo atinge 100% de bateria.

## Como funciona

A potência disponível para os carregadores é calculada pela fórmula:

```text
Potência Disponível = Limite Contratado - Consumo do Prédio
```

Quando a demanda dos veículos ultrapassa a potência disponível, o sistema reduz a potência distribuída de forma proporcional, dando prioridade aos veículos com menor SoC.

## Menu

```text
1 - Adicionar veículo
2 - Remover veículo
3 - Alterar consumo do prédio
X - Avançar 1 hora
0 - Sair
```

## Tecnologias Utilizadas

* Python 3
* Dataclasses

## Objetivo Acadêmico

Este projeto foi desenvolvido para demonstrar conceitos de:

* Mobilidade elétrica
* Smart Charging
* Gerenciamento de demanda energética
* Simulação de sistemas de carregamento de veículos elétricos

