export interface Place {
  id?: string;
  name: string;
  address?: string;
  latitude: number;
  longitude: number;
  type?: string;
  role?: "start" | "end" | "regular";
}

// Add this new type for better type safety
export interface PlacesData {
  places: Place[];
  start?: Place | null;
  end?: Place | null;
}

// Optimization response from backend
export interface OptimizedRouteResponse {
  optimized_places: Place[];
  visiting_order: number[];
  steps: Array<{
    from_place: Place;
    to_place: Place;
    distance_meters: number;
    duration_seconds: number;
  }>;
  total_distance: number;
  total_time: number;
  start?: Place;
  end?: Place;
}

// Optimization response normalized for UI
export type OptimizeStats = {
  distanceKm?: number;
  durationMin?: number;
  stops?: number;
};

export type OptimizeResult = {
  orderedPlaces: Place[];
  stats?: OptimizeStats;
  start?: Place;
  end?: Place;
};