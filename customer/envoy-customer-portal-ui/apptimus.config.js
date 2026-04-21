const apptimusConfig = {
  nexus: {
    projectKey: 'P874363272765785161187153',
    apiUrl: 'https://nexus-backend.apptimus.lk',
  },
  wordbook: {
    bookKey: 'f5c96606-3c0c-4362-beb0-a0d3a3f80e67',
    outDir: 'src/locale',
    type: 'ts', //js | ts
  },
  netlink: {
    async generateOptions() {
      const { cookie } = await import('./src/constans/StorageKeys.ts');
      const { getCookies } = await import('./src/helpers/handlers/cookiesHandler.ts');
      const token = await getCookies(cookie.token);
      const appKey = await getCookies(cookie.appKey);

      return {
        headers: {
          Authorization: 'Bearer ' + token,
          Accept: 'application/json',
          'Content-Type': 'application/json',
          'X-App-Key': appKey,
        },
      };
    },
  },
};

export default apptimusConfig;
