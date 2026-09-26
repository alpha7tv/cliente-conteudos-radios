#!/usr/bin/env python3
"""
Aplica a marca "Conteudos para Radios" no codigo-fonte oficial do cliente
desktop do Nextcloud (https://github.com/nextcloud/desktop).

Uso:
    python ferramentas/aplicar_marca.py <pasta-do-codigo-nextcloud-desktop>

Todas as informacoes da empresa ficam no bloco MARCA abaixo. Para mudar
nome, cor ou servidor, edite so aqui.
"""
import re
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# DADOS DA EMPRESA - edite aqui
# ---------------------------------------------------------------------------
MARCA = {
    # Nome que aparece nas janelas, no menu Iniciar e no instalador.
    # Evite acentos: eles podem quebrar caminhos e o registro do Windows.
    "nome": "Conteudos para Radios",
    # Nome curto, sem espacos (usado em pastas de configuracao e icones).
    "nome_curto": "ConteudosRadios",
    # Nome do arquivo .exe (minusculas, sem espacos).
    "executavel": "conteudosradios",
    "empresa": "Conteudos para Radios",
    "dominio": "midiaserver.com.br",
    # Servidor ja preenchido no assistente. O cliente so digita login e senha.
    "servidor": "https://nuvem.midiaserver.com.br",
    # True = o cliente so consegue conectar nesse servidor.
    "travar_servidor": True,
    # Azul mais escuro que o do Nextcloud (#0082c9) e texto branco.
    "cor_principal": "#00457C",
    "cor_texto_cabecalho": "#ffffff",
    # Identificadores internos (formato de dominio invertido).
    "rev_domain": "br.com.midiaserver.desktopclient",
    "rev_domain_dbus": "desktopclient.midiaserver.com.br",
}

# GUIDs proprios para as extensoes do Explorer e para o MSI.
# Sao fixos de proposito: se mudarem, o Windows trata cada versao como um
# programa diferente e as atualizacoes deixam instalacoes duplicadas.
GUIDS = {
    "WIN_SHELLEXT_CONTEXT_MENU_GUID": "{A5273479-74F2-4FAE-8A21-481D28995A94}",
    "WIN_SHELLEXT_OVERLAY_GUID_ERROR": "{46B252F1-EBC1-4906-90E1-5A3031B989A8}",
    "WIN_SHELLEXT_OVERLAY_GUID_OK": "{A3B2A33D-613E-4383-919E-01C7FC5C177F}",
    "WIN_SHELLEXT_OVERLAY_GUID_OK_SHARED": "{B3F646E6-1EED-48E3-A4EA-6E752322F859}",
    "WIN_SHELLEXT_OVERLAY_GUID_SYNC": "{20494B86-260B-4836-87A8-1ADE8D161C51}",
    "WIN_SHELLEXT_OVERLAY_GUID_WARNING": "{76E1A4A0-A3DC-4919-A3A7-A5A40D29C5FB}",
    "WIN_MSI_UPGRADE_CODE": "5E1E7C1A-5EDE-4ECC-BAD8-14C882533E78",
}

# IDs da extensao de "arquivos virtuais" do Explorer (ficam no CMakeLists.txt
# principal). Precisam ser diferentes dos do Nextcloud para os dois programas
# poderem conviver no mesmo PC.
GUIDS_CFAPI = {
    "CFAPI_SHELLEXT_APPID_REG": "{68A4EF0D-B8EA-4D3C-AF45-80814DC30B02}",
    "CFAPI_SHELLEXT_CUSTOM_STATE_HANDLER_CLASS_ID": "6500C4DB-8373-4E74-8C12-278F42256125",
    "CFAPI_SHELLEXT_THUMBNAIL_HANDLER_CLASS_ID": "AE446EBA-7C6F-45E6-A9F7-34E54445B0BA",
}

KIT = Path(__file__).resolve().parent.parent
ARQUIVOS_MARCA = KIT / "marca"


def trocar(texto: str, padrao: str, novo: str, descricao: str, contagem_min: int = 1) -> str:
    resultado, n = re.subn(padrao, novo, texto, flags=re.MULTILINE)
    if n < contagem_min:
        sys.exit(f"ERRO: nao encontrei '{descricao}' no NEXTCLOUD.cmake. "
                 "A versao do Nextcloud pode ter mudado; revise o padrao.")
    return resultado


def set_valor(texto: str, variavel: str, valor: str, contagem_min: int = 1) -> str:
    # Troca o primeiro argumento de: set( VARIAVEL "valor" ...)
    padrao = rf'(set\(\s*{variavel}\s+)"[^"]*"'
    return trocar(texto, padrao, lambda m: f'{m.group(1)}"{valor}"', variavel, contagem_min)


def set_opcao(texto: str, opcao: str, valor: str) -> str:
    padrao = rf'(option\(\s*{opcao}\s+"[^"]*"\s+)(ON|OFF)'
    return trocar(texto, padrao, lambda m: f"{m.group(1)}{valor}", opcao)


def ajustar_cmake(raiz: Path) -> None:
    arq = raiz / "NEXTCLOUD.cmake"
    t = arq.read_text(encoding="utf-8")
    m = MARCA

    # Nome (versao normal e versao "Dev", as duas ficam com a marca)
    t = set_valor(t, "APPLICATION_NAME", m["nome"], 2)
    t = set_valor(t, "APPLICATION_SHORTNAME", m["nome_curto"], 2)
    t = set_valor(t, "APPLICATION_EXECUTABLE", m["executavel"], 2)
    t = set_valor(t, "APPLICATION_DOMAIN", m["dominio"])
    t = set_valor(t, "APPLICATION_VENDOR", m["empresa"])

    # Sem atualizacao automatica pelo servidor do Nextcloud: ela baixaria o
    # cliente com a marca Nextcloud por cima do seu.
    t = set_valor(t, "APPLICATION_UPDATE_URL", "")
    t = set_opcao(t, "BUILD_UPDATER", "OFF")

    # Servidor pre-configurado
    t = set_valor(t, "APPLICATION_SERVER_URL", m["servidor"])
    t = trocar(t, r"(set\(\s*APPLICATION_SERVER_URL_ENFORCE\s+)(ON|OFF)",
               lambda mm: mm.group(1) + ("ON" if m["travar_servidor"] else "OFF"),
               "APPLICATION_SERVER_URL_ENFORCE")

    # Sem a lista de provedores de hospedagem do Nextcloud no assistente
    t = set_opcao(t, "WITH_PROVIDERS", "OFF")

    # Identificadores internos
    t = set_valor(t, "APPLICATION_REV_DOMAIN", m["rev_domain"])
    t = set_valor(t, "APPLICATION_REV_DOMAIN_DBUS", m["rev_domain_dbus"])
    t = set_valor(t, "APPLICATION_VIRTUALFILE_SUFFIX", m["executavel"])
    t = set_valor(t, "LINUX_PACKAGE_SHORTNAME", m["executavel"])

    # Cores
    t = set_valor(t, "NEXTCLOUD_BACKGROUND_COLOR", m["cor_principal"])
    t = set_valor(t, "APPLICATION_WIZARD_HEADER_TITLE_COLOR", m["cor_texto_cabecalho"])

    # GUIDs do Windows
    for var, guid in GUIDS.items():
        t = set_valor(t, var, guid)

    arq.write_text(t, encoding="utf-8")
    print("  NEXTCLOUD.cmake ajustado")

    arq = raiz / "CMakeLists.txt"
    t = arq.read_text(encoding="utf-8")
    for var, guid in GUIDS_CFAPI.items():
        t = trocar(t, rf'(set\(\s*{var}\s+)"[^"]*"', lambda mm, g=guid: f'{mm.group(1)}"{g}"', var)
    arq.write_text(t, encoding="utf-8")
    print("  CMakeLists.txt: IDs da extensao do Explorer trocados")


def copiar_arquivos(raiz: Path) -> None:
    for origem in ARQUIVOS_MARCA.rglob("*"):
        if origem.is_file():
            destino = raiz / origem.relative_to(ARQUIVOS_MARCA)
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, destino)
            print(f"  {destino.relative_to(raiz)}")


def ajustar_build_windows(raiz: Path) -> None:
    # Testes automatizados nao sao necessarios para gerar o instalador e
    # dobram o tempo de build.
    ini = raiz / "craftmaster.ini"
    if ini.exists():
        t = ini.read_text(encoding="utf-8")
        t = t.replace("nextcloud-client.buildTests = True", "nextcloud-client.buildTests = False")
        ini.write_text(t, encoding="utf-8")
        print("  craftmaster.ini: testes desligados")


def conferir(raiz: Path) -> None:
    nome = MARCA["nome_curto"]
    obrigatorios = [
        f"theme/colored/{nome}-icon.svg",
        f"theme/colored/{nome}-w10startmenu.svg",
        f"theme/{MARCA['executavel']}.VisualElementsManifest.xml",
        "theme/colored/wizard_logo.svg",
        "theme/colored/wizard_logo.png",
        "theme/colored/wizard_logo@2x.png",
    ]
    faltando = [p for p in obrigatorios if not (raiz / p).exists()]
    if faltando:
        sys.exit("ERRO: arquivos de marca faltando:\n  " + "\n  ".join(faltando))


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raiz = Path(sys.argv[1]).resolve()
    if not (raiz / "NEXTCLOUD.cmake").exists():
        sys.exit(f"ERRO: {raiz} nao parece ser o codigo do nextcloud/desktop")

    print(f"Aplicando a marca '{MARCA['nome']}' em {raiz}")
    ajustar_cmake(raiz)
    copiar_arquivos(raiz)
    ajustar_build_windows(raiz)
    conferir(raiz)
    print("Pronto.")


if __name__ == "__main__":
    main()
