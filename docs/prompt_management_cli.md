# Gerenciamento de Prompts via CLI

## Visão Geral

O comando `prompts` foi integrado ao CLI principal do projeto, facilitando o registro e atualização de prompts no banco de dados.

## Integração no CLI

O comando está disponível como subcomando do CLI principal:

```bash
python -m src.cli.commands prompts [opções]
```

## Uso

### Registro Inicial

```bash
# Registrar todos os prompts do diretório padrão (prompts/)
python -m src.cli.commands prompts
```

### Atualizar Metadados

```bash
# Atualizar metadados de prompts existentes
python -m src.cli.commands prompts --update-metadata
```

### Diretório Customizado

```bash
# Especificar diretório diferente
python -m src.cli.commands prompts --prompts-dir /caminho/customizado
```

### Modo Silencioso

```bash
# Menos output (útil para scripts)
python -m src.cli.commands prompts --quiet
```

## Opções Disponíveis

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| `--prompts-dir PATH` | Diretório com arquivos .md | `prompts/` |
| `--update-metadata` | Atualiza metadados existentes | `False` |
| `--quiet` | Modo silencioso | `False` |

## O que o Comando Faz

1. **Escaneia** o diretório em busca de arquivos `.md`
2. **Calcula métricas** para cada prompt:
   - Tamanho (caracteres, palavras, linhas)
   - Placeholders (variáveis do template)
   - Complexidade (score e nível)
   - Tokens estimados
3. **Registra** com versionamento automático:
   - Primeira vez: cria v1
   - Template diferente: cria v2, v3, etc.
   - Template idêntico: retorna versão existente (sem duplicata)
4. **Armazena metadados** completos no banco de dados

## Exemplo de Fluxo de Trabalho

### Setup Inicial

```bash
# 1. Registrar todos os prompts
python -m src.cli.commands prompts

# 2. Executar pipeline
python -m src.cli.commands full --article articles/artigo.md
```

### Após Modificar Prompts

```bash
# 1. Atualizar metadados dos prompts modificados
python -m src.cli.commands prompts --update-metadata

# 2. Continuar usando o pipeline normalmente
python -m src.cli.commands ideas --article articles/artigo.md
```

## Integração com Outros Comandos

O comando `prompts` é independente e pode ser executado a qualquer momento:

```bash
# Workflow completo
python -m src.cli.commands prompts                    # Registrar prompts
python -m src.cli.commands ideas --article artigo.md  # Gerar ideias
python -m src.cli.commands briefs --ideas-json ...    # Gerar briefs
```

## Vantagens da Integração CLI

1. **Acesso unificado**: Todos os comandos em um só lugar
2. **Consistência**: Mesma interface para todas as operações
3. **Facilidade**: Não precisa lembrar caminho do script
4. **Integração**: Funciona com outras opções globais do CLI

## Comparação: Script vs CLI

### Script Standalone

```bash
python scripts/register_prompts_from_directory.py
```

### CLI Integrado

```bash
python -m src.cli.commands prompts
```

**Vantagens do CLI:**
- ✅ Integrado ao sistema principal
- ✅ Mesma interface que outros comandos
- ✅ Mais fácil de descobrir (`--help`)
- ✅ Consistente com workflow do projeto

## Referências

- [Comandos CLI Completos](./cli_commands.md)
- [Sistema de Versionamento](./prompt_versioning_automatic.md)
- [Script de Registro](./register_prompts_script.md)

