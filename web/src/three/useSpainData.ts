// Data hooks for the 3D map: province geometry (TopoJSON, projected once) and
// seal coverage (live /geo/seal, falling back to the static snapshot if offline).
import { useQuery } from '@tanstack/react-query';
import { loadProvinceShapes, type ProvinceShape } from '../lib/geo';
import { loadSealSnapshot, sealMapFromLive, type SealMap, type Segment } from '../lib/seal';
import { useGeoSeal } from '../api/hooks';

export function useProvinceShapes() {
  return useQuery<ProvinceShape[]>({
    queryKey: ['province-shapes'],
    queryFn: loadProvinceShapes,
    staleTime: Infinity,
    gcTime: Infinity,
  });
}

// Live seal first; only fetch the static snapshot if the live API errored.
export function useSealMap(segment: Segment = 'venta'): SealMap {
  const live = useGeoSeal();
  const snapshot = useQuery<SealMap>({
    queryKey: ['seal-snapshot', segment],
    queryFn: () => loadSealSnapshot(segment),
    enabled: live.isError,
    staleTime: Infinity,
  });

  if (live.data) return sealMapFromLive(live.data, segment);
  if (snapshot.data) return snapshot.data;
  return {};
}
