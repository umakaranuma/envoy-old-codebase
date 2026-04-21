import React, { useState } from 'react';
import InteractionsList from './InteractionsList';
import { InteractionsView } from './InteractionsView';

interface ComponentsProp {
  id: string;
  onClose: Function;
}
const Interaction = ({ id }: ComponentsProp) => {
  const [currentViewId, setCurrentViewId] = useState('');

  return (
    <>
      <InteractionsList tableVers={0} onView={(id: string) => setCurrentViewId(id)} viewId={id} />
      {currentViewId !== '' && <InteractionsView viewId={currentViewId} isOpen={currentViewId !== ''} onClose={() => setCurrentViewId('')} contactId={id} />}
    </>
  );
};

export default Interaction;
