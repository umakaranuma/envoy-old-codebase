import React, { useEffect } from 'react';
import { mapChartType } from '../../chartService';
import { IChart } from '../../model';
import ReactApexChart from 'react-apexcharts';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Skeleton } from '@apptimus-ui/ui-element';
import { useChartTableProperty } from './ChartsTableProperty';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { deleteChartOfReport } from '../../api-service';
import RecordController from '@/components/table-properties/RecordController';

function ReportChart({ reportId, tableVersion, onEdit }: { reportId: string; tableVersion: number; onEdit: (id: string) => void }) {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const { tableProperties } = useChartTableProperty(reportId);

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteChartOfReport(deleteId);
    setLoader(false);
    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      tableProperties.reload();
      callback();
      onClose();
    }
  };

  useEffect(() => {
    tableProperties.reload();
  }, [tableVersion]);

  return (
    <div className="row">
      {tableProperties.isTbodyLoading ? (
        <Skeleton height="400px" width="100%" />
      ) : (
        <>
          {tableProperties.tableData.length > 0 ? (
            <>
              {tableProperties.tableData.map((chart: IChart) => {
                const chartConfig = mapChartType(chart.type, chart.chart_data);
                console.log('chartConfig', chartConfig);

                return (
                  <div key={chart.id} className="col-12 col-md-6">
                    <div className="mb-3 bg-light rounded-1 p-2">
                      <div className="d-flex justify-content-between gap-3 align-items-center p-2">
                        <div className="panel-title">{chart.title}</div>
                        <div className="d-flex gap-2">
                          <Flexicon icon="edit-05" variant="line" size={18} className="text-primary pointer" onClick={() => onEdit(chart.id.toString())} />
                          <DeleteConfirmPop
                            trigger={<Flexicon icon="trash-03" variant="line" size={18} className="text-danger pointer" />}
                            deleteId={chart.id}
                            {...{ handleOnDelete, onClose: () => {} }}
                          />
                        </div>
                      </div>
                      <ReactApexChart
                        options={{
                          ...chartConfig.options, // use options returned from mapChartType
                          dataLabels: { enabled: true },
                        }}
                        series={chartConfig.series}
                        type={chartConfig.type}
                      />
                    </div>
                  </div>
                );
              })}
              <RecordController tableProperties={tableProperties} isRowPerPageVisible={true} isPaginationTextVisible={true} isPaginationButtonVisible={true} />
            </>
          ) : (
            <div className="text-muted text-center fs-16 fw-semibold">No records found!</div>
          )}
        </>
      )}
    </div>
  );
}

export default ReportChart;
