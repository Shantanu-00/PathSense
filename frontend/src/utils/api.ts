import axios from "axios";

// Use relative path for same-origin requests since frontend and backend are served from same domain
const API_BASE = ""; // Empty string for same-origin requests

export async function sendChatMessage(query: string, session_id: string | null) {
  const res = await axios.post(`${API_BASE}/api/v1/chat`, { query, session_id });
  return res.data;
}

export async function getPlaces(business_type: string, location: string, count: number, session_id: string) {
  const res = await axios.get(`${API_BASE}/api/v1/get-places`, {
    params: { business_type, location, count, session_id },
  });
  return res.data;
}

export async function geocodeAddress(address: string) {
  const res = await axios.get(`${API_BASE}/api/v1/geocode`, { params: { address } });
  return res.data;
}

export async function optimizeRoute(session_id: string, algo: string, return_to_start: boolean) {
  const res = await axios.post(`${API_BASE}/api/v1/route/optimize`, null, {
    params: { session_id, algo, return_to_start },
  });
  return res.data;
}