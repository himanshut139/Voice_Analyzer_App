<template>
  <div class="transcription-container">
    <h1>Voice Analyzer</h1>
    <form @submit.prevent="uploadAudio">
      <label for="userId">User ID:</label>
      <input type="text" v-model="userId" required />

      <label for="audioFile">Upload Audio File:</label>
      <input type="file" @change="handleFileChange" accept="audio/*" required />

      <button type="submit" :disabled="isLoading">Transcribe</button>
    </form>

    <div v-if="isLoading" class="loading-indicator">
      <p>Transcribing... Please wait.</p>
    </div>

    <div v-if="transcribedText" class="result">
      <h2>Transcribed Text:</h2>
      <p>{{ transcribedText }}</p>
    </div>

    <div v-if="errorMessage" class="error">
      <p>Error: {{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VoiceTranscription',
  data() {
    return {
      userId: '',
      audioFile: null,
      transcribedText: '',
      errorMessage: '',
      isLoading: false // Add a loading state
    };
  },
  methods: {
    handleFileChange(event) {
      this.audioFile = event.target.files[0];
    },
    async uploadAudio() {
      if (!this.userId || !this.audioFile) {
        this.errorMessage = 'User ID and audio file are required.';
        return;
      }

      const formData = new FormData();
      formData.append('user_id', this.userId);
      formData.append('audio', this.audioFile);

      this.isLoading = true; // Set loading state to true

      try {
        const response = await fetch('https://voice-backend-2odw.onrender.com/transcribe', {
          method: 'POST',
          body: formData
        });

        const result = await response.json();
        if (response.ok) {
          this.transcribedText = result.translated_text;
          this.errorMessage = '';
        } else {
          this.transcribedText = '';
          this.errorMessage = result.message || 'An error occurred.';
        }
      } catch (error) {
        this.transcribedText = '';
        this.errorMessage = `Error: ${error.message}`; // Corrected syntax
      } finally {
        this.isLoading = false; // Set loading state to false after processing
      }
    }
  }
};
</script>

<style scoped>
.transcription-container {
  max-width: 600px;
  margin: auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
input[type="text"],
input[type="file"] {
  display: block;
  margin-bottom: 10px;
}
button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
button:hover {
  background-color: #0056b3;
}
.result, .error {
  margin-top: 20px;
}
.loading-indicator {
  font-size: 1.2em;
  color: #007bff;
}
</style>
