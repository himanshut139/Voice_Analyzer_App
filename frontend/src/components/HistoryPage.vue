<template>
  <div class="history-container">
    <h2>Your Transcription History</h2>
    <form @submit.prevent="fetchHistory" class="history-form">
      <label for="userId">Enter Your Name (Case Sensitive):</label>
      <input type="text" v-model="userId" required />
      <button type="submit">View History</button>
    </form>

    <div v-if="history.length">
      <h3>Transcription History:</h3>
      <ul class="history-list">
        <li v-for="(transcription, index) in history" :key="index" class="history-item">
          {{ transcription.timestamp }}: {{ transcription.translated_text }}
        </li>
      </ul>
    </div>
    <div v-else-if="historyFetched && !history.length">
      <p>No transcription history found for this user.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HistoryPage',
  data() {
    return {
      userId: '',
      history: [],
      historyFetched: false,
    };
  },
  methods: {
    async fetchHistory() {
      this.historyFetched = false;
      try {
        const response = await fetch(`https://voice-backend-2odw.onrender.com/history/${this.userId}`);
        if (response.ok) {
          this.history = await response.json();
        } else {
          this.history = [];
        }
        this.historyFetched = true;
      } catch (error) {
        console.error('Error fetching history:', error);
        this.history = [];
        this.historyFetched = true;
      }
    },
  },
};
</script>

<style scoped>
.history-container {
  max-width: 800px;
  margin: auto;
  padding: 20px;
  text-align: center;
}

.history-form {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.history-form label,
.history-form input,
.history-form button {
  width: 100%;
  max-width: 300px;
  margin: 5px 0;
}

ul {
  list-style: none;
  padding: 0;
}

.history-list {
  padding: 0;
  margin: 0;
}

.history-item {
  border-bottom: 1px solid #ccc;
  padding: 10px 0;
  text-align: left;
}

@media (max-width: 600px) {
  .history-container {
    padding: 15px;
  }

  .history-form label,
  .history-form input,
  .history-form button {
    max-width: 100%;
  }

  .history-item {
    font-size: 14px;
    padding: 8px 0;
  }
}
</style>
