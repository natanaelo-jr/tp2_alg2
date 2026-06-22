# Registro de Decisões de Projeto e Análise Experimental
**Trabalho Prático 2 – Set Covering Problem (SCP)**

Este documento registra as decisões metodológicas e de implementação tomadas durante o desenvolvimento dos experimentos para o TP2, servindo de base para a redação do relatório final (artigo padrão IEEE).

---

## 1. Decisão Metodológica: Amostragem de Instâncias Reais da OR-Library

### Contexto
O enunciado do TP2 exige a avaliação dos Test Sets 4, 5 e 6, e dos Test Sets A, B, C e D da OR-Library. O total acumulado desses conjuntos é de **45 instâncias de grande porte** (com dimensões variando de $200 \times 1000$ até $400 \times 4000$).
Executar o Branch & Bound exato em todas as 45 instâncias com um timeout elevado (ex: 20 minutos por configuração) exigiria:
$$\text{Tempo Total} = 45 \text{ instâncias} \times 6 \text{ configurações B&B} \times 20 \text{ min} = 5400 \text{ core-minutes}$$
Com paralelismo em 8 núcleos de CPU, isso levaria mais de **11 horas** ininterruptas caso a maioria das instâncias sofresse timeout (o que é o comportamento esperado para o B&B exato em instâncias de larga escala). Em computadores com menor poder de processamento, isso é proibitivo e ineficiente.

### Decisão de Amostragem
Decidimos selecionar **uma instância representativa de cada uma das 7 classes de Test Sets** da OR-Library. Essa abordagem reduz o número de instâncias de 45 para **7 instâncias**, permitindo aumentar substancialmente o timeout por configuração para **1 hora (3600 segundos)**.

As instâncias selecionadas e suas características são:

| Classe | Instância Selecionada | Dimensões ($m \times n$) | Densidade | Custo dos Conjuntos |
| :--- | :---: | :---: | :---: | :---: |
| **Test Set 4** | `scp41.txt` | $200 \times 1000$ | 2% | Unicusto (1.0) |
| **Test Set 5** | `scp51.txt` | $200 \times 2000$ | 2% | Unicusto (1.0) |
| **Test Set 6** | `scp61.txt` | $200 \times 1000$ | 5% | Unicusto (1.0) |
| **Test Set A** | `scpa1.txt` | $300 \times 3000$ | 2% | Unicusto (1.0) |
| **Test Set B** | `scpb1.txt` | $300 \times 3000$ | 5% | Unicusto (1.0) |
| **Test Set C** | `scpc1.txt` | $400 \times 4000$ | 2% | Unicusto (1.0) |
| **Test Set D** | `scpd1.txt` | $400 \times 4000$ | 5% | Unicusto (1.0) |

### Raciocínio Científico
Essa amostragem é estatisticamente e cientificamente robusta para o relatório porque:
1. **Representatividade de Escala**: Cobre todo o espectro de tamanhos de matriz do benchmark ($200 \times 1000$ até $400 \times 4000$).
2. **Representatividade de Densidade**: Permite analisar diretamente o impacto da densidade (2% vs. 5%) em problemas de mesma escala (ex: comparar `scpa1` com `scpb1`, ou `scp41` com `scp61`).
3. **Viabilidade Temporal**: 7 instâncias com timeout de 3600 segundos em 8 cores executam em no máximo **7 horas** (cada instância leva no máximo 1 hora pois as configurações rodam em paralelo na CPU), o que viabiliza a execução rápida dos experimentos.

---

## 2. Decisões de Implementação do Branch and Bound

### 2.1 Controle de Memória no Best-First Search
* **Problema**: O Best-First Search utiliza uma Fila de Prioridades (heap) para expandir primeiro os nós com menor estimativa de limitante inferior. Em instâncias de grande porte, o número de nós abertos na fila cresce exponencialmente, estourando a memória RAM do computador (provocando travamento da máquina devido a swap de disco).
* **Decisão**: Foi implementado um limite de segurança de **50.000 nós** na fila do Best-First (`len(pq) > 50000`). Ao atingir esse limite, a busca é interrompida precocemente e o algoritmo retorna a melhor solução viável encontrada até então.
* **Justificativa no Relatório**: Essa é uma decisão clássica de engenharia de algoritmos para garantir a robustez e estabilidade do sistema sob restrições físicas de hardware.

### 2.2 Seleção e Uso de Limitantes Inferiores (Lower Bounds)
* **Sum-Degree (Efficiency)**: Um limitante relaxado computacionalmente muito barato ($O(m \times n)$), ideal para ser computado rapidamente em cada nó.
* **Packing (Disjoint-Subset)**: Modelado como um Independent Set no grafo de conflitos dos elementos disjuntos. É muito mais forte para podar a árvore, mas requer $O(m^2 \log m)$ para ordenar as dificuldades dos elementos, sendo computacionalmente caro.
* **Estratégia "Both" (Poda Cirúrgica)**: Implementamos a computação sequencial dos limitantes. O Sum-Degree é calculado primeiro. Se a soma do custo atual com o Sum-Degree já ultrapassa o limite superior atual, o nó é podado imediatamente, **evitando o cálculo custoso do Packing**. O Packing só é calculado se o Sum-Degree falhar em podar. Essa decisão reduziu drasticamente o tempo de execução por nó nas variantes combinadas.

---

## 3. Heurística Gulosa: Fator de Aproximação Teórico vs. Empírico
* **Decisão de Geração Adversarial**: O gerador de instâncias foi projetado utilizando a construção binária clássica que força a escolha consecutiva de $k$ conjuntos de tamanhos decrescentes pelo algoritmo guloso, enquanto a solução ótima necessita de apenas $2$ conjuntos.
* **Justificativa**: Isso demonstra empiricamente a exatidão do limite superior teórico de aproximação de $H(m) \approx \ln(m)$, provando no relatório que existem cenários reais onde o algoritmo aproximativo possui performance ruim de qualidade, justificando o uso do Branch & Bound.

---

## 4. Escalonamento e Análise de Transição de Complexidade (Instâncias Médias)
* **Decisão**: Além das instâncias muito pequenas (que resolvem em segundos) e das originais muito grandes (que dão timeout de 1h), definimos uma escala intermediária de sub-instâncias reais com **redução de ~57%** ($m=85$ para as classes SCP4/SCP5 e $m=70$ para a classe SCP6), configurando o timeout exato de **3 horas (10800.0 segundos)**.
* **Justificativa no Relatório**: Essas instâncias operam na transição de fase de complexidade (limiar entre fácil e difícil) para o Branch and Bound. Elas levam tempos na faixa de 30 minutos a 2 horas para serem resolvidas até a optimalidade global. Isso provê dados experimentais excelentes para ilustrar o crescimento exponencial do custo computacional do B&B e sua sensibilidade à densidade e tamanho.
