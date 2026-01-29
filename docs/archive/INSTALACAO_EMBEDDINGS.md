# Instalação de Embeddings para Template Selector

Este guia explica como instalar as dependências necessárias para o sistema de seleção semântica de templates usando embeddings.

## 📋 Requisitos

O arquivo `src/templates/selector.py` usa a biblioteca `sentence-transformers` para gerar embeddings semânticos de alta qualidade. Sem essa biblioteca, o sistema usa um método de fallback baseado em palavras-chave.

## 🚀 Instalação

### Opção 1: Instalação Direta (Recomendado)

```bash
# No diretório do projeto
cd /home/jescott/syntropy-cc/botique

# Instalar todas as dependências de embeddings
pip install -r requirements_templates.txt
```

### Opção 2: Instalação Mínima (Apenas sentence-transformers)

Se você quiser instalar apenas o essencial:

```bash
pip install sentence-transformers
```

O `sentence-transformers` instalará automaticamente suas dependências:
- `torch` (PyTorch)
- `transformers` (Hugging Face)
- `numpy`
- E outras dependências necessárias

### Opção 3: Usando Ambiente Virtual (Recomendado para Produção)

Para isolar as dependências e evitar conflitos:

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# No Linux/Mac:
source venv/bin/activate
# No Windows:
# venv\Scripts\activate

# Instalar dependências
pip install -r requirements_templates.txt
```

## ✅ Verificação

Após a instalação, você pode verificar se está funcionando:

```python
from sentence_transformers import SentenceTransformer

# Testar carregamento do modelo padrão
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Embeddings instalados e funcionando!")
```

Ou execute o seletor de templates:

```python
from src.templates.selector import TemplateSelector

selector = TemplateSelector()
# Se não houver avisos sobre fallback, está funcionando!
```

## 📦 Dependências Instaladas

O arquivo `requirements_templates.txt` instala:

- **sentence-transformers** (>=2.2.0): Biblioteca principal para embeddings
- **torch** (>=1.9.0): PyTorch para modelos de deep learning
- **transformers** (>=4.20.0): Biblioteca Hugging Face para modelos
- **numpy** (>=1.19.0): Operações numéricas

## 🔧 Modelos Disponíveis

O sistema usa por padrão o modelo `all-MiniLM-L6-v2`, que é:
- ✅ Rápido e eficiente
- ✅ Otimizado para inglês
- ✅ Pequeno (~80MB)

### Modelos Alternativos

Você pode especificar outros modelos ao inicializar o `TemplateSelector`:

```python
# Multilíngue (mais lento, mas suporta português)
selector = TemplateSelector(model_name="paraphrase-multilingual-MiniLM-L12-v2")

# Maior qualidade (mais lento)
selector = TemplateSelector(model_name="all-mpnet-base-v2")

# Padrão (rápido, inglês)
selector = TemplateSelector(model_name="all-MiniLM-L6-v2")
```

## ⚠️ Solução de Problemas

### Erro de Permissão

Se você encontrar erros de permissão:

```bash
# Usar --user para instalar no diretório do usuário
pip install --user -r requirements_templates.txt

# Ou usar sudo (não recomendado)
sudo pip install -r requirements_templates.txt
```

### Espaço em Disco

Os modelos podem ocupar bastante espaço:
- `all-MiniLM-L6-v2`: ~80MB
- `paraphrase-multilingual-MiniLM-L12-v2`: ~420MB
- `all-mpnet-base-v2`: ~420MB

Certifique-se de ter pelo menos 500MB livres.

### Primeira Execução

Na primeira vez que você usar um modelo, ele será baixado automaticamente do Hugging Face. Isso pode levar alguns minutos dependendo da sua conexão.

## 📝 Notas

- O sistema tem **fallback automático**: se `sentence-transformers` não estiver disponível, usa método baseado em palavras-chave
- Os embeddings são **pré-computados** na inicialização para melhor performance
- O cache de embeddings é mantido em memória durante a execução

## 🔗 Referências

- [Documentação sentence-transformers](https://www.sbert.net/)
- [Modelos disponíveis no Hugging Face](https://huggingface.co/models?library=sentence-transformers)
- [Documentação do Template Selector](./SEMANTIC_TEMPLATE_SELECTION.md)
