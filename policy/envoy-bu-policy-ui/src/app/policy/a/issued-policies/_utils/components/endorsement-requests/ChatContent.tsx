import Chat from '@/components/others/page-related/chat/Chat';
import React from 'react';
import { createMsg, getAllChatMsg, getSyncChatMsg } from '../../api-service';

function ChatContent({ policyId, endoresementId }: { policyId: string; endoresementId: string }) {
  return (
    <div>
      <Chat id={endoresementId} getAllChatMsg={getAllChatMsg} createMsgFn={createMsg} getSyncChatMsg={() => getSyncChatMsg(true, policyId)} />
    </div>
  );
}

export default ChatContent;
