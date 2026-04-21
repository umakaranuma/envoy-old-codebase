import React from 'react';

function CustomPageHeading({ title }: { title: string }) {
  return <div className="fs-15 fw-semibold mb-3">{title}</div>;
}

export default CustomPageHeading;
