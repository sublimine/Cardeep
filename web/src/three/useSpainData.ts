// Data hooks for the 3D map: province geometry (TopoJSON, projected once) and
// seal coverage (live /geo/seal, falling back to the static snapshot if offline).
import { useQuery } from '@tanstack/react-query';
import { loadProvinceShapes, type ProvinceShape } from '../lib/geo';
import { sealMapFromLive, type SealMap, type Segment } from '../lib/seal';
import { useGeoSeal } from '../api/hooks';

export function useProvinceShapes() {
  return useQuery<ProvinceShape[]>({
    queryKey: ['province-shapes'],
    queryFn: loadProvinceShapes,
    staleTime: Infinity,
    gcTime: Infinity,
  });
}

// LIVE seal only. There is deliberately NO static-snapshot fallback: the committed snapshot drifted
// from the live seal (6 province verdicts flipped -> the map painted WRONG coverage colours when the
// API was down). On a live miss we return {} so the map/coverage render their honest empty/loading
// state instead of stale fabricated verdicts (same principle as the Landing FALLBACK removal).
export function useSealMap(segment: Segment = 'venta'): SealMap {
  const live = useGeoSeal();
  if (live.data) return sealMapFromLive(live.data, segment);
  return {};
}
