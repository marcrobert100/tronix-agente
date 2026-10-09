# Gerador de Licenças TRONIX - Formato 11 Dígitos

Sistema de geração de chaves numéricas de 11 dígitos, criado para ser compatível com o padrão do **Ativador UnitvFree**.

## Arquivos Criados

| Arquivo | Descrição |
|---|---|
| `licenca_tronix_11dig_v2.py` | Módulo principal - gera e valida chaves 11 dígitos |
| `gerador_11dig_gui.py` | Interface gráfica para gerar múltiplas chaves |
| `validador_11dig.py` | Interface gráfica para validar chaves |
| `Ativador-UnitvFree-11Dig.bat` | Menu principal |
| `Gerador 11 Digitos TRONIX.bat` | Atalho direto ao gerador |
| `Validador 11 Digitos TRONIX.bat` | Atalho direto ao validador |

## Como Usar

### Método 1: Menu Principal (Recomendado)

Clique em **`Ativador-UnitvFree-11Dig.bat`** na Área de Trabalho ou em `C:\xampp\htdocs\agente\`

### Método 2: Direto

**Gerar chaves:**
```cmd
cd C:\xampp\htdocs\agente
python gerador_11dig_gui.py
```

**Validar chaves:**
```cmd
cd C:\xampp\htdocs\agente
python validador_11dig.py
```

**Console:**
```cmd
cd C:\xampp\htdocs\agente
python licenca_tronix_11dig_v2.py
```

## Características

- **Formato:** 11 dígitos numéricos (Ex: `77814248122`)
- **Checksum:** Dígito verificador calculado por algoritmo mod10 alternado
- **Únicas:** Usa `time.time_ns()` + `os.urandom()` para garantir unicidade
- **Segurança:** Baseado em HMAC-SHA256 para geração determinística
- **Lote:** Gera até 100 chaves simultaneamente
- **Interface moderna:** Tema dark com destaque em dourado (#ffd700)

## Exemplo de Uso Programático

```python
from licenca_tronix_11dig_v2 import Licenca11Digitos

lic = Licenca11Digitos()

# Gerar 1 chave
chave = lic.gerar_chave("Cliente Exemplo")
print(chave)  # Ex: 77814248122

# Validar
valida, dados = lic.validar_chave(chave)
if valida:
    print("✓ Válida")
else:
    print("✗ Inválida:", dados['erro'])
```

## Validando pelo Sistema

1. Abra o **Validador 11 Dígitos TRONIX**
2. Cole a chave de 11 dígitos
3. Clique em **VALIDAR CHAVE**
4. Verifica formato + checksum automaticamente

## Evolução do Sistema

O sistema foi evoluído do anterior (base64url com expiração) para o formato **puramente numérico de 11 dígitos**, exatamente como solicitado.

**Desenvolvido por TRONIX | Marcos Roberto**
