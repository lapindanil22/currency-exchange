async function getCurrencies() {
  const response = await fetch("/currencies", {
    method: "GET",
    headers: { "Accept": "application/json" }
  });
  if (response.ok === true) {
    const users = await response.json();
    const rows = document.querySelector("tbody");
    users.forEach(user => rows.append(row(user)));
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

// async function deleteUser(id) {
//     const response = await fetch(`/users/${id}`, {
//         method: "DELETE",
//         headers: { "Accept": "application/json" }
//     });
//     if (response.ok === true) {
//         const user = await response.json();
//         document.querySelector(`tr[data-rowid='${user.id}']`).remove();
//     }
//     else {
//         const error = await response.json();
//         console.log(error.message);
//     }
// }

// сброс данных формы после отправки
function reset() {
    
}

// создание строки для таблицы
function row(user) {

    const tr = document.createElement("tr");
    tr.setAttribute("data-rowid", user.id);

    const nameTd = document.createElement("td");
    nameTd.append(user.name);
    tr.append(nameTd);

    const codeTd = document.createElement("td");
    codeTd.append(user.code);
    tr.append(codeTd);

    const signTd = document.createElement("td");
    signTd.append(user.sign);
    tr.append(signTd);

    const linksTd = document.createElement("td");

    const editLink = document.createElement("button"); 
    editLink.append("Изменить");
    editLink.addEventListener("click", async() => await getCurrency(user.id));
    linksTd.append(editLink);

    const removeLink = document.createElement("button"); 
    removeLink.append("Удалить");
    removeLink.addEventListener("click", async () => await deleteUser(user.id));

    linksTd.append(removeLink);
    tr.appendChild(linksTd);

    return tr;
}

// загрузка пользователей
document.addEventListener("DOMContentLoaded", function() {
    getCurrencies();

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
