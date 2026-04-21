import React, { useEffect, useState } from 'react';
import { validateInvitation } from '../api-service';
import { useRouter } from 'next/navigation';
import { SVG } from '@/components/others/SVG';
import { setCookies } from '@/helpers/handlers/cookiesHandler';
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
        setLocalStorage(local_storage.auth_user_info, {
          value: response?.result.user,
        });
        router.push('/a/dashboard');
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
          {/* <Image src={loader.src} alt={'loading...'} width={48} height={48} /> */}
          <LoadingIcon />
          <div className="fs-22 fw-medium  mt-3">Validating your invitation, please wait...</div>
        </div>
      )}
      {showError && (
        <div className="d-flex flex-column justify-content-center align-items-center">
          <SVG icon="information-circle" width={45} height={45} />
          <div className="fs-22 fw-medium mt-3">This invitation is invalid or has expired. Please request a new invitation to proceed.</div>
        </div>
      )}
    </>
  );
}

export default WithInvitation;
