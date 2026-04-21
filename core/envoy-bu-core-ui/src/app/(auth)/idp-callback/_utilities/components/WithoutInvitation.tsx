import React, { useEffect, useState } from 'react';
import { validateToken } from '../api-service';
import { useRouter } from 'next/navigation';
import { SVG } from '@/components/others/SVG';
import { setCookies } from '@/helpers/handlers/cookiesHandler';
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
          setLocalStorage(local_storage.auth_user_info, {
            value: response?.result.user,
          });
          setStatus('LOGIN_SUCCESS');
          router.push('/a/dashboard');
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
          {/* <Image src={loader.src} alt={'loading...'} width={48} height={48} /> */}
          <LoadingIcon />
          <div className="fs-22 fw-medium mt-3">Logging you in, please wait.....</div>
        </div>
      )}

      {(status === 'USER_NOT_FOUND' || status === 'DEFAULT_ERROR') && (
        <>
          <div className="d-flex flex-column justify-content-center align-items-center">
            <SVG icon="information-circle" width={45} height={45} />
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
