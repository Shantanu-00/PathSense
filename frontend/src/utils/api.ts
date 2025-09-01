// lib/api.ts
import axios from "axios";
import type { Place } from "@/lib/types";

// For production - use your Render backend URL
// For development - use localhost or relative path
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL!;


// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error("[API Request Error]", error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("[API Response Error]", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Chat
export async function sendChatMessage(query: string, session_id: string | null) {
  const res = await apiClient.post(`/api/v1/chat`, { query, session_id });
  return res.data;
}

// Get places
export async function getPlaces(business_type: string, location: string, count: number, session_id: string) {
  const res = await apiClient.get(`/api/v1/get-places`, {
    params: { business_type, location, count, session_id },
  });
  return res.data;
}

// Geocode
export async function geocodeAddress(address: string) {
  const res = await apiClient.get(`/api/v1/geocode`, { params: { address } });
  return res.data;
}

// Route optimization
export async function optimizeRoute(session_id: string, algo: string, return_to_start: boolean) {
  const res = await apiClient.post(`/api/v1/route/optimize`, null, {
    params: { session_id, algo, return_to_start },
  });
  return res.data;
}

// Confirm places (update backend)
export async function confirmPlaces(session_id: string, places: Place[], start: Place | null, end: Place | null) {
  const res = await apiClient.post(
    `/api/v1/confirm-places?session_id=${encodeURIComponent(session_id)}`,
    { places, start, end }
  );
  return res.data;
}

// Set start/end points
export async function setStartEnd(session_id: string, start: Place | null, end: Place | null) {
  const res = await apiClient.post(
    `/api/v1/set-start-end?session_id=${encodeURIComponent(session_id)}`,
    { start, end }
  );
  return res.data;
}

// Reset start/end points
export async function resetStartEnd(session_id: string, reset_start: boolean, reset_end: boolean) {
  const res = await apiClient.post(
    `/api/v1/reset-start-end?session_id=${encodeURIComponent(session_id)}`,
    { reset_start, reset_end }
  );
  return res.data;
}

// Add place
export async function addPlace(session_id: string, place: Place) {
  const res = await apiClient.post(
    `/api/v1/add-place?session_id=${encodeURIComponent(session_id)}`,
    place
  );
  return res.data;
}

// Remove place
export async function removePlace(session_id: string, place_id: string) {
  const res = await apiClient.post(
    `/api/v1/remove-place?session_id=${encodeURIComponent(session_id)}`,
    { place_id }
  );
  return res.data;
}

// Find places
export async function findPlaces(session_id: string, business_type: string, location: string, count: number) {
  const res = await apiClient.get(
    `/api/v1/find-places?session_id=${encodeURIComponent(session_id)}&business_type=${encodeURIComponent(business_type)}&location=${encodeURIComponent(location)}&count=${count}`
  );
  return res.data;
}