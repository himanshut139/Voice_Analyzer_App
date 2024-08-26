<template>
  <div class="container">
    <h1>Live Audio Transcription</h1>
    <div>
      <label for="user-id">User ID:</label>
      <input type="text" v-model="userId" id="user-id" placeholder="Enter your user ID" required />
    </div>
    <div>
      <button @click="startRecording" :disabled="isRecording">Start Recording</button>
      <button @click="stopRecording" :disabled="!isRecording">Stop Recording</button>
    </div>
    <audio :src="audioURL" controls v-if="audioURL"></audio>
    <br>
    <button @click="uploadAudio" :disabled="!audioData || !userId">Transcribe Audio</button>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="loading">Transcribing... Please wait.</div>

    <div v-if="transcription">
      <h2>Transcription:</h2>
      <p>{{ transcription }}</p>
    </div>

    <div v-if="errorMessage">
      <h2>Error:</h2>
      <p>{{ errorMessage }}</p>
    </div>

    <!-- Similar Users Section -->
    <div v-if="similarUsers.length > 0">
      <h2>Similar Users:</h2>
      <ul>
        <li v-for="user in similarUsers" :key="user.user_id">
          User ID: {{ user.user_id }} - Similarity Score: {{ user.score.toFixed(2) }}
        </li>
      </ul>
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
      similarUsers: []  // New data property for similar users
    };
  },
  methods: {
    startRecording() {
      this.isRecording = true;
      this.audioData = null;
      this.transcription = null;
      this.errorMessage = null;
      this.similarUsers = [];  // Reset similar users list

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
        this.errorMessage = 'Please enter your user ID.';
        return;
      }

      const formData = new FormData();
      formData.append('user_id', this.userId);
      formData.append('audio', this.audioData, 'audio.wav');

      this.isLoading = true; // Show loading indicator

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
          this.isLoading = false; // Hide loading indicator
          if (data.status === 'success') {
            this.transcription = data.transcription;
            this.errorMessage = null;

            // Fetch similar users
            this.fetchSimilarUsers();
          } else {
            this.errorMessage = data.message;
            this.transcription = null;
          }
        })
        .catch(error => {
          this.isLoading = false; // Hide loading indicator
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
          this.similarUsers = data; // Update similar users list
        })
        .catch(error => {
          console.error('Error fetching similar users:', error);
          this.errorMessage = `Error occurred while fetching similar users: ${error.message}`;
        });
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
audio {
  margin-top: 10px;
}
input[type="text"] {
  margin: 10px;
  padding: 5px;
}
.loading {
  margin: 10px;
  color: #007bff;
  font-weight: bold;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  margin: 5px 0;
}
</style>
