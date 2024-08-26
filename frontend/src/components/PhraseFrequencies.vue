<template>
  <div class="phrases-container">
    <h2>View Your Top 3 Phrases</h2>
    <form @submit.prevent="fetchPhrases" class="phrases-form">
      <label for="userId">Enter Your User Name:</label>
      <input type="text" v-model="userId" placeholder="Enter your user name" required />
      <button type="submit" :disabled="isLoading">View Phrases</button>
    </form>

    <div v-if="isLoading" class="loading-indicator">
      <p>Loading... Please wait.</p>
    </div>

    <div v-if="phrases.length" class="result">
      <h3>Top 3 Phrases:</h3>
      <ul>
        <li v-for="(phrase, index) in phrases" :key="index">
          "{{ phrase.phrase }}" - {{ phrase.frequency }} times
        </li>
      </ul>
    </div>

    <div v-else-if="phrasesFetched && !phrases.length" class="no-data">
      <p>No phrase data found for this user.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PhraseFrequencies',
  data() {
    return {
      userId: '',
      phrases: [],
      phrasesFetched: false,
      isLoading: false
    };
  },
  methods: {
    async fetchPhrases() {
      if (!this.userId) {
        return;
      }

      this.isLoading = true;
      this.phrasesFetched = false;

      try {
        const response = await fetch(`https://voice-backend-2odw.onrender.com/phrase-frequencies/${this.userId}`);
        if (response.ok) {
          this.phrases = await response.json();
        } else {
          this.phrases = [];
        }
        this.phrasesFetched = true;
      } catch (error) {
        console.error('Error fetching phrases:', error);
        this.phrases = [];
        this.phrasesFetched = true;
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.phrases-container {
  max-width: 600px;
  margin: auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f9f9f9;
  text-align: center;
}

.phrases-form {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.phrases-form label,
.phrases-form input,
.phrases-form button {
  width: 100%;
  max-width: 300px;
  margin: 5px 0;
}

input[type="text"] {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  width: 100%;
  max-width: 300px;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #0056b3;
}

.result, .no-data {
  margin-top: 20px;
}

.loading-indicator {
  font-size: 1.2em;
  color: #007bff;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  border-bottom: 1px solid #ddd;
  padding: 8px;
}

.no-data {
  color: #f00;
}

@media (max-width: 600px) {
  .phrases-container {
    padding: 15px;
  }

  .phrases-form label,
  .phrases-form input,
  .phrases-form button {
    max-width: 100%;
  }

  li {
    padding: 6px;
  }
}
</style>
