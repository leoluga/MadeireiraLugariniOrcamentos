let products = [];
let itensOrcamento = []; // array de objetos { produto, comprimento, largura, espessura, quantidade, volume, precoTotal }

document.addEventListener('DOMContentLoaded', () => {
  fetch('products.json')
    .then(response => response.json())
    .then(data => {
      products = data;
      populateProductSelect(products);
    });

  document.getElementById('addItemBtn').addEventListener('click', addItemAoOrcamento);
  document.getElementById('descontoValor').addEventListener('input', recalcularTotais);
  document.getElementById('printBtn').addEventListener('click', () => window.print());
});

function populateProductSelect(products) {
  const select = document.getElementById('produtoSelect');
  select.innerHTML = '';
  products.forEach(prod => {
    const option = document.createElement('option');
    option.value = prod.id;
    option.textContent = `${prod.nome} - R$ ${prod.preco_m3.toFixed(2)}/m³`;
    select.appendChild(option);
  });
}

function addItemAoOrcamento() {
  const produtoId = parseInt(document.getElementById('produtoSelect').value);
  const produto = products.find(p => p.id === produtoId);

  const comprimento = parseFloat(document.getElementById('comprimento').value) || 0;
  const largura = parseFloat(document.getElementById('largura').value) || 0;
  const espessura = parseFloat(document.getElementById('espessura').value) || 0;
  const quantidade = parseFloat(document.getElementById('quantity').value) || 0;

  const volume = comprimento * largura * espessura * quantidade;
  const precoTotal = produto.preco_m3 * volume;

  const item = {
    produto: produto,
    comprimento,
    largura,
    espessura,
    quantidade,
    volume,
    precoTotal
  };

  itensOrcamento.push(item);
  renderItens();
  recalcularTotais();
}

function renderItens() {
  const tbody = document.getElementById('itensBody');
  tbody.innerHTML = '';

  itensOrcamento.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${item.produto.nome}</td>
      <td>${item.comprimento.toFixed(2)} x ${item.largura.toFixed(2)} x ${item.espessura.toFixed(2)}</td>
      <td>${item.quantidade}</td>
      <td>${item.volume.toFixed(3)}</td>
      <td>${item.produto.preco_m3.toFixed(2)}</td>
      <td>${item.precoTotal.toFixed(2)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function recalcularTotais() {
  const totalBruto = itensOrcamento.reduce((acc, item) => acc + item.precoTotal, 0);
  const desconto = parseFloat(document.getElementById('descontoValor').value) || 0;
  const totalComDesconto = Math.max(totalBruto - desconto, 0);

  document.getElementById('totalBruto').textContent = totalBruto.toFixed(2);
  document.getElementById('totalComDesconto').textContent = totalComDesconto.toFixed(2);
}
