import S3Avatar from '@/components/others/page-related/S3Avatar';
import { useTrans } from '@/helpers/services/lang/langService';
import React from 'react';
import { IInvitation } from '../model';
import { cancelInvitation, resendInvitation } from '../api-service';
import { PopConfirm } from '@apptimus-ui/ui-element';
import { toaster } from '@/helpers/services/toaster';

function InvitationListCard({ data, onReload }: { data: IInvitation; onReload: Function }) {
  const t = useTrans('label.user,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const onCancel = async (callback: Function, setLoading: Function) => {
    try {
      setLoading(true);
      const response = await cancelInvitation(data.uid);
      if (response.is_success) {
        setLoading(false);
        callback();
        onReload();
        toaster.success(tBe(response.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };

  const onResend = async (callback: Function, setLoading: Function) => {
    try {
      setLoading(true);
      const response = await resendInvitation(data.uid);
      if (response.is_success) {
        setLoading(false);
        callback();
        onReload();
        toaster.success(tBe(response.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };

  return (
    <div className="bg-light rounded-2 shadow-md border border-2">
      <div className="p-4">
        <div className="d-flex flex-row gap-2 mb-3">
          <div>
            <S3Avatar imageKey={undefined} />
          </div>
          <div className="d-flex flex-column">
            <div className="fw-medium fs-12">{data.name}</div>
            <div className="fs-12 text-dark">{data.email}</div>
          </div>
        </div>
        <div className="d-flex flex-row justify-content-between gap-4 fw-semibold text-primary">
          <PopConfirm
            trigger={<div className="pointer">{t('resend_invitation')}</div>}
            onConfirm={(callback, setLoading) => {
              onResend(callback, setLoading);
            }}
            onCancel={(callback) => {
              callback();
            }}
          />
          <PopConfirm
            trigger={<div className="pointer">{t('cancel_invitation')}</div>}
            onConfirm={(callback, setLoading) => {
              onCancel(callback, setLoading);
            }}
            onCancel={(callback) => {
              callback();
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default InvitationListCard;
