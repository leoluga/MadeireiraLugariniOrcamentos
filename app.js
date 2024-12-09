let selectedProduct = null;
let products = [];

document.addEventListener('DOMContentLoaded', () => {
  fetch('products.json')
    .then(response => response.json())
    .then(data => {
      products = data;
      renderProducts(products);
    });

  const inputs = [document.getElementById('comprimento'),
                  document.getElementById('largura'),
                  document.getElementById('espessura'),
                  document.getElementById('quantity')];

  inputs.forEach(input => input.addEventListener('input', updateTotal));

  document.getElementById('printBtn').addEventListener('click', () => window.print());
});

function renderProducts(products) {
  const container = document.getElementById('products');
  container.innerHTML = '';

  products.forEach(product => {
    const div = document.createElement('div');
    div.innerHTML = `
      <strong>${product.nome}</strong><br>
      Preço por m³: R$ ${product.preco_m3.toFixed(2)}<br>
      <button onclick="selectProduct(${product.id})">Selecionar</button>
    `;
    container.appendChild(div);
  });
}

function selectProduct(id) {
  selectedProduct = products.find(p => p.id === id);
  document.getElementById('selected-product').textContent = 
    `Produto Selecionado: ${selectedProduct.nome} (R$ ${selectedProduct.preco_m3.toFixed(2)}/m³)`;
  updateTotal();
}

function updateTotal() {
  const totalPriceEl = document.getElementById('totalPrice');
  if (selectedProduct) {
    const comprimento = parseFloat(document.getElementById('comprimento').value) || 0;
    const largura = parseFloat(document.getElementById('largura').value) || 0;
    const espessura = parseFloat(document.getElementById('espessura').value) || 0;
    const quantidade = parseFloat(document.getElementById('quantity').value) || 0;

    const volume = comprimento * largura * espessura * quantidade;
    const total = selectedProduct.preco_m3 * volume;
    totalPriceEl.textContent = total.toFixed(2);
  } else {
    totalPriceEl.textContent = '0.00';
  }
}
