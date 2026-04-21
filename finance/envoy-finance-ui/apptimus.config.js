const apptimusConfig = {
  nexus: {
    projectKey: 'P874363272765785161187153',
    apiUrl: 'https://nexus-backend.apptimus.lk',
  },
  wordbook: {
    bookKey: 'c2d73658-9414-470f-9aa2-896234501583',
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
