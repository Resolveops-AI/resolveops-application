import axios from "axios";

const PAYMENT_BASE_URL = import.meta.env.VITE_PAYMENT_API_URL || "/api/payments";

const paymentApi = axios.create({
  baseURL: PAYMENT_BASE_URL,
  headers: {
    "Content-Type": "application/json"
  }
});

paymentApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default paymentApi;
