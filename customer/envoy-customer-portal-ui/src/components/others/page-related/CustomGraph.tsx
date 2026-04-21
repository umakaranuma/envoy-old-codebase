import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Line, ResponsiveContainer } from 'recharts';

const data = [
  { day: 1, value: 3 },
  { day: 2, value: 5 },
  { day: 3, value: 9 },
  { day: 4, value: 6 },
  { day: 5, value: 4 },
  { day: 6, value: 7 },
  { day: 7, value: 3 },
  { day: 8, value: 5 },
];

export default function CustomGraph() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="day" />
        <YAxis />
        <Tooltip />
        <Area type="monotone" dataKey="value" stroke="red" fill="red" fillOpacity={0.3} />
        <Line type="monotone" dataKey="value" stroke="red" dot={{ r: 5, fill: 'red' }} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
