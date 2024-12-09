let orcamentos = [];
let products = [];

// Variáveis para criar novo orçamento
let itensNovoOrcamento = [];

// Referências ao DOM
const listaSection = document.getElementById('lista-section');
const adicionarSection = document.getElementById('adicionar-section');
const detalheSection = document.getElementById('detalhe-section');
const adicionarItemSection = document.getElementById('adicionar-item-section');

document.addEventListener('DOMContentLoaded', () => {
  carregarOrcamentos();
  carregarProdutos().then(() => {
    renderizarLista();
    popularSelectProdutos();
  });

  // Botões da lista
  document.getElementById('btnAdicionarOrcamento').addEventListener('click', () => {
    mostrarSecao('adicionar-section');
  });

  // Botões da seção de adicionar orçamento
  document.getElementById('btnCancelarOrcamento').addEventListener('click', () => {
    limparFormularioOrcamento();
    mostrarSecao('lista-section');
  });

  document.getElementById('btnSalvarOrcamento').addEventListener('click', salvarOrcamento);

  // Botão adicionar item no novo orçamento
  document.getElementById('btnAdicionarItem').addEventListener('click', () => {
    mostrarItemSection(true);
  });

  // Botões da seção adicionar item
  document.getElementById('btnFecharItem').addEventListener('click', () => {
    mostrarItemSection(false);
  });
  document.getElementById('btnAdicionarItemAoOrcamento').addEventListener('click', adicionarItemAoOrcamento);

  // Campo desconto no novo orçamento
  document.getElementById('descontoOrcamento').addEventListener('input', recalcularTotaisNovoOrcamento);

  // Detalhes do orçamento
  document.getElementById('btnAtualizarStatus').addEventListener('click', atualizarStatusOrcamento);
  document.getElementById('btnVoltarLista').addEventListener('click', () => {
    mostrarSecao('lista-section');
  });

});

function carregarOrcamentos() {
  const dados = localStorage.getItem('orcamentos');
  if (dados) {
    orcamentos = JSON.parse(dados);
  } else {
    orcamentos = [];
  }
}

function salvarOrcamentos() {
  localStorage.setItem('orcamentos', JSON.stringify(orcamentos));
}

async function carregarProdutos() {
  const response = await fetch('products.json');
  products = await response.json();
}

function renderizarLista() {
  const tbody = document.getElementById('orcamentosBody');
  tbody.innerHTML = '';
  orcamentos.forEach(orc => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${orc.id}</td>
      <td>${orc.nome}</td>
      <td>${orc.status}</td>
    `;
    tr.addEventListener('click', () => {
      mostrarDetalhes(orc.id);
    });
    tbody.appendChild(tr);
  });
}

function mostrarSecao(secaoId) {
  const secoes = ['lista-section', 'adicionar-section', 'detalhe-section'];
  secoes.forEach(s => {
    document.getElementById(s).style.display = s === secaoId ? 'block' : 'none';
  });
  if (secaoId === 'lista-section') {
    adicionarItemSection.style.display = 'none'; // garantir que feche a seção de item se aberta
  }
}

function limparFormularioOrcamento() {
  document.getElementById('novoNomeOrcamento').value = '';
  document.getElementById('novoStatusOrcamento').value = 'Em aprovação';
  document.getElementById('descontoOrcamento').value = '0';
  itensNovoOrcamento = [];
  renderizarItensNovoOrcamento();
  recalcularTotaisNovoOrcamento();
}

function salvarOrcamento() {
  const nome = document.getElementById('novoNomeOrcamento').value.trim();
  const status = document.getElementById('novoStatusOrcamento').value;
  const desconto = parseFloat(document.getElementById('descontoOrcamento').value) || 0;

  if (!nome) {
    alert('Digite um nome para o orçamento.');
    return;
  }

  if (itensNovoOrcamento.length === 0) {
    alert('Adicione ao menos um item ao orçamento.');
    return;
  }

  const novoId = orcamentos.length > 0 ? Math.max(...orcamentos.map(o => o.id)) + 1 : 1;
  const totalBruto = itensNovoOrcamento.reduce((acc, i) => acc + i.precoTotal, 0);
  const totalComDesconto = Math.max(totalBruto - desconto, 0);

  const novoOrc = {
    id: novoId,
    nome,
    status,
    desconto,
    itens: itensNovoOrcamento,
    totalBruto,
    totalComDesconto
  };

  orcamentos.push(novoOrc);
  salvarOrcamentos();
  renderizarLista();
  limparFormularioOrcamento();
  mostrarSecao('lista-section');
}

function mostrarItemSection(show) {
  adicionarItemSection.style.display = show ? 'block' : 'none';
}

function popularSelectProdutos() {
  const select = document.getElementById('produtoSelect');
  select.innerHTML = '';
  products.forEach(p => {
    const option = document.createElement('option');
    option.value = p.id;
    option.textContent = `${p.nome} - R$${p.preco_m3.toFixed(2)}/m³`;
    select.appendChild(option);
  });
}

function adicionarItemAoOrcamento() {
  const produtoId = parseInt(document.getElementById('produtoSelect').value);
  const produto = products.find(p => p.id === produtoId);

  const comprimento = parseFloat(document.getElementById('comprimentoItem').value) || 0;
  const largura = parseFloat(document.getElementById('larguraItem').value) || 0;
  const espessura = parseFloat(document.getElementById('espessuraItem').value) || 0;
  const quantidade = parseFloat(document.getElementById('quantidadeItem').value) || 0;

  if (quantidade <= 0 || comprimento <= 0 || largura <= 0 || espessura <= 0) {
    alert('Informe valores válidos para dimensões e quantidade.');
    return;
  }

  const volume = comprimento * largura * espessura * quantidade;
  const precoTotal = produto.preco_m3 * volume;

  const item = {
    produtoId,
    produtoNome: produto.nome,
    preco_m3: produto.preco_m3,
    comprimento,
    largura,
    espessura,
    quantidade,
    volume,
    precoTotal
  };

  itensNovoOrcamento.push(item);
  renderizarItensNovoOrcamento();
  recalcularTotaisNovoOrcamento();
  mostrarItemSection(false);

  // Resetar campos do item
  document.getElementById('comprimentoItem').value = '1';
  document.getElementById('larguraItem').value = '1';
  document.getElementById('espessuraItem').value = '1';
  document.getElementById('quantidadeItem').value = '1';
}

function renderizarItensNovoOrcamento() {
  const tbody = document.getElementById('itensNovoOrcamentoBody');
  tbody.innerHTML = '';

  itensNovoOrcamento.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${item.produtoNome}</td>
      <td>${item.comprimento.toFixed(2)} x ${item.largura.toFixed(2)} x ${item.espessura.toFixed(2)}</td>
      <td>${item.quantidade}</td>
      <td>${item.volume.toFixed(3)}</td>
      <td>${item.preco_m3.toFixed(2)}</td>
      <td>${item.precoTotal.toFixed(2)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function recalcularTotaisNovoOrcamento() {
  const totalBruto = itensNovoOrcamento.reduce((acc, i) => acc + i.precoTotal, 0);
  const desconto = parseFloat(document.getElementById('descontoOrcamento').value) || 0;
  const totalComDesconto = Math.max(totalBruto - desconto, 0);

  document.getElementById('totalBrutoOrcamento').textContent = totalBruto.toFixed(2);
  document.getElementById('totalComDescontoOrcamento').textContent = totalComDesconto.toFixed(2);
}

function mostrarDetalhes(id) {
  const orc = orcamentos.find(o => o.id === id);
  if (!orc) return;

  document.getElementById('detalheId').textContent = orc.id;
  document.getElementById('detalheNome').textContent = orc.nome;
  document.getElementById('detalheStatus').value = orc.status;
  document.getElementById('detalheDesconto').textContent = orc.desconto.toFixed(2);
  document.getElementById('detalheTotalBruto').textContent = orc.totalBruto.toFixed(2);
  document.getElementById('detalheTotalComDesconto').textContent = orc.totalComDesconto.toFixed(2);

  const tbody = document.getElementById('detalhesItensBody');
  tbody.innerHTML = '';
  orc.itens.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${item.produtoNome}</td>
      <td>${item.comprimento.toFixed(2)} x ${item.largura.toFixed(2)} x ${item.espessura.toFixed(2)}</td>
      <td>${item.quantidade}</td>
      <td>${item.volume.toFixed(3)}</td>
      <td>${item.preco_m3.toFixed(2)}</td>
      <td>${item.precoTotal.toFixed(2)}</td>
    `;
    tbody.appendChild(tr);
  });

  mostrarSecao('detalhe-section');
}

function atualizarStatusOrcamento() {
  const id = parseInt(document.getElementById('detalheId').textContent);
  const novoStatus = document.getElementById('detalheStatus').value;

  const idx = orcamentos.findIndex(o => o.id === id);
  if (idx >= 0) {
    orcamentos[idx].status = novoStatus;
    salvarOrcamentos();
    renderizarLista();
  }

  mostrarSecao('lista-section');
}
