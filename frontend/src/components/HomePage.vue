<template>
  <div class="container">
    <h1>Live Audio Transcription</h1>
    <br>
    <div>
      <label for="user-id">User Name:</label>
      <input type="text" v-model="userId" id="user-id" placeholder="Enter your Name" required />
    </div>
<br>
    <p v-if="!userId && !showUpload" class="warning-message">Please enter your User Name to proceed.</p>

    <div>
      <button @click="startRecording" :disabled="isRecording || !userId">Start Recording</button>
      <button @click="stopRecording" :disabled="!isRecording">Stop Recording</button>
    </div>
    <audio :src="audioURL" controls v-if="audioURL"></audio>
    <br>
    <button @click="uploadAudio" :disabled="!audioData || !userId">Transcribe</button>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="loading">Transcribing... Please wait.</div>

    <div v-if="transcription && !isLoading">
      <h2>Transcription:</h2>
      <p>{{ transcription }}</p>
    </div>

    <div v-if="errorMessage">
      <h2>Error:</h2>
      <p>{{ errorMessage }}</p>
    </div>

    <div v-if="similarUsers.length > 0 && !isLoading">
      <h2>Similar Users:</h2>
      <ul>
        <li v-for="user in similarUsers" :key="user.user_id">
          User ID: {{ user.user_id }}
        </li>
      </ul>
    </div>

    <br>
    <div>
      <p>Have an audio? <a href="#" @click="showUploadSection">Try this.</a></p>
    </div>

    <!-- Hidden Upload Section -->
    <div v-if="showUpload">
      <h2>Upload Audio File</h2>
      <input type="file" @change="handleFileUpload" />

      <!-- Message for entering User ID (for uploaded audio) -->
      <p v-if="!userId && showUpload" class="warning-message">Please enter your Name to proceed.</p>

      <button @click="uploadExistingAudio" :disabled="!uploadedAudio || !userId">Transcribe Audio</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isRecording: false,
      audioData: null,
      audioURL: null,
      transcription: null,
      errorMessage: null,
      userId: '',
      isLoading: false,
      mediaRecorder: null,
      similarUsers: [],
      showUpload: false,  // Toggle upload section
      uploadedAudio: null // Store uploaded audio file
    };
  },
  methods: {
    startRecording() {
      this.resetState();
      this.isRecording = true;

      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          const mimeType = 'audio/webm';

          if (MediaRecorder.isTypeSupported(mimeType)) {
            this.mediaRecorder = new MediaRecorder(stream, { mimeType });
          } else {
            console.error(`MIME type ${mimeType} not supported.`);
            return;
          }

          this.mediaRecorder.start();

          const audioChunks = [];
          this.mediaRecorder.addEventListener("dataavailable", event => {
            audioChunks.push(event.data);
          });

          this.mediaRecorder.addEventListener("stop", () => {
            const audioBlob = new Blob(audioChunks, { type: mimeType });
            this.audioData = audioBlob;
            this.audioURL = URL.createObjectURL(audioBlob);
          });
        })
        .catch(error => {
          console.error('Error accessing audio device:', error);
          this.errorMessage = 'Error accessing audio device.';
        });
    },
    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.isRecording = false;
        this.mediaRecorder.stop();
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        this.mediaRecorder = null;
      }
    },
    uploadAudio() {
      if (!this.userId) {
        this.errorMessage = 'Please enter your User ID.';
        return;
      }

      this.resetState();
      this.isLoading = true;

      const formData = new FormData();
      formData.append('user_id', this.userId);
      formData.append('audio', this.audioData, 'audio.wav');

      fetch('https://voice-backend-2odw.onrender.com/transcribe_live', {
        method: 'POST',
        body: formData,
      })
        .then(response => {
          if (!response.ok) {
            return response.json().then(data => {
              throw new Error(data.message);
            });
          }
          return response.json();
        })
        .then(data => {
          this.isLoading = false;
          if (data.status === 'success') {
            this.transcription = data.transcription;
            this.fetchSimilarUsers();
          } else {
            this.errorMessage = data.message;
          }
        })
        .catch(error => {
          this.isLoading = false;
          console.error('Error:', error);
          this.errorMessage = `Error occurred: ${error.message}`;
        });
    },
    showUploadSection() {
      this.showUpload = true;
    },
    handleFileUpload(event) {
      this.uploadedAudio = event.target.files[0];
    },
    uploadExistingAudio() {
      if (!this.userId) {
        this.errorMessage = 'Please enter your User ID.';
        return;
      }

      this.resetState();
      this.isLoading = true;

      const formData = new FormData();
      formData.append('user_id', this.userId);
      formData.append('audio', this.uploadedAudio);

      fetch('https://voice-backend-2odw.onrender.com/transcribe', {
        method: 'POST',
        body: formData,
      })
        .then(response => {
          if (!response.ok) {
            return response.json().then(data => {
              throw new Error(data.message);
            });
          }
          return response.json();
        })
        .then(data => {
          this.isLoading = false;
          if (data.status === 'success') {
            this.transcription = data.translated_text;
            this.fetchSimilarUsers();
          } else {
            this.errorMessage = data.message;
          }
        })
        .catch(error => {
          this.isLoading = false;
          console.error('Error:', error);
          this.errorMessage = `Error occurred: ${error.message}`;
        });
    },
    fetchSimilarUsers() {
      fetch(`https://voice-backend-2odw.onrender.com/compare_similarity/${this.userId}`)
        .then(response => {
          if (!response.ok) {
            return response.json().then(data => {
              throw new Error(data.message);
            });
          }
          return response.json();
        })
        .then(data => {
          this.similarUsers = data;
        })
        .catch(error => {
          console.error('Error fetching similar users:', error);
          this.errorMessage = `Error occurred while fetching similar users: ${error.message}`;
        });
    },
    resetState() {
      this.transcription = null;
      this.errorMessage = null;
      this.similarUsers = [];
      this.isLoading = false;
    }
  }
};
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}
button {
  margin: 10px;
}
.loading {
  font-weight: bold;
  color: #333;
}
.warning-message {
  color: red;
  font-weight: bold;
}
</style>
