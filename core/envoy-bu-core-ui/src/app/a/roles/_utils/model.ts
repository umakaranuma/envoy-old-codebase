export interface IRoles {
  id: number;
  name?: string;
  description?: string;
  system_role?: string;
  permission_ids?: [];
}

export const initFormData = {
  id: '',
  name: '',
  description: '',
  system_role: '',
  permission_ids: [],
};

export interface Permission {
  id: number;
  entity: string;
  action: string;
}

export interface EntityItem {
  entity: string;
  actions: Permission[];
}

export interface ModuleItem {
  module: string;
  permissions: Permission[];
}
