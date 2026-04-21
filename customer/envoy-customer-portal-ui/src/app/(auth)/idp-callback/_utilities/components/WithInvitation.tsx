import React, { useEffect, useState } from 'react';
import { validateInvitation } from '../api-service';
import { useRouter } from 'next/navigation';
import { getCookies, setCookies } from '@/helpers/handlers/cookiesHandler';
import { cookie, local_storage } from '@/constans/StorageKeys';
import { setLocalStorage } from '@/helpers/handlers/localStorageHandler';
import LoadingIcon from '@/components/others/page-related/LoadingIcon';
function WithInvitation({ token, invitation }: { token: string; invitation: string }) {
  const [loading, setLoading] = useState(true);
  const [showError, setShowError] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const checkInvitation = async () => {
      setLoading(true);
      const response = await validateInvitation(token, invitation);
      if (response.is_success) {
        await setCookies(cookie.token, {
          value: response?.result.access_token,
        });
        await setCookies(cookie.appKey, {
          value: response?.result.customer.portal_id,
        });
        setLocalStorage(local_storage.auth_user_info, {
          value: response?.result.user,
        });
        setLocalStorage(local_storage.agent_info, {
          value: response?.result.agent,
        });
        const appKey = (await getCookies(cookie.appKey)) || response?.result.customer.portal_id;
        router.push(`/${appKey}/a/home`);
      } else {
        setShowError(true);
      }
      setLoading(false);
    };
    checkInvitation();
  }, []);

  return (
    <>
      {loading && (
        <div className="d-flex flex-column justify-content-center align-items-center">
          <LoadingIcon />
          <div className="fs-22 fw-medium  mt-3">Validating your invitation, please wait...</div>
        </div>
      )}
      {showError && (
        <div className="d-flex flex-column justify-content-center align-items-center">
          {/* <SVG icon="information-circle" width={45} height={45} /> */}
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M11 15h2v2h-2zm0-8h2v6h-2zm1-5C6.47 2 2 6.5 2 12a10 10 0 0 0 10 10a10 10 0 0 0 10-10A10 10 0 0 0 12 2m0 18a8 8 0 0 1-8-8a8 8 0 0 1 8-8a8 8 0 0 1 8 8a8 8 0 0 1-8 8"
            />
          </svg>
          <div className="fs-22 fw-medium mt-3">This invitation is invalid or has expired. Please request a new invitation to proceed.</div>
        </div>
      )}
    </>
  );
}

export default WithInvitation;
