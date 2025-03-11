// Código común para chat y modal (usado en index, login, register, etc.)
let firstOpen = true;
let loginModal = document.getElementById("loginModal");

// Toggle del chat (si existe)
const chatToggle = document.getElementById("chatToggle");
const chatContainer = document.querySelector(".chat-container");

if (chatToggle && chatContainer) {
  chatToggle.addEventListener("click", () => {
    chatContainer.classList.toggle("active");

    if (firstOpen && chatContainer.classList.contains("active")) {
      setTimeout(() => {
        addMessage("Hola, soy tu asistente. ¿En qué puedo ayudarte?", "bot");
        setTimeout(() => {
          addMessage(
            "Recuerda que iniciando sesión puedes obtener una asistencia más personalizada",
            "bot"
          );
        }, 500);
      }, 300);
      firstOpen = false;
    }
  });
}

// Funcionalidad del chat
const chatForm = document.getElementById("chatForm");
if (chatForm) {
  chatForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const input = this.querySelector("input");
    const message = input.value.trim();

    if (message) {
      addMessage(message, "user");
      input.value = "";

      // Enviar el mensaje al endpoint FastAPI y mostrar la respuesta
      fetch("http://127.0.0.1:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: message }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.generated_text) {
            addMessage(data.generated_text, "bot");
          } else {
            addMessage("Lo siento, no pude obtener una respuesta.", "bot");
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          addMessage("Error al comunicarse con el servidor.", "bot");
        });
    }
  });
}

// Funciones del modal (solo se ejecutan si existe loginModal)
function toggleLogin() {
  if (loginModal) {
    loginModal.classList.toggle("active");
  }
}

if (loginModal) {
  window.onclick = function (event) {
    if (event.target == loginModal) {
      loginModal.classList.remove("active");
    }
  };
}

// Función auxiliar para agregar mensajes en el chat (usado en páginas con plantilla de mensajes)
function addMessage(text, sender) {
  const template = document.getElementById("message-template");
  const messagesContainer = document.getElementById("messages");

  if (!template || !messagesContainer) return;

  const clone = template.content.cloneNode(true);
  const messageElement = clone.querySelector(".message");
  const textPara = clone.querySelector(".text");
  const timestamp = clone.querySelector(".timestamp");

  messageElement.classList.add(sender);
  textPara.textContent = text;
  timestamp.textContent = getCurrentTime();

  messagesContainer.appendChild(clone);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function getCurrentTime() {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Mostrar el modal automáticamente al cargar la página (si existe)
window.addEventListener("DOMContentLoaded", () => {
  if (loginModal) {
    toggleLogin();
  }
});

/* ========================= */
/* Funciones específicas para Dashboard */
/* ========================= */

// Función para mostrar/ocultar el sidebar
function toggleSidebar() {
  const sidebar = document.getElementById("chatSidebar");
  if (sidebar) {
    sidebar.classList.toggle("hidden");
  }
}

// Función para enviar mensaje desde el dashboard
function sendDashboardMessage() {
  const input = document.getElementById("dashboardInput");
  const message = input.value.trim();
  if (message !== "") {
    const messagesContainer = document.getElementById("dashboardMessages");

    const messageWrapper = document.createElement("div");
    messageWrapper.classList.add("dashboard-message-wrapper", "user-message");

    const messageContent = document.createElement("div");
    messageContent.classList.add("dashboard-message-content");
    messageContent.textContent = message;

    const timestampElement = document.createElement("div");
    timestampElement.classList.add("dashboard-message-timestamp");
    timestampElement.textContent = getCurrentTime();

    const actionsDiv = document.createElement("div");
    actionsDiv.classList.add("dashboard-message-actions");
    const copyBtn = document.createElement("button");
    copyBtn.title = "Copiar";
    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
    copyBtn.onclick = function () {
      copyMessage(copyBtn);
    };
    const deleteBtn = document.createElement("button");
    deleteBtn.title = "Eliminar";
    deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
    deleteBtn.onclick = function () {
      deleteMessage(deleteBtn);
    };
    actionsDiv.appendChild(copyBtn);
    actionsDiv.appendChild(deleteBtn);

    messageWrapper.appendChild(messageContent);
    messageWrapper.appendChild(timestampElement);
    messageWrapper.appendChild(actionsDiv);

    messagesContainer.appendChild(messageWrapper);
    input.value = "";
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Guardar mensaje de usuario en el backend
    fetch('{{ url_for("store_message_route") }}', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sender: "user", message: message }),
    });

    // Enviar mensaje para generar respuesta
    fetch("http://127.0.0.1:8000/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: message }),
    })
      .then((response) => response.json())
      .then((data) => {
        const botMessageMarkdown =
          data.generated_text || "Lo siento, no pude generar una respuesta.";
        const botMessageHTML = marked.parse(botMessageMarkdown);

        const botWrapper = document.createElement("div");
        botWrapper.classList.add("dashboard-message-wrapper", "bot-message");

        const botContent = document.createElement("div");
        botContent.classList.add("dashboard-message-content", "markdown");
        botContent.innerHTML = botMessageHTML;

        const botTimestamp = document.createElement("div");
        botTimestamp.classList.add("dashboard-message-timestamp");
        botTimestamp.textContent = getCurrentTime();

        const botActions = document.createElement("div");
        botActions.classList.add("dashboard-message-actions");
        const botCopyBtn = document.createElement("button");
        botCopyBtn.title = "Copiar";
        botCopyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        botCopyBtn.onclick = function () {
          copyMessage(botCopyBtn);
        };
        const botDeleteBtn = document.createElement("button");
        botDeleteBtn.title = "Eliminar";
        botDeleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
        botDeleteBtn.onclick = function () {
          deleteMessage(botDeleteBtn);
        };
        botActions.appendChild(botCopyBtn);
        botActions.appendChild(botDeleteBtn);

        botWrapper.appendChild(botContent);
        botWrapper.appendChild(botTimestamp);
        botWrapper.appendChild(botActions);
        messagesContainer.appendChild(botWrapper);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        fetch('{{ url_for("store_message_route") }}', {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sender: "bot", message: botMessageMarkdown }),
        });
      })
      .catch((error) =>
        console.error("Error al obtener respuesta del bot:", error)
      );
  }
}

// Función para copiar mensaje (compatible con dashboard)
function copyMessage(button) {
  const wrapper = button.parentElement.parentElement;
  const messageContent = wrapper.querySelector(".dashboard-message-content");
  const textToCopy = messageContent.innerText;
  navigator.clipboard
    .writeText(textToCopy)
    .then(() => alert("Mensaje copiado"))
    .catch((err) => console.error("Error al copiar el mensaje:", err));
}

// Función para eliminar mensaje (compatible con dashboard)
function deleteMessage(button) {
  const wrapper = button.parentElement.parentElement;
  const msgId = wrapper.getAttribute("data-msg-id");
  if (msgId) {
    fetch('{{ url_for("delete_message") }}', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ msg_id: msgId }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          wrapper.remove();
        } else {
          alert("Error al eliminar el mensaje");
        }
      })
      .catch((error) => console.error("Error al eliminar el mensaje:", error));
  } else {
    wrapper.remove();
  }
}

// Funciones para el modal de solicitud de documento
function openDocumentModal() {
  document.getElementById("documentModal").style.display = "block";
}

function closeDocumentModal() {
  document.getElementById("documentModal").style.display = "none";
}

function solicitarDocumento() {
  const docType = document.getElementById("docType").value;
  const cedula = document.getElementById("cedula").value.trim();

  if (!cedula) {
    alert("Debes ingresar tu número de cédula.");
    return;
  }

  console.log("Solicitando documento:", docType, cedula);
  // Se usa el endpoint /generate_pdf, que debe existir en el backend
  fetch("/generate_pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_type: docType, cedula: cedula }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Respuesta del backend:", data);
      if (data.success) {
        alert(
          "Tu documento ha sido procesado. Haz clic en el siguiente enlace para descargarlo:\n" +
            data.url
        );
        agregarMensajeBot(
          "Tu documento está listo. Descárgalo haciendo clic en el siguiente enlace: <a href='" +
            data.url +
            "' target='_blank'>Descargar Documento</a>"
        );
        closeDocumentModal();
      } else {
        alert("Error: " + data.error);
      }
    })
    .catch((error) => console.error("Error al generar el documento:", error));
}

// Función para agregar un mensaje de bot en el dashboard
function agregarMensajeBot(htmlContent) {
  const messagesContainer = document.getElementById("dashboardMessages");

  const botWrapper = document.createElement("div");
  botWrapper.classList.add("dashboard-message-wrapper", "bot-message");

  const botContent = document.createElement("div");
  botContent.classList.add("dashboard-message-content", "markdown");
  botContent.innerHTML = htmlContent;

  const botTimestamp = document.createElement("div");
  botTimestamp.classList.add("dashboard-message-timestamp");
  botTimestamp.textContent = getCurrentTime();

  const botActions = document.createElement("div");
  botActions.classList.add("dashboard-message-actions");
  const botCopyBtn = document.createElement("button");
  botCopyBtn.title = "Copiar";
  botCopyBtn.innerHTML = '<i class="fas fa-copy"></i>';
  botCopyBtn.onclick = function () {
    copyMessage(botCopyBtn);
  };
  const botDeleteBtn = document.createElement("button");
  botDeleteBtn.title = "Eliminar";
  botDeleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
  botDeleteBtn.onclick = function () {
    deleteMessage(botDeleteBtn);
  };
  botActions.appendChild(botCopyBtn);
  botActions.appendChild(botDeleteBtn);

  botWrapper.appendChild(botContent);
  botWrapper.appendChild(botTimestamp);
  botWrapper.appendChild(botActions);
  messagesContainer.appendChild(botWrapper);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  fetch('{{ url_for("store_message_route") }}', {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sender: "bot", message: htmlContent }),
  });
}

// Agregar event listener para el input del dashboard (Enter)
document.addEventListener("DOMContentLoaded", () => {
  const messagesContainer = document.getElementById("dashboardMessages");
  if (messagesContainer) {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    // Procesar markdown en mensajes de bot ya cargados
    const markdownElements = document.querySelectorAll(
      ".dashboard-message-content.markdown"
    );
    markdownElements.forEach((el) => {
      el.innerHTML = marked.parse(el.innerText);
    });
  }
  const dashboardInput = document.getElementById("dashboardInput");
  if (dashboardInput) {
    dashboardInput.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        sendDashboardMessage();
      }
    });
  }
});
