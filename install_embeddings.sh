#!/bin/bash
# Script de instalação de embeddings para Template Selector
# Uso: ./install_embeddings.sh

set -e

echo "🚀 Instalando dependências de embeddings para Template Selector..."
echo ""

# Verificar se está no diretório correto
if [ ! -f "requirements_templates.txt" ]; then
    echo "❌ Erro: requirements_templates.txt não encontrado!"
    echo "   Execute este script no diretório raiz do projeto."
    exit 1
fi

# Verificar se pip está disponível
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ Erro: pip não encontrado!"
    echo "   Instale o pip primeiro: sudo apt-get install python3-pip"
    exit 1
fi

# Usar pip3 se disponível, senão pip
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo "📦 Instalando pacotes..."
echo ""

# Tentar instalação normal primeiro
if $PIP_CMD install -r requirements_templates.txt; then
    echo ""
    echo "✅ Instalação concluída com sucesso!"
    echo ""
    echo "Para verificar, execute:"
    echo "  python3 -c \"from sentence_transformers import SentenceTransformer; print('✅ OK!')\""
else
    echo ""
    echo "⚠️  Instalação normal falhou. Tentando com --user..."
    echo ""
    
    if $PIP_CMD install --user -r requirements_templates.txt; then
        echo ""
        echo "✅ Instalação concluída com sucesso (--user)!"
        echo ""
        echo "Para verificar, execute:"
        echo "  python3 -c \"from sentence_transformers import SentenceTransformer; print('✅ OK!')\""
    else
        echo ""
        echo "❌ Instalação falhou. Tente manualmente:"
        echo "   $PIP_CMD install --user sentence-transformers"
        echo ""
        echo "Ou use um ambiente virtual:"
        echo "   python3 -m venv venv"
        echo "   source venv/bin/activate"
        echo "   pip install -r requirements_templates.txt"
        exit 1
    fi
fi
