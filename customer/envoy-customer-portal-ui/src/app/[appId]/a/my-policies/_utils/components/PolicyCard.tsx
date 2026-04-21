import { formatDate, hexToRgba, thousandSeparator } from '@/helpers/services/commonService';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { IPolicy } from '../model';
import Image from 'next/image';
import dummyImage from '../../../../../../../public/images/empty-partner.png';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';
import S3Avatar from '@/components/others/page-related/S3Avatar';

export const PolicyCard = ({ policy, border = true, action }: { policy: IPolicy; border?: boolean; action: React.ReactNode }) => {
  const t = useTrans('label.my_policy,otr.common');

  return (
    <div className={`my-policy-card ${border ? 'border border-primary' : ''} rounded-2 p-2 mb-3`}>
      <div>
        {/* <S3Avatar imageKey="20442234/customer/profile/JjNcMKElEnpdkdDXGags9_image_1752556710505.jpeg" className="rounded-2" width={120} height={68} /> */}
        {policy.insurer_info_logo ? (
          <S3Avatar imageKey={policy.insurer_info_logo} className="rounded-2" width={120} height={68} />
        ) : (
          <Image src={dummyImage.src} className="rounded-2" width={120} height={68} alt={'Partner Logo'} />
        )}
      </div>
      <div className="d-flex flex-row flex-wrap gap-2">
        <div className="d-flex flex-row flex-wrap gap-2 justify-content-between align-items-center w-100 px-3 py-1">
          <div className="fw-medium fs-14">{policy.risk_type_name}</div>
          <div
            className={`rounded-5 fw-semibold px-2 fs-12`}
            style={{
              background: hexToRgba(policy.policy_request_status_color ? policy.policy_request_status_color : '', 0.1),
              border: `1px solid ${hexToRgba(policy.policy_request_status_color ? policy.policy_request_status_color : '', 0.4)}`,
              color: policy.policy_request_status_color ? policy.policy_request_status_color : '',
            }}
          >
            {policy.policy_request_status ? policy.policy_request_status : '-'}
          </div>
        </div>
        <div className={`d-flex flex-row flex-wrap gap-3 justify-content-start align-items-center`}>
          <DataCard icon={<Flexicon icon="calendar" variant="line" />} label={t('start_date')} value={formatDate(policy.start_date?.toString())} color={'#3e4784'} bgColor={'#EAECF5'} />
          <DataCard icon={<Flexicon icon="clock-stopwatch" variant="line" />} label={t('end_date')} value={formatDate(policy.end_date?.toString())} color={'#dc6803'} bgColor={'#feefc6'} />
          <DataCard icon={<Flexicon icon="target-04" variant="line" />} label={t('endorsements')} value={policy.endorsement_count?.toString()} color={'#079455'} bgColor={'#dbfae6'} />
          <DataCard
            icon={<Flexicon icon="wallet-04" variant="line" />}
            label={t('premium_amount')}
            value={thousandSeparator(policy.premium_amount?.toString() || '0')}
            color={'#09729A'}
            bgColor={'#Addaeb'}
          />
          <DataCard
            icon={<Flexicon icon="wallet-04" variant="line" />}
            label={t('outstanding')}
            value={thousandSeparator(policy.outstanding_amount?.toString() || '0')}
            color={'#d92d20'}
            bgColor={'#fee4e2'}
          />
        </div>
      </div>
      <div className={'d-flex flex-row flex-wrap gap-2 justify-content-center align-items-center px-2'}>
        {policy.policy_document && <FileDownloadButton s3Key={policy.policy_document} fileType="pdf" fileName="Policy" />}
        {policy.invoice_document && <FileDownloadButton s3Key={policy.invoice_document} fileType="pdf" fileName="Debit Note" />}
        <div className="d-flex flex-row flex-wrap gap-2">{action}</div>
      </div>
    </div>
  );
};

const DataCard = ({ color = '#3e4784', bgColor = '#EAECF5', icon, label, value }: { color: string; bgColor: string; icon: React.ReactNode; label: string; value: string }) => (
  <div className="d-flex flex-row gap-2 p-2 bg-white align-items-center">
    <div style={{ backgroundColor: bgColor, color: color }} className="p-2 rounded-3">
      {icon}
    </div>
    <div>
      <div className="fs-14 text-muted">{label}</div>
      <div className={`fw-medium fs-12`} style={{ color: label === 'Outstanding' ? '#d92d20' : '' }}>
        {value}
      </div>
    </div>
  </div>
);
