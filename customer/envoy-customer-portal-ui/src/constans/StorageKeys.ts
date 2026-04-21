import { IStorageConfig } from '../interface/IStorageKey';

// Keys for Cookies
export const cookie: IStorageConfig = {
  token: {
    name: 'token',
    secretName: 'RTASKXFGLSIZXZBXESDF',
    encrypted: false,
  },
  theme_mode: {
    name: 'theme_mode',
    secretName: 'OKHGKXFGDFGSXZBXVCXS',
    encrypted: false,
  },
  locale: {
    name: 'locale',
    secretName: 'OKHGKXFGDFWESDBXVCXS',
    encrypted: false,
  },
  appKey: {
    name: 'appKey',
    secretName: 'OKHGKXFGDFGSXZBXVCXS',
    encrypted: false,
  },
};

// Keys for Local Storage
export const local_storage: IStorageConfig = {
  auth_user_info: {
    name: 'auth_user_info',
    secretName: 'FSDVKXFGLESDRZBXJKLH',
    encrypted: process.env.ENCRYPTION_MODE === 'true' ? true : false,
  },
  agent_info: {
    name: 'agent_info',
    secretName: 'FSDVKXFGLESDRZBXJKLH',
    encrypted: process.env.ENCRYPTION_MODE === 'true' ? true : false,
  },
  sidebar_close: {
    name: 'sidebar_close',
    secretName: 'AWESERSTDFGSXZBXPOKI',
    encrypted: false,
  },
  sm_sidebar_close: {
    name: 'sm_sidebar_close',
    secretName: 'EDSFERSTDFGSXZBXERTG',
    encrypted: false,
  },
};
