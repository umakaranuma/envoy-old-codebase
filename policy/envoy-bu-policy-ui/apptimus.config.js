const apptimusConfig = {
  nexus: {
    projectKey: 'P874363272765785161187153',
    apiUrl: 'https://nexus-backend.apptimus.lk',
  },
  wordbook: {
    bookKey: 'ab837be1-051b-4c38-b028-e60c91c11e70',
    outDir: 'src/locale',
    type: 'ts', //js | ts
  },
  netlink: {
    async generateOptions() {
      const { cookie } = await import('./src/constans/StorageKeys.ts');
      const { getCookies } = await import('./src/helpers/handlers/cookiesHandler.ts');
      const token = await getCookies(cookie.token);

      return {
        headers: {
          Authorization: 'Bearer ' + token,
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
      };
    },
  },
};

export default apptimusConfig;
