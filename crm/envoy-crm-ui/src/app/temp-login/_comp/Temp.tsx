'use client';

import { authUser } from '@/api-services/common';
import { cookie, local_storage } from '@/constans/StorageKeys';
import { setCookies } from '@/helpers/handlers/cookiesHandler';
import { setLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

function Temp({ path, token }: any) {
  const router = useRouter();

  useEffect(() => {
    const setCook = async () => {
      await setCookies(cookie.token, { value: token });

      const response = await authUser(token);
      if (response.is_success) {
        setLocalStorage(local_storage.auth_user_info, {
          value: response?.result,
        });
      }
      router.push(path || '');
    };

    setCook();
  }, []);

  return null;
}

export default Temp;
