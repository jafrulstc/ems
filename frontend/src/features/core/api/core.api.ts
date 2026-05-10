import { useApi } from '@/composables/useApi';
import type { APIResponse } from '@/types/api.types';
import type { GeoDivision, GeoDistrict, GeoUpazila, GeoPostOffice, GeoVillage } from '@/types/core.types';

export const coreApi = {
  getDivisions() {
    return useApi().get<APIResponse<GeoDivision[]>>('/core/geo/divisions');
  },
  getDistricts(divisionId?: number) {
    const query = divisionId ? `?division_id=${divisionId}` : '';
    return useApi().get<APIResponse<GeoDistrict[]>>(`/core/geo/districts${query}`);
  },
  getUpazilas(districtId?: number) {
    const query = districtId ? `?district_id=${districtId}` : '';
    return useApi().get<APIResponse<GeoUpazila[]>>(`/core/geo/upazilas${query}`);
  },
  getPostOffices(upazilaId?: number) {
    const query = upazilaId ? `?upazila_id=${upazilaId}` : '';
    return useApi().get<APIResponse<GeoPostOffice[]>>(`/core/geo/post-offices${query}`);
  },
  getVillages(postOfficeId?: number) {
    const query = postOfficeId ? `?post_office_id=${postOfficeId}` : '';
    return useApi().get<APIResponse<GeoVillage[]>>(`/core/geo/villages${query}`);
  }
};
