import { useTrans } from '@/helpers/services/lang/langService';
import { claimData } from '../service';

export const ClaimTable = () => {
  const t = useTrans('label.my_claims,otr.common');
  return (
    <div className="d-flex flex-row gap-3 claim-table-container">
      <table className="claim-table">
        <thead>
          <tr>
            <th>{t('coverage_details')}</th>
            <th>{t('estimated_amount')}</th>
            <th>{t('approved_amount')}</th>
            <th>
              {t('payable_by_insurer')}
              <span className="ms-2">80%</span>
            </th>
            <th>
              {t('payable_by_customer')}
              <span className="ms-2">20%</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {claimData.claimData.rows.map((row: any, index: number) => (
            <tr key={index}>
              <td className="text-muted" style={{ whiteSpace: 'nowrap' }}>
                {row.details}
              </td>
              <td className="text-muted">{row.estimated}</td>
              <td className="text-muted">{row.aggremed}</td>
              <td className="text-muted">{row.payableInstant}</td>
              <td className="text-muted">{row.payableCustomer}</td>
            </tr>
          ))}
          <tr className="total-row">
            <td>Total Amount</td>
            <td style={{ color: '#075573' }}>{claimData.claimData.totals.estimated}</td>
            <td style={{ color: '#079455' }}>{claimData.claimData.totals.aggremed}</td>
            <td style={{ color: '#079455' }}>{claimData.claimData.totals.payableInstant}</td>
            <td style={{ color: '#D92D20' }}>{claimData.claimData.totals.payableCustomer}</td>
          </tr>
        </tbody>
      </table>
      <div className="d-flex justify-content-center align-items-center flex-column w-100">
        <div>
          <div className="text-muted fs-18">Total Claim Amount</div>
          <div className="fs-18 fw-semibold" style={{ color: '#079455' }}>
            {' '}
            {claimData.claimData.totalClaimAmount}
          </div>
        </div>
      </div>
    </div>
  );
};
