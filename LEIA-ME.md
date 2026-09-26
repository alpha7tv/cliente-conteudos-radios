# Cliente desktop "Conteudos para Radios"

Kit para gerar o instalador Windows do cliente de sincronização com a marca da
empresa, a partir do código oficial do Nextcloud (versão base: **v34.0.4**).

## O que já está configurado

| Item | Valor |
|---|---|
| Nome do programa | Conteudos para Radios |
| Arquivo do programa | `conteudosradios.exe` |
| Servidor | `https://nuvem.midiaserver.com.br` (já preenchido e travado) |
| Cor principal | Azul escuro `#00457C` com texto branco |
| Atualização automática do Nextcloud | Desligada (senão ela instalaria o Nextcloud original por cima) |
| Lista de provedores de hospedagem do Nextcloud | Removida |
| IDs do Windows (Explorer, MSI) | Próprios, então pode conviver com o Nextcloud original no mesmo PC |
| Logo | **Provisório** (ondas de rádio). Veja o passo 1 |

Todos esses valores ficam no bloco `MARCA` de `ferramentas/aplicar_marca.py`.
Para mudar nome, cor ou servidor, edite só ali.

## Passo a passo

### 1. Colocar o logo real

Precisa de Python instalado no PC (python.org).

```
pip install pillow
python ferramentas/trocar_logo.py caminho/do/logo.png
```

Se tiver uma versão quadrada do logo (só o símbolo), use também:

```
python ferramentas/trocar_logo.py logo-completo.png --icone simbolo.png
```

Dicas: PNG com fundo transparente, 512 px ou mais. O ícone precisa ser
legível em 16 px (barra de tarefas), por isso um símbolo simples funciona
melhor que um logo com texto. Se o logo for escuro, o script coloca um fundo
branco atrás dele automaticamente.

### 2. Subir o kit para o GitHub

1. Crie uma conta em github.com (se não tiver) e um repositório novo,
   por exemplo `cliente-conteudos-radios`.
2. Envie **todo o conteúdo desta pasta** para o repositório, incluindo a pasta
   oculta `.github`. Pelo site: "Add file" > "Upload files" e arraste os
   arquivos. A pasta `.github` às vezes não aparece no Windows Explorer;
   ative "Mostrar itens ocultos" ou use o GitHub Desktop.

### 3. Gerar o instalador

1. No repositório, abra a aba **Actions** > **Gerar instalador Windows** >
   **Run workflow**.
2. A primeira execução demora de 1h30 a 3h, porque compila o Qt e as outras
   dependências. As seguintes reaproveitam o cache e ficam bem mais rápidas.
3. Ao terminar, o instalador aparece em **Artifacts**, no fim da página da
   execução: `ConteudosParaRadios-Setup-v34.0.4.exe`.

Se o repositório for privado, o GitHub dá uma cota mensal de minutos
gratuitos para Windows que pode não cobrir o primeiro build. Em repositório
público é gratuito. O código aqui não tem senhas, então público não é
problema (e isso também cumpre a licença GPL, veja abaixo).

### 4. Assinar o instalador (recomendado)

Sem assinatura digital, o Windows mostra "Editor desconhecido" e o
SmartScreen pode bloquear o download. Para evitar:

1. Compre um certificado de assinatura de código (Code Signing) em nome da
   empresa, de uma autoridade como Certum, Sectigo ou DigiCert.
2. No GitHub: Settings > Secrets and variables > Actions > New repository
   secret. Crie:
   - `CERT_PFX_BASE64`: o arquivo `.pfx` convertido em texto. No PowerShell:
     `[Convert]::ToBase64String([IO.File]::ReadAllBytes("cert.pfx")) | Set-Clipboard`
   - `CERT_SENHA`: a senha do `.pfx`
3. Rode o workflow de novo. A assinatura é aplicada automaticamente.

Observação: desde 2023 muitos certificados vêm em token físico (USB) ou em
nuvem, e não como `.pfx`. Nesse caso a etapa de assinatura precisa ser
adaptada ao serviço do fornecedor.

### 5. Testar antes de distribuir

Instale num PC de teste e confira: nome e ícone no menu Iniciar, logo e cor
no assistente de conexão, servidor já preenchido, login funcionando e
sincronização de uma pasta. Depois disso, publique o `.exe` no site da empresa.

## Atualizar para uma versão nova do Nextcloud

Ao rodar o workflow, troque o campo "Versão do cliente Nextcloud" pela tag
nova (lista em github.com/nextcloud/desktop/releases, use só versões finais,
sem "rc" ou "beta"). Os clientes instalam o novo `.exe` por cima do antigo,
sem perder a configuração.

## Licença e marca registrada

- O cliente Nextcloud é software livre (GPL versão 2 ou posterior). Ao
  distribuir o instalador, vocês precisam oferecer o código-fonte. Este
  repositório + a tag oficial do Nextcloud usada cumprem isso: basta deixar o
  repositório público ou enviar o código a quem pedir.
- "Nextcloud" e seu logo são marcas registradas da Nextcloud GmbH. Este kit
  troca nome, logo e cores para a identidade da empresa. Não use o nome ou o
  logo do Nextcloud na divulgação do programa.

## Arquivos do kit

```
.github/workflows/gerar-instalador-windows.yml   build automático no GitHub
ferramentas/aplicar_marca.py                     dados da marca e aplicação no código
ferramentas/trocar_logo.py                       troca o logo provisório pelo real
ferramentas/ajustar_instalador_craft.py          nome/ícone/atalho do instalador .exe
marca/                                           ícones, logo e arquivos do Windows
```
