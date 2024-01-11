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

async function getExchangeRates() {
  const response = await fetch("/exchangeRates", {
    method: "GET",
    headers: { "Accept": "application/json" }
  });
  if (response.ok === true) {
    const exchangeRates = await response.json();
    const rows = document.querySelector("#exchangeTBody");
    exchangeRates.forEach(exchangeRate => rows.append(exchangeRateRow(exchangeRate)));
  }
}

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

// async function createCurrency(userName, userAge) {
//     const response = await fetch("/currencies", {
//         method: "POST",
//         headers: { "Accept": "application/json", "Content-Type": "application/json" },
//         body: JSON.stringify({
//             name: userName,
//             age: parseInt(userAge, 10)
//         })
//     });
//     if (response.ok === true) {
//         const user = await response.json();
//         document.querySelector("tbody").append(row(user));
//     }
//     else {
//         const error = await response.json();
//         console.log(error.message);
//     }
// }

// async function editUser(userId, userName, userAge) {
//     const response = await fetch("api/users", {
//         method: "PUT",
//         headers: { "Accept": "application/json", "Content-Type": "application/json" },
//         body: JSON.stringify({
//             id: userId,
//             name: userName,
//             age: parseInt(userAge, 10)
//         })
//     });
//     if (response.ok === true) {
//         const user = await response.json();
//         document.querySelector(`tr[data-rowid='${user.id}']`).replaceWith(row(user));
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

// сброс данных формы после отправки
function reset() {
    
}

// создание строки для таблицы валют
function currencyRow(currency) {
    const tr = document.createElement("tr");
    tr.setAttribute("data-rowid", "currency" + currency.id);

    const nameTd = document.createElement("td");
    nameTd.append(currency.name);
    tr.append(nameTd);

    const codeTd = document.createElement("td");
    codeTd.append(currency.code);
    tr.append(codeTd);

    const signTd = document.createElement("td");
    signTd.append(currency.sign);
    tr.append(signTd);

    const linksTd = document.createElement("td");

    // const editLink = document.createElement("button"); 
    // editLink.append("Изменить");
    // editLink.addEventListener("click", async() => await getCurrency(user.id));
    // linksTd.append(editLink);

    const removeLink = document.createElement("button"); 
    removeLink.append("delete");
    removeLink.addEventListener("click", async () => await deleteCurrency(currency.code));

    linksTd.append(removeLink);
    tr.appendChild(linksTd);

    return tr;
}

// создание строки для таблицы обменных курсов
function exchangeRateRow(exchangeRate) {
  const tr = document.createElement("tr");
  tr.setAttribute("data-rowid", "exchangeRate" + exchangeRate.id);

  const nameTd = document.createElement("td");
  nameTd.append(exchangeRate.base_currency.code);
  tr.append(nameTd);

  const codeTd = document.createElement("td");
  codeTd.append(exchangeRate.target_currency.code);
  tr.append(codeTd);

  const signTd = document.createElement("td");
  signTd.append(exchangeRate.rate);
  tr.append(signTd);

  const linksTd = document.createElement("td");

  // const editLink = document.createElement("button"); 
  // editLink.append("Изменить");
  // editLink.addEventListener("click", async() => await getexchangeRate(user.id));
  // linksTd.append(editLink);

  const removeLink = document.createElement("button"); 
  removeLink.append("delete");
  removeLink.addEventListener("click", async () => await deleteExchangeRate(exchangeRate.base_currency.code + exchangeRate.target_currency.code));

  linksTd.append(removeLink);
  tr.appendChild(linksTd);

  return tr;
}

document.addEventListener("DOMContentLoaded", function() {
    getCurrencies();
    getExchangeRates();

    // // сброс значений формы
    // document.getElementById("resetBtn").addEventListener("click", () => {
    //     document.getElementById("userId").value = "";
    //     document.getElementById("userName").value = "";
    //     document.getElementById("userAge").value = "";
    // });

    // // отправка формы
    // document.getElementById("saveBtn").addEventListener("click", async () => {
    //     const id = document.getElementById("userId").value;
    //     const name = document.getElementById("userName").value;
    //     const age = document.getElementById("userAge").value;
    //     if (id === "")
    //         await createUser(name, age);
    //     else
    //         await editUser(id, name, age);
    //     reset();
    // });
})
