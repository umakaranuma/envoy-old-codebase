import { useEffect, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { useRouter } from 'next/navigation';
import '../../../../public/styles/page-related/profile.css';
import { clearCookie } from '@/helpers/handlers/cookiesHandler';
import { clearLocalStorage, getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { cookie, local_storage } from '@/constans/StorageKeys';
import S3Avatar from './S3Avatar';

function Profile() {
  const router = useRouter();
  const [authUser, setAuthUser] = useState<any>(null);

  useEffect(() => {
    const user = getLocalStorage(local_storage.auth_user_info);
    if (user) {
      setAuthUser(user);
    }
  }, []);

  // const handleOptionClick = (onClose: any) => {
  //   onClose();
  // };

  const logout = async () => {
    await clearCookie(cookie.token);
    clearLocalStorage(local_storage.auth_user_info);

    router.push('/login');
  };

  return (
    <Dropdown
      trigger={
        <div className="pointer">
          <S3Avatar width={32} height={32} imageKey={authUser?.picture} />
        </div>
      }
    >
      {(onClose: any) => (
        <>
          <div className="px-3 py-2 border-bottom mb-1">
            <div style={{ width: '220px' }}>
              <div className="d-flex gap-2">
                <div className="text-end align-self-center">
                  <S3Avatar width={38} height={38} imageKey={authUser?.picture} />
                </div>
                <div>
                  <div className="fs-14">{authUser?.display_name}</div>
                  <div className="fs-12 text-muted">{authUser?.role?.name || '-'}</div>
                </div>
              </div>
            </div>
          </div>
          <DropdownItem
            className=""
            option="Profile"
            onClick={() => {
              router.push('/a/profile');
              onClose();
            }}
          />
          {/* <DropdownItem className="pointer-not-allowed" option="Support" onClick={() => handleOptionClick(onClose)} />
          <DropdownItem className="pointer-not-allowed" option="Change Password" onClick={() => handleOptionClick(onClose)} /> */}
          <DropdownItem option="Logout" onClick={() => logout()} />
        </>
      )}
    </Dropdown>
  );
}

// function ProfileContent() {
//   return (
//     <div className="d-flex justify-content-between align-items-center profile-container rounded-5 pointer">
//       {/* <Image className="rounded-pill image" src={avatar} alt="avatar" width={30} height={30} /> */}
//        <S3Avatar width={30} height={30} imageKey={authUser?.picture} />
//     </div>
//   );
// }

export default Profile;
