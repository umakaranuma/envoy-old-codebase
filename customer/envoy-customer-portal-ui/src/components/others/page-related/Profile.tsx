import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { useParams, useRouter } from 'next/navigation';
// import avatar from '../../../../public/images/avatar.jpg';
import '../../../../public/styles/page-related/profile.css';
import { clearCookie } from '@/helpers/handlers/cookiesHandler';
import { clearLocalStorage, getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { cookie, local_storage } from '@/constans/StorageKeys';
import S3Avatar from './S3Avatar';

function Profile() {
  const router = useRouter();
  const authUser = getLocalStorage(local_storage.auth_user_info);
  const params = useParams();
  const appId = params.appId as string;

  const logout = async () => {
    await clearCookie(cookie.token);
    clearLocalStorage(local_storage.auth_user_info);
    router.push('/login');
  };

  return (
    <Dropdown trigger={<ProfileContent />}>
      {(onClose: any) => (
        <>
          <div className="px-3 py-2 border-bottom mb-1">
            <div>
              <div className="d-flex gap-2">
                <div className="text-end align-self-center">
                  <S3Avatar width={38} height={38} imageKey={authUser?.logo} />
                </div>
                <div>
                  <div className="fs-14 text-truncate">{authUser?.name}</div>
                  <div className="fs-12 text-muted text-truncate">{authUser?.email || '-'}</div>
                </div>
              </div>
            </div>
          </div>
          <DropdownItem
            option="Profile"
            onClick={() => {
              router.push(`/${appId}/a/profile`), onClose();
            }}
          />
          {/* <DropdownItem className="pointer-not-allowed" option="Support" onClick={() => handleOptionClick(onClose)} /> */}
          <DropdownItem
            option="Change Password"
            onClick={() => {
              router.push(`/${appId}/a/profile?t=password`), onClose();
            }}
          />
          <DropdownItem option="Logout" onClick={() => logout()} />
        </>
      )}
    </Dropdown>
  );
}

function ProfileContent() {
  const authUser = getLocalStorage(local_storage.auth_user_info);
  return (
    <div className="pointer">
      <S3Avatar width={38} height={38} imageKey={authUser?.logo} />
    </div>
  );
}

export default Profile;
