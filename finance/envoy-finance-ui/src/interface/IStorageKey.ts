export interface IStorageOptions {
  name: string;
  secretName?: string;
  encrypted: boolean;
}

export interface IStorageConfig {
  [key: string]: IStorageOptions;
}
