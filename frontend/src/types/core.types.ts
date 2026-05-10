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
