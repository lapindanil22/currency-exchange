// Currencies block

async function getCurrencies() {
  const response = await fetch("/currencies", {
    method: "GET",
    headers: { "Accept": "application/json" }
  });
  if (response.ok === true) {
    const currencies = await response.json();
    const rows = document.querySelector("#currenciesTBody");
    currencies.forEach(currency => rows.append(currencyRow(currency)));
  }
}

async function addCurrency(event) {
  event.preventDefault();

  const nameInput = document.getElementById("cname");
  const codeInput = document.getElementById("ccode");
  const signInput = document.getElementById("csign");

  const response = await fetch("/currencies", {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      name: nameInput.value, 
      code: codeInput.value, 
      sign: signInput.value
    })
  });
  if (response.ok === true) {
    const currency = await response.json();
    const rows = document.querySelector("#currenciesTBody");
    rows.append(currencyRow(currency));
    nameInput.value = "",
    codeInput.value = "",
    signInput.value = ""
  }
}

// for later
// async function getCurrency(code) {
//     const response = await fetch(`/currencies/${code}`, {
//         method: "GET",
//         headers: { "Accept": "application/json" }
//     });
//     if (response.ok === true) {
//         const currency = await response.json();
//         document.getElementById("userId").value = currency.id;
//         document.getElementById("userName").value = currency.name;
//         document.getElementById("userAge").value = currency.age;
//     }
//     else {
//         const error = await response.json();
//         console.log(error.message);
//     }
// }

async function deleteCurrency(code) {
  const response = await fetch(`/currencies/${code}`, {
      method: "DELETE",
      headers: { "Accept": "application/json" }
  });
  if (response.ok === true) {
      const currency = await response.json();
      document.querySelector(`tr[data-rowid='${"currency" + currency.id}']`).remove();
  }
  else {
      const error = await response.json();
      console.log(error.message);
  }
}

// Exchange Rates block

async function getExchangeRates() {
  const response = await fetch("/exchangeRates", {
    method: "GET",
    headers: { "Accept": "application/json" }
  });
  if (response.ok === true) {
    const exchangeRates = await response.json();
    const rows = document.querySelector("#exchangeTBody");
    rows.innerHTML = "";
    exchangeRates.forEach(exchangeRate => rows.append(exchangeRateRow(exchangeRate)));
  }
}

async function addExchangeRate(event) {
  const baseCurrencyCodeInput = document.getElementById("erbccode");
  const targetCurrencyCodeInput = document.getElementById("ertccode");
  const rateInput = document.getElementById("errate");
  
  const response = await fetch("/exchangeRates", {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      baseCurrencyCode: baseCurrencyCodeInput.value, 
      targetCurrencyCode: targetCurrencyCodeInput.value, 
      rate: rateInput.value
    })
  });
  if (response.ok === true) {
    const exchangeRate = await response.json();
    const rows = document.querySelector("#exchangeTBody");
    rows.append(exchangeRateRow(exchangeRate));
    
    baseCurrencyCodeInput.value = "";
    targetCurrencyCodeInput.value = "";
    rateInput.value = "";
  }
}

async function editExchangeRate(event) {
  const baseCurrencyCodeInput = document.getElementById("erbccode");
  const targetCurrencyCodeInput = document.getElementById("ertccode");
  const rateInput = document.getElementById("errate");
  
  const response = await fetch(`/exchangeRates/${erpair.value}`, {
    method: "PATCH",
    headers: {    
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
    body: parseFloat(rateInput.value)
  });
  if (response.ok === true) {
    const exchangeRate = await response.json();
    document.querySelector(`tr[data-rowid='${"exchangeRate" + exchangeRate.id}']`).replaceWith(exchangeRateRow(exchangeRate));
    
    erpair.value = "";
    baseCurrencyCodeInput.value = "";
    targetCurrencyCodeInput.value = "";
    rateInput.value = "";
  }
}

async function deleteExchangeRate(pair) {
  const response = await fetch(`/exchangeRates/${pair}`, {
      method: "DELETE",
      headers: { "Accept": "application/json" }
  });
  if (response.ok === true) {
      const exchangeRate = await response.json();
      document.querySelector(`tr[data-rowid='${"exchangeRate" + exchangeRate.id}']`).remove();
  }
  else {
      const error = await response.json();
      console.log(error.message);
  }
}

// Exchange block

async function exchange(event) {
  event.preventDefault();
  
  const baseCode = document.getElementById("baseCode").value;
  const targetCode = document.getElementById("targetCode").value;
  const amount = document.getElementById("amount").value;
  const convertedAmountSpan = document.getElementById("convertedAmount")

  const response = await fetch(`/exchange?baseCode=${baseCode}&targetCode=${targetCode}&amount=${amount}`, {
    method: "GET",
    headers: { "Accept": "application/json" }
  });
  if (response.ok === true) {
    const exchange = await response.json();
    convertedAmountSpan.innerHTML = exchange.converted_amount;
  }
  else {
    const error = await response.json();
    console.log(error.message);
  }
}

// Helper functions

async function addOrEditExchangeRate(event) {
  event.preventDefault();

  if (document.getElementById("erpair").value === "") {
    addExchangeRate(event);
  }
  else {
    editExchangeRate(event)
  }
}

// on edit button click
async function enableEditModeExchangeRate(exchangeRate) {
  
  const erpair = document.getElementById("erpair");
  const baseCurrencyCodeInput = document.getElementById("erbccode");
  const targetCurrencyCodeInput = document.getElementById("ertccode");
  const rateInput = document.getElementById("errate");

  erpair.value = exchangeRate.base_currency.code + exchangeRate.target_currency.code;
  baseCurrencyCodeInput.value = exchangeRate.base_currency.code;
  targetCurrencyCodeInput.value = exchangeRate.target_currency.code;
  rateInput.value = exchangeRate.rate;
}

// add row in currencies table
function currencyRow(currency) {
    const tr = document.createElement("tr");
    tr.setAttribute("data-rowid", "currency" + currency.id);

    const nameTd = document.createElement("td");
    nameTd.append(currency.name);
    tr.append(nameTd);

    const codeTd = document.createElement("td");
    codeTd.innerHTML = `<a href="/currencies/${currency.code}">${currency.code}</a>`;
    tr.append(codeTd);

    const signTd = document.createElement("td");
    signTd.append(currency.sign);
    tr.append(signTd);

    const linksTd = document.createElement("td");

    const removeLink = document.createElement("button"); 
    removeLink.append("delete");
    removeLink.addEventListener("click", async () => await deleteCurrency(currency.code));

    linksTd.append(removeLink);
    tr.appendChild(linksTd);

    return tr;
}

// add row in exchange rates table
function exchangeRateRow(exchangeRate) {
  const tr = document.createElement("tr");
  tr.setAttribute("data-rowid", "exchangeRate" + exchangeRate.id);

  const pairTd = document.createElement("td");
  pairTd.innerHTML = `<a href="/exchangeRates/${exchangeRate.base_currency.code + exchangeRate.target_currency.code}">${exchangeRate.base_currency.code}/${exchangeRate.target_currency.code}</a>`;
  tr.append(pairTd);

  const rateTd = document.createElement("td");
  rateTd.append(exchangeRate.rate);
  tr.append(rateTd);

  const linksTd = document.createElement("td");

  const editLink = document.createElement("button"); 
  editLink.append("edit");
  editLink.addEventListener("click", async() => await enableEditModeExchangeRate(exchangeRate));
  linksTd.append(editLink);

  const removeLink = document.createElement("button"); 
  removeLink.append("delete");
  removeLink.addEventListener("click", async () => await deleteExchangeRate(exchangeRate.base_currency.code + exchangeRate.target_currency.code));

  linksTd.append(removeLink);
  tr.appendChild(linksTd);

  return tr;
}

// on full page load
document.addEventListener("DOMContentLoaded", function() {
    getCurrencies();
    getExchangeRates();

    document.getElementById("exchangeButton").addEventListener("click", async() => await exchange(event));
    document.getElementById("cadd").addEventListener("click", async() => await addCurrency(event));
    document.getElementById("eradd").addEventListener("click", async() => await addOrEditExchangeRate(event));
})
