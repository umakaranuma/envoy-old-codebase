import Chat from '@/components/others/page-related/chat/Chat';
import React, { useEffect } from 'react';
import { createMsg, getAllChatMsg, getSyncChatMsg } from '../api-service';
import { IFilePreviewer } from '@/components/others/page-related/chat/_utils/model';

function ChatContent({ id, handleDocExtraction, setCurrentPolicyRequestId }: { id: string; handleDocExtraction: Function; setCurrentPolicyRequestId?: Function }) {
  useEffect(() => {
    if (setCurrentPolicyRequestId) {
      setCurrentPolicyRequestId(id);
    }
  }, [id]);

  return (
    <Chat
      id={id}
      getAllChatMsg={getAllChatMsg}
      createMsgFn={createMsg}
      getSyncChatMsg={getSyncChatMsg}
      handleDocExtraction={(data: IFilePreviewer) => {
        handleDocExtraction(data);
      }}
    />
  );
}

export default ChatContent;
