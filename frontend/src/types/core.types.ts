export interface MenuItem {
  id: number;
  organization_id: number;
  parent_id: number | null;
  label: string;
  icon: string | null;
  route_name: string | null;
  permission_key: string | null;
  order: number;
  is_active: boolean;
  children: MenuItem[];
}

export interface GeoDivision {
  id: number;
  name: string;
}

export interface GeoDistrict {
  id: number;
  division_id: number;
  name: string;
}

export interface GeoUpazila {
  id: number;
  district_id: number;
  name: string;
}

export interface GeoPostOffice {
  id: number;
  upazila_id: number;
  name: string;
  post_code: string;
}

export interface GeoVillage {
  id: number;
  post_office_id: number;
  name: string;
}
