# Trabalho Prático 2 — Set Covering Problem (SCP)
**DCC207 – Algoritmos 2 | Departamento de Ciência da Computação (UFMG)**

Este repositório contém a implementação dos algoritmos desenvolvidos para o Trabalho Prático 2 (TP2) da disciplina de Algoritmos 2 da UFMG. O objetivo deste trabalho é analisar o comportamento de algoritmos aproximativos (Heurística Gulosa) e exatos (Branch and Bound) para solucionar o **Set Covering Problem (SCP)**, avaliando seu desempenho em termos de qualidade de solução, tempo de execução, consumo de memória (RAM) e o impacto de limitantes e estratégias de poda.

---

## 🛠️ Tecnologias e Dependências

O projeto foi desenvolvido em **Python >= 3.12** utilizando as seguintes bibliotecas para processamento de dados e suporte matemático:
- **NumPy**: Manipulação eficiente de matrizes de cobertura e dados.
- **Pandas**: Processamento e consolidação de tabelas de resultados experimentais.
- **Matplotlib**: Geração de gráficos de análise experimental.
- **SciPy**: Operações científicas de suporte.

O gerenciamento de dependências pode ser realizado facilmente usando o gerenciador de pacotes rápido `uv` ou com `pip`.

---

## 📂 Estrutura de Arquivos

Abaixo está descrita a organização dos arquivos principais do repositório:

- **[`scp_types.py`](file:///home/nana/projects/tp2_alg2/scp_types.py)**: Define as estruturas de dados e classes de domínio para o problema (representando a classe de dados `SCPInstance`).
- **[`greedy.py`](file:///home/nana/projects/tp2_alg2/greedy.py)**: Implementação da heurística gulosa de aproximação para o SCP.
- **[`branch_and_bound.py`](file:///home/nana/projects/tp2_alg2/branch_and_bound.py)**: Implementação central do algoritmo exato Branch and Bound (suportando busca em Profundidade - DFS e busca de Melhor Escolha - Best-First, com limites superiores e inferiores configuráveis).
- **[`generator.py`](file:///home/nana/projects/tp2_alg2/generator.py)**: Lógica interna para geração de instâncias sintéticas uniformes e instâncias adversariais.
- **[`generate_synthetic_files.py`](file:///home/nana/projects/tp2_alg2/generate_synthetic_files.py)**: Script para gerar em lote e salvar os arquivos de instâncias sintéticas em formato padrão OR-Library.
- **[`benchmark.py`](file:///home/nana/projects/tp2_alg2/benchmark.py)**: Invólucro e lógica auxiliar para execução de experimentos individuais e coleta de métricas de tempo/nós.
- **[`benchmark_ram_time.py`](file:///home/nana/projects/tp2_alg2/benchmark_ram_time.py)**: Script especializado em medir o consumo de RAM e tempo de processamento empírico de forma controlada.
- **[`run_synthetic_experiments.py`](file:///home/nana/projects/tp2_alg2/run_synthetic_experiments.py)**: Automatiza a execução de todos os testes sintéticos (uniformes e adversariais).
- **[`run_reduced_real_benchmarks.py`](file:///home/nana/projects/tp2_alg2/run_reduced_real_benchmarks.py)**: Automatiza o benchmark para as instâncias reais reduzidas da OR-Library (Test Sets 4, 5, 6, A, B, C e D).
- **[`utils.py`](file:///home/nana/projects/tp2_alg2/utils.py)**: Funções de leitura de arquivos OR-Library, cálculo de limitantes matemáticos (Sum-Degree e Packing) e validação de cobertura das soluções.
- **[`test_all.py`](file:///home/nana/projects/tp2_alg2/test_all.py)**: Conjunto de testes de integração e testes em instâncias adversariais para assegurar a corretude dos resolvedores.

---

## ⚙️ Instalação e Preparação

### 1. Criando um ambiente virtual (Recomendado)
Usando a ferramenta padrão `venv` do Python:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalando as dependências
Com o ambiente ativado, instale as dependências listadas no `pyproject.toml`:
```bash
pip install -e .
```
Ou instale-as diretamente via `pip`:
```bash
pip install numpy pandas matplotlib scipy
```

---

## 🚀 Como Executar os Experimentos

### 1. Executar os testes de integração (Corretude)
Execute a suíte básica de testes locais para certificar-se de que a implementação gulosa e o Branch and Bound estão integrados e funcionando corretamente:
```bash
python test_all.py
```

### 2. Gerar as instâncias sintéticas
Para criar as instâncias uniformes e adversariais nas proporções exigidas nos testes locais:
```bash
python generate_synthetic_files.py
```
Isso povoará o diretório `data/synthetic/` com os arquivos `.txt` das instâncias correspondentes.

### 3. Rodar os benchmarks sintéticos
Execute a bateria de testes nas instâncias sintéticas para coletar dados de tempo, número de nós explorados e diferença de qualidade de solução:
```bash
python run_synthetic_experiments.py
```
Os dados consolidados serão gerados nos arquivos locais CSV (estes arquivos e suas análises ficam salvos localmente, sem poluir o repositório Git).

### 4. Rodar os benchmarks nas instâncias da OR-Library
Para avaliar os resolvedores nos conjuntos reduzidos das instâncias reais da OR-Library (Test Sets 4, 5, 6 e A, B, C, D):
```bash
python run_reduced_real_benchmarks.py
```
Os experimentos de B&B exato rodarão sob um timeout rígido e exportarão as métricas comparativas.

---

## 🧠 Detalhes de Implementação

### Algoritmo Guloso (Aproximativo)
A heurística gulosa escolhe sucessivamente o subconjunto com a maior razão entre elementos não cobertos e o custo do conjunto. O pior caso de aproximação teórica, limitado a $H(m) \approx \ln(m)$, é testado empiricamente por meio de instâncias geradas adversariamente em `generator.py`.

### Branch and Bound (Exato)
A árvore de exploração do B&B implementa a decisão binária de selecionar ou não cada subconjunto.
1. **Estratégias de Busca**:
   - **DFS (Depth-First)**: Explora caminhos profundamente. Limita o consumo de memória à profundidade da árvore.
   - **Best-First**: Utiliza uma fila de prioridades para priorizar nós com menor limitante inferior estimado. Possui um limite de segurança de 50.000 nós para prevenir estouro de RAM física.
2. **Limitantes Inferiores (Lower Bounds)**:
   - **Sum-Degree**: Estimativa rápida baseada na cobertura restante ponderada pelo grau máximo de cobertura restante.
   - **Packing**: Modelado como um conjunto independente máximo de subconjuntos mutuamente disjuntos (grafo de conflitos), fornecendo podas extremamente potentes.
   - **Both**: Abordagem sequencial que calcula o Sum-Degree primeiro e recorre ao Packing apenas se o nó não pôde ser podado de imediato, otimizando o overhead computacional por nó.
3. **Limitantes Superiores Iniciais (Upper Bounds)**:
   - Permite inicializar o limite de poda superior (`best_cost`) tanto com um limitante **Trivial** (soma dos custos de todos os conjuntos) quanto com o limitante gerado pela **Heurística Gulosa**, acelerando as podas no início da exploração exata.
