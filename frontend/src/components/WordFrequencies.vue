<template>
  <div class="frequencies-container">
    <h1>Word Frequencies</h1>
    <form @submit.prevent="fetchWordFrequencies" class="frequencies-form">
      <label for="userId">User Name:</label>
      <input type="text" v-model="userId" placeholder="Enter your user name" required />
      <button type="submit" :disabled="isLoading">Get Frequencies</button>
    </form>

    <div v-if="isLoading" class="loading-indicator">
      <p>Loading... Please wait.</p>
    </div>

    <div v-if="wordFrequencies.length" class="result">
      <h2>Word Frequencies:</h2>
      <table>
        <thead>
          <tr>
            <th>Word</th>
            <th>Frequency</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in wordFrequencies" :key="entry.word">
            <td>{{ entry.word }}</td>
            <td>{{ entry.frequency }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="errorMessage" class="error">
      <p>Error: {{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WordFrequencies',
  data() {
    return {
      userId: '',
      wordFrequencies: [],
      errorMessage: '',
      isLoading: false,
    };
  },
  methods: {
    async fetchWordFrequencies() {
      if (!this.userId) {
        this.errorMessage = 'User ID is required.';
        return;
      }

      this.isLoading = true;

      try {
        const response = await fetch(`https://voice-backend-2odw.onrender.com/frequencies/${this.userId}`);
        const data = await response.json();
        if (response.ok) {
          this.wordFrequencies = data;
          this.errorMessage = '';
        } else {
          this.wordFrequencies = [];
          this.errorMessage = data.error || 'An error occurred.';
        }
      } catch (error) {
        this.wordFrequencies = [];
        this.errorMessage = `Error: ${error.message}`;
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style scoped>
.frequencies-container {
  max-width: 600px;
  margin: auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f9f9f9;
  text-align: center;
}

.frequencies-form {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.frequencies-form label,
.frequencies-form input,
.frequencies-form button {
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

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}

@media (max-width: 600px) {
  .frequencies-container {
    padding: 15px;
  }

  .frequencies-form label,
  .frequencies-form input,
  .frequencies-form button {
    max-width: 100%;
  }

  table {
    font-size: 14px;
  }

  th, td {
    padding: 6px;
  }
}
</style>
