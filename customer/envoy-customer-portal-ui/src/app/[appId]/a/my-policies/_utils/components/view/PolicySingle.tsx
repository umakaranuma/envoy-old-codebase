'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { PolicyCard } from '../PolicyCard';
import TransactionList from './TransactionList';
import { useParams, useRouter } from 'next/navigation';
import GoTo from '@/components/others/page-related/GoTo';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import MakePayment from './settlement/MakePayment';
import UploadReceipt from './settlement/UploadReceipt';
import SuccessMessage from './settlement/SuccessMessage';
import { getOnePolicy } from '../../api-service';
import { IPolicy } from '../../model';

function PolicySingle() {
  const t = useTrans('label.my_policy,otr.common');
  const [paymentPolicyId, setPaymentPolicyId] = useState<string | null>(null);
  const [paidInvoice, setPaidInvoice] = useState('');
  const [openReceipt, setOpenReceipt] = useState(false);
  const [formData, setFormData] = useState<IPolicy>({} as IPolicy);
  const [skeleton, setSkeleton] = useState(false);
  const [tableVers, setTableVers] = useState('');
  const router = useRouter();
  const params = useParams();
  const appId = params.appId as string;
  const policyId = params.policyId as string;

  useEffect(() => {
    if (policyId) {
      setSkeleton(true);
      fetchData();
    }
  }, [policyId]);

  const fetchData = async () => {
    const responseData = await getOnePolicy(policyId);
    if (responseData?.is_success) {
      setFormData(responseData.result);
      setSkeleton(false);
    }
  };

  const handleNextStep = (paymentMethod: string, invoiceNumber: string) => {
    fetchData();
    if (paymentMethod === 'bank_transfer') {
      setPaidInvoice(invoiceNumber);
    } else {
      setOpenReceipt(true);
    }
  };

  return (
    <div className="panel">
      <div className="d-flex align-items-center gap-2 mb-4">
        <GoTo goTo={() => router.push(`/${appId}/a/my-policies`)} />
        <div className="fs-15 fw-medium">{t('policy_details')}</div>
      </div>
      <div className="my-3 border border-2 border-primary rounded-2">
        {skeleton ? (
          <Skeleton height="200px" width="100%" />
        ) : (
          <div className="py-3">
            <PolicyCard
              border={false}
              action={
                <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setPaymentPolicyId(policyId)}>
                  <Flexicon icon="plus-circle" variant="line" size={16} />
                  <span className="d-none d-sm-inline">{t('add_settlement')}</span>
                </Button>
              }
              policy={formData}
            />
            <div>
              <div className="fs-15 fw-medium px-3">{t('transaction_details')}</div>
              <TransactionList policyId={policyId} tableVers={tableVers} />
            </div>
          </div>
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
      {openReceipt && (
        <UploadReceipt
          isOpen={openReceipt}
          onCancel={() => setOpenReceipt(false)}
          setOpenSuccessMsg={(id: string) => {
            setPaidInvoice(id);
          }}
        />
      )}
      {paidInvoice !== '' && (
        <SuccessMessage
          isOpen={paidInvoice !== ''}
          onCancel={() => {
            setPaidInvoice(''), setTableVers(tableVers + 1);
          }}
          invoiceNumber={paidInvoice}
        />
      )}
    </div>
  );
}

export default PolicySingle;
