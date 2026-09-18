/**
 * Recebe as respostas da pesquisa e grava numa planilha do Google.
 *
 * Como instalar (uma vez só, leva uns 3 minutos):
 *  1. Crie uma planilha nova em sheets.new
 *  2. Menu Extensões -> Apps Script
 *  3. Apague o que estiver lá e cole este arquivo inteiro
 *  4. Troque a CHAVE_LEITURA abaixo por qualquer senha sua
 *  5. Implantar -> Nova implantação -> tipo "App da Web"
 *       Executar como: Eu
 *       Quem pode acessar: Qualquer pessoa
 *  6. Copie o endereço que termina em /exec
 *  7. Cole esse endereço no arquivo config.json do app, junto com a chave
 */

const ABA = "Respostas";
const CHAVE_LEITURA = "troque-esta-chave";

/** Recebe uma resposta e acrescenta uma linha. */
function doPost(e) {
  const trava = LockService.getScriptLock();
  try {
    trava.waitLock(15000);   // evita duas respostas escrevendo na mesma linha
    const dados = JSON.parse(e.postData.contents);
    if (!Array.isArray(dados.linha) || !Array.isArray(dados.cabecalho))
      return json({ ok: false, erro: "formato inesperado" });

    const aba = abaDeRespostas();
    if (aba.getLastRow() === 0) {
      aba.appendRow(dados.cabecalho);
      aba.getRange(1, 1, 1, dados.cabecalho.length)
         .setFontWeight("bold").setBackground("#1B4F8F").setFontColor("#FFFFFF");
      aba.setFrozenRows(1);
    }
    // não grava a mesma resposta duas vezes, se o aparelho reenviar
    const id = String(dados.linha[dados.linha.length - 1] || "");
    if (id && jaExiste(aba, id)) return json({ ok: true, repetida: true });

    aba.appendRow(dados.linha);
    return json({ ok: true });
  } catch (erro) {
    return json({ ok: false, erro: String(erro) });
  } finally {
    try { trava.releaseLock(); } catch (e2) {}
  }
}

/** Devolve todas as respostas para o painel de quem aplicou a pesquisa. */
function doGet(e) {
  if (!e || !e.parameter || e.parameter.chave !== CHAVE_LEITURA)
    return json({ ok: false, erro: "chave inválida" });
  const aba = abaDeRespostas();
  const valores = aba.getLastRow() ? aba.getDataRange().getDisplayValues() : [];
  return json({ ok: true, valores: valores });
}

function abaDeRespostas() {
  const p = SpreadsheetApp.getActiveSpreadsheet();
  return p.getSheetByName(ABA) || p.insertSheet(ABA);
}

function jaExiste(aba, id) {
  if (aba.getLastRow() < 2) return false;
  const col = aba.getLastColumn();
  const ids = aba.getRange(2, col, aba.getLastRow() - 1, 1).getDisplayValues();
  for (let i = 0; i < ids.length; i++) if (String(ids[i][0]) === id) return true;
  return false;
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
