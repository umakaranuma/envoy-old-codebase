import Quotations from '@/app/crm/a/quotations/_utils/components/Quotations';
import Received from '@/app/crm/a/quotations/_utils/components/view/received/Received';
import React from 'react';

function Quotation({
  quotationRequestId,
  leadId,
  afterCreateRequest,
  customerId,
  stageId,
}: {
  quotationRequestId: string;
  leadId: string;
  afterCreateRequest: Function;
  customerId: number | null;
  stageId: number | null;
}) {
  return (
    <div>
      {!quotationRequestId ? (
        <Quotations leadIdFromCrm={leadId} afterCreateRequest={afterCreateRequest} isHideCreate={stageId !== null && stageId < 3} />
      ) : (
        <Received quotationId={quotationRequestId} customerId={customerId} leadId={leadId} />
      )}
    </div>
  );
}

export default Quotation;
