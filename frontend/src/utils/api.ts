import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'dev-key', // adiciona se o backend exigir
  },
});

export default api;

