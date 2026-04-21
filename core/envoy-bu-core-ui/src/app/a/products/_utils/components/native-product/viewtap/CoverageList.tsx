import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchProductCoverageTableData } from '../../../services';
import { Badge } from '@apptimus-ui/ui-element';
import { useCurrency } from '@/contexts/CurrencyContext';
import { thousandSeparator } from '@/helpers/services/commonService';

function CoverageList({ viewId }: { viewId: string }) {
  const t = useTrans('label.products,otr.common');
  const { currency } = useCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        header: t('coverage_name'),
        accessorKey: 'name',
        sort: true,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'coverage_amount',
        header: `${t('coverage_limit')} (${currency.code})`,
        accessorKey: 'coverage_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'excess_amount',
        header: `${t('excess')} (${currency.code})`,
        accessorKey: 'excess_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'limitation',
        header: `${t('limitations')} (${currency.code})`,
        accessorKey: 'limitation',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'is_mandatory',
        header: t('is_mandatory'),
        accessorKey: 'is_mandatory',
        sort: true,
        cell: ({ cell }: any) => {
          const value = cell.getValue();
          if (value === 0) return <Badge text={t('optional')} color="warning" variant="light" />;
          if (value === 1) return <Badge text={t('yes')} color="success" variant="light" />;
          return <div>{value}</div>;
        },
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (params: any) => fetchProductCoverageTableData(params, viewId),
    paginate: true,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [viewId]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-3'}`}>
        <Table heading={<PageHeading title={t('team_details')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, searchOption: false, enableTopContent: false }} />
      </div>
    </>
  );
}

export default CoverageList;
