import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { useTableProperty } from './MyPoliciesTableProperty';
import { useState } from 'react';
import RecordController from '@/components/table-properties/RecordController';
import { PolicyCard } from './PolicyCard';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter } from 'next/navigation';
import MakePayment from './view/settlement/MakePayment';
import UploadReceipt from './view/settlement/UploadReceipt';
import SuccessMessage from './view/settlement/SuccessMessage';
import { IPolicy } from '../model';

function MyPoliciesList() {
  const t = useTrans('label.my_policy,otr.common');
  const { tableProperties } = useTableProperty();
  const router = useRouter();
  const [paymentPolicyId, setPaymentPolicyId] = useState<string | null>(null);
  const [paidInvoice, setPaidInvoice] = useState('');
  const [openReceipt, setOpenReceipt] = useState(false);
  const params = useParams();
  const appId = params.appId as string;

  const handleNextStep = (paymentMethod: string, invoiceNumber: string) => {
    tableProperties.reload();
    if (paymentMethod === 'bank_transfer') {
      setPaidInvoice(invoiceNumber);
    } else {
      setOpenReceipt(true);
    }
  };

  return (
    <div className="bg-white rounded-2 py-3">
      <div className="d-flex flex-column gap-3">
        {tableProperties.isTbodyLoading ? (
          <Skeleton height="100px" width="100%" />
        ) : (
          <>
            {tableProperties.tableData.length > 0 ? (
              <>
                {tableProperties?.tableData?.map((policy: IPolicy, index: number) => (
                  <PolicyCard
                    key={index}
                    action={
                      <>
                        <Button text={t('view')} width="xs" size="sm" onClick={() => router.push(`/${appId}/a/my-policies/${policy.id}`)} />
                        <Button text={t('pay_now')} width="xs" size="sm" variant="outline" onClick={() => setPaymentPolicyId(policy.id.toString())} />
                      </>
                    }
                    policy={policy}
                  />
                ))}
                <RecordController tableProperties={tableProperties} isRowPerPageVisible={true} isPaginationTextVisible={true} isPaginationButtonVisible={true} />
              </>
            ) : (
              <div className="text-muted text-center fs-16 fw-semibold">No records found!</div>
            )}
          </>
        )}
      </div>
      {paymentPolicyId && (
        <MakePayment
          isOpen={!!paymentPolicyId}
          onCancel={() => {
            setPaymentPolicyId(null);
          }}
          afterSubmit={handleNextStep}
          selectedPolicyId={paymentPolicyId}
        />
      )}
      {openReceipt && <UploadReceipt isOpen={openReceipt} onCancel={() => setOpenReceipt(false)} setOpenSuccessMsg={(id: string) => setPaidInvoice(id)} />}
      {paidInvoice !== '' && <SuccessMessage isOpen={paidInvoice !== ''} onCancel={() => setPaidInvoice('')} invoiceNumber={paidInvoice} />}
    </div>
  );
}

export default MyPoliciesList;
