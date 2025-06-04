async function startRecording() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(stream);
  const audioChunks = [];

  mediaRecorder.ondataavailable = event => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('file', audioBlob, 'voice.webm');

    try {
      const res = await fetch('http://127.0.0.1:8000/voice-to-text/', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      console.log("🎤 Transcription received:", data.transcription);
      document.getElementById('result').textContent = data.transcription || data.error;

      if (data.transcription) {
        const chatForm = new FormData();
        chatForm.append('user_input', data.transcription);

        const chatRes = await fetch('http://127.0.0.1:8000/chat-response/', {
          method: 'POST',
          body: chatForm
        });

        const chatData = await chatRes.json();
        const responseText = chatData.response || chatData.error || "No response";
        console.log("🧠 Assistant response:", responseText);

        const responseEl = document.getElementById('response');
        if (responseEl) {
          responseEl.textContent = responseText;
          responseEl.scrollIntoView({ behavior: "smooth" });
        } else {
          console.warn("⚠️ #response element not found!");
        }
      } else {
        console.warn("⚠️ No transcription received.");
      }

    } catch (error) {
      console.error("❌ Error:", error);
      document.getElementById('response').textContent = "An error occurred.";
    } finally {
      stream.getTracks().forEach(track => track.stop());
    }
  };

  mediaRecorder.start();
  setTimeout(() => mediaRecorder.stop(), 5000);
}
