# Sistema de Licenciamento TRONIX

Sistema legítimo de geração e validação de códigos de ativação com criptografia HMAC-SHA256.

## Arquivos Criados

| Arquivo | Descrição |
|---|---|
| `licenca_tronix.py` | Módulo principal (console) - gera, valida e exporta licenças |
| `gerador_licencas_gui.py` | Interface gráfica para gerar licenças |
| `validador_licencas_gui.py` | Interface gráfica para validar licenças |
| `iniciar_licencas.bat` | Menu de inicialização |

## Como Usar

### 1. Modo Console

```bash
python licenca_tronix.py
```

Opções disponíveis:
- 1. Gerar nova licença
- 2. Validar licença
- 3. Gerar licença para cliente específico (salva arquivo .txt)
- 4. Sair

### 2. Interface Gráfica

Execute o menu principal:

```bash
iniciar_licencas.bat
```

Ou diretamente:

**Gerador:**
```bash
python gerador_licencas_gui.py
```

**Validador:**
```bash
python validador_licencas_gui.py
```

## Como Funciona

O sistema utiliza **HMAC-SHA256** para assinar digitalmente cada licença.

### Estrutura da Chave

A chave é gerada a partir de:
- Nome do cliente
- Data de emissão
- Data de expiração
- Versão do sistema
- Assinatura criptográfica com chave secreta

Todo o payload é codificado em **Base64URL** (sem padding desnecessário).

### Validação

Ao validar uma chave, o sistema:
1. Decodifica a chave em Base64URL
2. Separa payload + assinatura (16 bytes)
3. Recalcula HMAC-SHA256 com a chave secreta
4. Compara assinaturas (timing-safe)
5. Verifica se não está expirada

## Segurança

- Chave secreta está definida em `licenca_tronix.py` (`SECRET_KEY`)
- Para uso em produção, **ALTERE** a `SECRET_KEY` para um valor único e aleatório
- Assinaturas truncadas em 128 bits (16 bytes) - suficiente para este propósito
- Uso de `hmac.compare_digest` para evitar timing attacks

## Exemplo de Uso Programático

```python
from licenca_tronix import LicencaTronix

lic = LicencaTronix()

# Gerar licença
chave = lic.gerar_chave("Empresa XYZ", dias_validade=365)
print(chave)

# Validar licença
valida, dados = lic.validar_chave(chave)
if valida:
    print(f"Válida! Cliente: {dados['cliente']}, Dias restantes: {dados['dias_restantes']}")
else:
    print(f"Inválida: {dados['erro']}")
```

## Integração com Aplicativos

Você pode integrar esse sistema em qualquer aplicação Python:

```python
# ativacao.py
from licenca_tronix import LicencaTronix

def ativar(chave):
    lic = LicencaTronix()
    return lic.validar_chave(chave)

# No seu app
if __name__ == '__main__':
    chave = input("Digite sua chave de ativação: ")
    ok, info = ativar(chave)
    if ok:
        print("Ativado com sucesso!")
    else:
        print("Chave inválida!")
        sys.exit(1)
```

## Recursos

- ✓ Geração segura com HMAC-SHA256
- ✓ Validação com verificação de assinatura
- ✓ Controle de expiração por data
- ✓ Interface CLI e GUI (Tkinter)
- ✓ Exportação automática para arquivo .txt
- ✓ Sistema 100% legítimo para uso próprio

**Desenvolvido por TRONIX | Marcos Roberto**
