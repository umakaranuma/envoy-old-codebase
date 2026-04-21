import { useParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { Area, AreaChart, CartesianGrid, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { getAllHealthOfOpportunity } from '../../../api-service';
import { IHealth } from '../../../model';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import AddHealth from './AddHealth';

const HealthHistory = ({ setTableVers }: { setTableVers: Function }) => {
  const t = useTrans('label.sales_managements,otr.common');
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';
  const [skeleton, setSkeleton] = useState(true);
  const [data, setData] = useState<IHealth[]>([]);
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [createFormKey, setCreateFormKey] = useState(0);

  useEffect(() => {
    if (opportunityId) {
      setSkeleton(true);
      fetchData();
    }
  }, [opportunityId]);

  const fetchData = async () => {
    const responseData = await getAllHealthOfOpportunity(opportunityId, 'asc', 'date');
    if (responseData?.is_success) {
      setData(responseData.result?.data);
      setSkeleton(false);
    }
  };

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setCreateFormVisible(false);
    setTableVers((prevTableVers: number) => prevTableVers + 1);
    fetchData();
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  return (
    <>
      <div className="d-flex justify-content-end">
        <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
          <Flexicon icon="plus-circle" size={18} />
          <span className="d-none d-sm-inline">{t('add_health')}</span>
        </Button>
      </div>
      <div className="mt-4 p-2">
        <ResponsiveContainer width="100%" height={300}>
          {skeleton ? (
            <Skeleton />
          ) : (
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis
                domain={[0, 10]}
                tickCount={10}
                label={{
                  value: t('health'),
                  angle: -90,
                  position: 'insideLeft',
                  dy: 25,
                  dx: 6,
                  fill: 'black',
                  fontSize: 16,
                }}
              />
              <Tooltip />
              <Area type="monotone" dataKey="health" stroke="#ff0000" fill="rgba(255, 0, 0, 0.5)" fillOpacity={0.6} />
              <Line type="monotone" dataKey="health" stroke="red" dot={{ r: 5, fill: 'red' }} />
            </AreaChart>
          )}
        </ResponsiveContainer>
      </div>
      {createFormVisible && <AddHealth key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />}
    </>
  );
};

export default HealthHistory;
