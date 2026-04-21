import React, { useState } from 'react';
import { AccountsView } from './AccountsView';
import AccountsList from './AccountsList';

interface ComponentsProp {
  id: string;
  onClose: Function;
}
const Accounts = ({ id }: ComponentsProp) => {
  const [currentViewId, setCurrentViewId] = useState('');

  return (
    <>
      <AccountsList tableVers={0} onView={(id: string) => setCurrentViewId(id)} viewId={id} />
      {currentViewId !== '' && <AccountsView viewId={currentViewId} isOpen={currentViewId !== ''} onClose={() => setCurrentViewId('')} />}
    </>
  );
};

export default Accounts;
