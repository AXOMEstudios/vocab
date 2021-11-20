function generateMessage(message, t="danger") {
  var msg = document.createElement("ARTICLE");
  msg.classList.add("message");
  msg.classList.add("is-"+t);
  var msgbody = document.createElement("DIV");
  msgbody.classList.add([
    "message-body"
  ]);
  msgbody.innerHTML = message;
  msg.appendChild(msgbody);
  setTimeout(() => {
    msg.remove()
  }, 3000);
  document.getElementById("errorMessageContainer").appendChild(msg);
}

function request(url='', data={}) {
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    redirect: 'follow',
    body: JSON.stringify(data)
  }).then((response) => {
    if (!response.ok) {
      response.text().then((errmsg) => {
        generateMessage(errmsg);
      });
      throw errmsg;
    }
  })
}

function request_return(url='', data={}) {
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    redirect: 'follow',
    body: JSON.stringify(data)
  })
}

function addVocabulary() {
  const fr = document.getElementById("add-word-from");
  const to = document.getElementById("add-word-to");

  request("/editor/{{d['_id']}}/api", {
    action: "add-card",
    fr: fr.value,
    to: to.value,
    token: "{{token}}"
  }).then(() => {
    var newBox = document.createElement("DIV");
    newBox.classList.add([
      "box"
    ]);
    newBox.classList.add([
      "is-clickable"
    ]);
    newBox.classList.add([
      "is-vocab"
    ]);
    newBox.value = fr.value;
    newBox.onclick = (e) => {
      openCard(e.target.value);
    };
    var newStrong = document.createElement("STRONG");
    newStrong.innerHTML = fr.value;

    var newDelete = document.createElement("BUTTON");
    newDelete.classList.add("delete");
    newDelete.classList.add("is-large");
    newDelete.value = fr.value;
    newDelete.onclick = (e) => {
      deleteCard(e.target.value, e.target.parentElement);
    }
    
    newBox.appendChild(newStrong);
    newBox.appendChild(newDelete)
    document.getElementById("cardContainer").appendChild(newBox);
    
    fr.value = ""; to.value = "";
    fr.focus();
    generateMessage("Successfully uploaded.","success");
  });
}

function openCard(vocab) {
  let fr = document.getElementById("card-workspace-from");
  let to = document.getElementById("card-workspace-to");

  
  request_return("/editor/{{d['_id']}}/api", {
    action: "get-card",
    fr: vocab,
    token: "{{token}}"
  }).then((response) => {
    if (!response.ok) {
      response.text().then((errmsg) => {
        generateMessage(errmsg);
      });
      throw errmsg;
    }
    response.text().then((text) => {
      to.innerHTML = text;
      fr.innerHTML = vocab;
    });
  });
}

function deleteCard(voc, par) {
  request("/editor/{{d['_id']}}/api", {
    action: "delete-card",
    card: voc,
    token: "{{token}}"
  }).then(() => {
    par.remove();
  });
}

function hotkey(e) {
    if (e.key == "Enter") {
        addVocabulary();
    }
}

document.addEventListener('keyup', hotkey, false);