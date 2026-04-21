import { Flexicon } from '@apptimus-ui/flexicon';
import { Select } from '@apptimus-ui/select';
import React from 'react';

function ReportHeadingSection({
  chartFullScreen,
  setChartFullScreen,
  setChartType,
  setChartComKey,
  setChartDefaultValue,
  chartDefaultValue,
  title,
}: {
  chartFullScreen: boolean;
  setChartFullScreen: Function;
  setChartType: Function;
  setChartComKey: Function;
  setChartDefaultValue: Function;
  chartDefaultValue: { id: string; label: string };
  title: string;
}) {
  return (
    <div>
      <div className={`d-flex justify-content-between align-items-center mb-3 ${chartFullScreen ? 'bg-primary text-white px-3' : ''}`}>
        <div className={`chart-title ${chartFullScreen && 'text-white'}`}>{title}</div>
        <span onClick={() => setChartFullScreen((pre: boolean) => !pre)} className="me-2 pointer">
          <Flexicon icon={chartFullScreen ? 'minimize-02' : 'maximize-02'} variant="line" size={18} className="pointer" />
        </span>
      </div>
      <div className={`general-ledger-grgraph d-flex justify-content-end mb-3 ${chartFullScreen ? ' me-4' : ''}`}>
        <Select
          defaultValue={chartDefaultValue}
          onChange={(value, data) => {
            setChartType(value as 'pie' | 'bar' | 'line' | 'area');
            setChartComKey((prev: number) => prev + 1);
            setChartDefaultValue({ id: data.id, label: data.label });
          }}
          options={[
            { id: 'pie', label: 'Pie Chart' },
            { id: 'bar', label: 'Bar Chart' },
            { id: 'line', label: 'Line Chart' },
            { id: 'area', label: 'Area Chart' },
          ]}
          option={{
            label: 'label',
            value: 'id',
          }}
          className="chart-type-selector"
        />
      </div>
    </div>
  );
}

export default ReportHeadingSection;
