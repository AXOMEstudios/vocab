function init(vocs=[]) {
  function shuffle(array) {
    let currentIndex = array.length,  randomIndex;
    while (currentIndex != 0) {
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex--;
      [array[currentIndex], array[randomIndex]] = [
        array[randomIndex], array[currentIndex]];
    }
    return array;
  }
  return shuffle(vocs);
}

var vocabs = init([
  {% for i in d["vocabs"] %}
  "{{i[0]}}",
  {% endfor %}
])
var idx = 0;

function generateMessage(message, t="danger") {
  var msg = document.createElement("ARTICLE");
  msg.classList.add("message");
  msg.classList.add("is-"+t);
  var msgbody = document.createElement("DIV");
  msgbody.classList.add([
    "message-body"
  ]);
  msgbody.classList.add([
    "has-text-black"
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

function openCard(vocab) {
  let fr = document.getElementById("card-workspace-from");
  let to = document.getElementById("card-workspace-to");

  
  request_return("/learn/{{d['_id']}}/api", {
    action: "get-card",
    fr: vocab
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

function doYouKnow(y="y") {
  if (y == "y") {
    $("#was-that-correct").removeClass("is-hidden");
  } else {
    $("#type-it-correct").removeClass("is-hidden");
  }
  $("#do-you-know").addClass("is-hidden");
  $("#card-workspace-to").removeClass("is-hidden");
}

function wasThatCorrect(y="y") {
  if (y != "y") {
    $("#was-that-correct").addClass("is-hidden");
    $("#type-it-correct").removeClass("is-hidden");
  } else {
    vocabs.remove
    continueLearning();
  }
}

function submitRepeatWriting() {
  let input = document.getElementById("type-prompt-1");
  let comp = document.getElementById("card-workspace-to");
  if ($.trim(input.value) == $.trim(comp.innerHTML)) {
    input.value = "";
    continueLearning();
  } else {
    generateMessage("That's not the EXACT word.");
  }
}

function continueLearning() {
  let phrases = [
    "Perfect!",
    "You're getting better!",
    "Incredible!",
    "Awesome. Simply awesome.",
    "Never saw such great Scholar.",
    "Genius!",
    "That makes me happy.",
    "You're learning very fast!",
    "Great.",
    "Okay, let's go!",
    "Are ya winning, son?"
  ]
  generateMessage(phrases[Math.floor(Math.random()*phrases.length)], "success");
  $("#do-you-know").removeClass("is-hidden");
  $("#card-workspace-to").addClass("is-hidden");
  $("#continue-button").addClass("is-hidden");
  $("#was-that-correct").addClass("is-hidden");
  $("#type-it-correct").addClass("is-hidden");
  idx++;
  if (idx >= vocabs.length) {
    
  } else {
    openCard(vocabs[idx]);
  }
}

openCard(vocabs[idx]);