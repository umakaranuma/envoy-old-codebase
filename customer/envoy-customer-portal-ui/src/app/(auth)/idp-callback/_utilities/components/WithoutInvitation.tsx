import React, { useEffect, useState } from 'react';
import { validateToken } from '../api-service';
import { useRouter } from 'next/navigation';
import { getCookies, setCookies } from '@/helpers/handlers/cookiesHandler';
import { cookie, local_storage } from '@/constans/StorageKeys';
import { setLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { systemCodes } from '@/constans/Common';
import LoadingIcon from '@/components/others/page-related/LoadingIcon';

function WithoutInvitation({ token }: { token: string }) {
  const [status, setStatus] = useState<'DEFAULT_ERROR' | 'USER_NOT_FOUND' | 'LOGIN_SUCCESS' | 'PROCESSING'>('PROCESSING');
  const router = useRouter();

  useEffect(() => {
    const checkInvitation = async () => {
      try {
        setStatus('PROCESSING');
        const response = await validateToken(token);

        if (response.is_success) {
          await setCookies(cookie.token, {
            value: response?.result.access_token,
          });
          await setCookies(cookie.appKey, {
            value: response?.result.customer.portal_id,
          });
          setLocalStorage(local_storage.auth_user_info, {
            value: response?.result.customer,
          });
          setLocalStorage(local_storage.agent_info, {
            value: response?.result.agent,
          });
          setStatus('LOGIN_SUCCESS');
          const appKey = (await getCookies(cookie.appKey)) || response?.result.customer.portal_id;
          router.push(`/${appKey}/a/home`);
        } else {
          if (response.system_code === systemCodes.LOGIN_USER_NOT_FOUND) {
            setStatus('USER_NOT_FOUND');
          }
        }
      } catch (error) {
        setStatus('DEFAULT_ERROR');
      }
    };

    checkInvitation();
  }, []);

  return (
    <>
      {(status === 'PROCESSING' || status === 'LOGIN_SUCCESS') && (
        <div className="d-flex flex-column justify-content-center align-items-center">
          <LoadingIcon />
          <div className="fs-22 fw-medium mt-3">Logging you in, please wait.....</div>
        </div>
      )}

      {(status === 'USER_NOT_FOUND' || status === 'DEFAULT_ERROR') && (
        <>
          <div className="d-flex flex-column justify-content-center align-items-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M11 15h2v2h-2zm0-8h2v6h-2zm1-5C6.47 2 2 6.5 2 12a10 10 0 0 0 10 10a10 10 0 0 0 10-10A10 10 0 0 0 12 2m0 18a8 8 0 0 1-8-8a8 8 0 0 1 8-8a8 8 0 0 1 8 8a8 8 0 0 1-8 8"
              />
            </svg>
            <div className="fs-22 fw-medium mt-3">
              {status === 'USER_NOT_FOUND' ? 'You have no permission to access this application.' : 'An error occurred while processing your request. Please try again later.'}
            </div>
          </div>
        </>
      )}
    </>
  );
}

export default WithoutInvitation;
