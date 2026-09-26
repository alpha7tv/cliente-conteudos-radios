#!/usr/bin/env python3
"""
Ajusta a receita de empacotamento (Craft) do cliente para que o instalador
.exe saia com o nome, a empresa, o icone e o atalho do menu Iniciar da marca.

Usado pelo workflow do GitHub depois que o Craft baixou suas receitas:
    python ferramentas/ajustar_instalador_craft.py <pasta-onde-procurar>
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplicar_marca import MARCA  # noqa: E402

NOVO_BLOCO = '''        # --- marca {nome} ---
        from pathlib import Path
        self.defines["appname"] = "{exe}"
        self.defines["company"] = "{empresa}"
        self.defines["productname"] = "{nome}"
        self.defines["display_name"] = "{nome}"
        self.defines["description"] = "{nome} - sincronizacao de arquivos"
        self.defines["website"] = "https://{dominio}"
        self.defines["executable"] = "bin\\\\{exe}.exe"
        _icones = list(Path(self.buildDir()).rglob("{curto}.ico"))
        if _icones:
            self.defines["icon"] = _icones[0]
        self.applicationExecutable = "{exe}"
        # --- fim da marca ---'''


def main() -> None:
    raiz = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not raiz.exists() or not any(raiz.rglob("nextcloud-client.py")):
        # Craft guardou as receitas em outro lugar: procura na pasta de trabalho inteira
        print(f"  receita nao esta em {raiz}; procurando em {raiz.parent.parent}")
        raiz = raiz.parent.parent
    receitas = [p for p in raiz.rglob("nextcloud-client.py")
                if p.parent.name == "nextcloud-client" and "craft-blueprints-nextcloud" in str(p)]
    if not receitas:
        receitas = [p for p in raiz.rglob("nextcloud-client.py") if p.parent.name == "nextcloud-client"]
    if not receitas:
        sys.exit(f"ERRO: receita nextcloud-client.py nao encontrada em {raiz}")

    bloco = NOVO_BLOCO.format(nome=MARCA["nome"], exe=MARCA["executavel"], empresa=MARCA["empresa"],
                              dominio=MARCA["dominio"], curto=MARCA["nome_curto"])
    for arq in receitas:
        t = arq.read_text(encoding="utf-8")
        if "--- marca" in t:
            print(f"  ja ajustado: {arq}")
            continue
        padrao = (r'^\s*self\.defines\["appname"\]\s*=\s*"nextcloud"\s*\n'
                  r'\s*self\.defines\["company"\]\s*=\s*"Nextcloud GmbH"\s*\n'
                  r'\s*self\.applicationExecutable\s*=\s*"nextcloud"\s*$')
        t, n = re.subn(padrao, lambda _: bloco, t, flags=re.MULTILINE)
        if n != 1:
            sys.exit(f"ERRO: formato inesperado em {arq}; a receita do Nextcloud mudou.")
        if not re.search(r"^import os\b", t, flags=re.M):
            t = re.sub(r"^(import info\s*)$", r"import os\n\1", t, count=1, flags=re.M)
        arq.write_text(t, encoding="utf-8")
        print(f"  receita ajustada: {arq}")


if __name__ == "__main__":
    main()
