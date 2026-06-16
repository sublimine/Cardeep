// TanStack Query hooks over the CARDEEP API client.
import { useQuery } from '@tanstack/react-query';
import { api } from './client';

export const useStats = () => useQuery({ queryKey: ['stats'], queryFn: api.stats });

export const useGeoSeal = () => useQuery({ queryKey: ['geo-seal'], queryFn: api.geoSeal });

export const useProvinceEntities = (province: string | undefined, page = 1, size = 50) =>
  useQuery({
    queryKey: ['prov-entities', province, page, size],
    queryFn: () => api.provinceEntities(province!, page, size),
    enabled: !!province,
  });

export const useEntity = (cdp: string | undefined) =>
  useQuery({ queryKey: ['entity', cdp], queryFn: () => api.entity(cdp!), enabled: !!cdp });

export const useEntityInventory = (cdp: string | undefined, page = 1, size = 50) =>
  useQuery({
    queryKey: ['entity-inv', cdp, page, size],
    queryFn: () => api.entityInventory(cdp!, page, size),
    enabled: !!cdp,
  });

export const useEntityDelta = (cdp: string | undefined, page = 1, size = 50) =>
  useQuery({
    queryKey: ['entity-delta', cdp, page, size],
    queryFn: () => api.entityDelta(cdp!, page, size),
    enabled: !!cdp,
  });

export const useVehicle = (ulid: string | undefined) =>
  useQuery({ queryKey: ['vehicle', ulid], queryFn: () => api.vehicle(ulid!), enabled: !!ulid });
