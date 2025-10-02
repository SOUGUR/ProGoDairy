document.getElementById('chatbot-button').addEventListener('click', function() {
      const chatbotWindow = document.getElementById('chatbot-window');
      if (chatbotWindow.style.display === 'flex') {
        chatbotWindow.style.display = 'none';
      } else {
        chatbotWindow.style.display = 'flex';
      }
    });

document.getElementById('close-chatbot').addEventListener('click', function() {
      document.getElementById('chatbot-window').style.display = 'none';
    });

    
document.getElementById('chatbot-send').addEventListener('click', sendMessage);
document.getElementById('chatbot-user-input').addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });

async function sendMessage() {
  const input = document.getElementById('chatbot-user-input');
  const message = input.value.trim();
  
  if (!message) return;

  addMessage(message, 'user');
  input.value = '';

  try {
    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"  
      },
      body: JSON.stringify({
        model: "llama-3.3-70b-versatile",
        messages: [
          { role: "user", content: message }
        ],
        temperature: 0.7,
        max_tokens: 1024
      })
    });

    const data = await response.json();
    if (!response.ok || data.error) {
      console.error("API Error:", data.error?.message);
      addMessage("⚠️ " + (data.error?.message || "Request failed."), "bot");
      return;
    }
    const botReply = data.choices[0].message.content;
    addMessage(botReply, 'bot');
  } catch (error) {
    console.error("AI API Error:", error);
    addMessage("Sorry, I couldn't reach the AI. Try again later.", "bot");
  }
}

function addMessage(text, sender) {
      const messagesContainer = document.getElementById('chatbot-messages');
      const messageDiv = document.createElement('div');
      messageDiv.classList.add('message', sender + '-message');
      messageDiv.textContent = text;
      messagesContainer.appendChild(messageDiv);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
