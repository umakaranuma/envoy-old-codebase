import React from 'react';
import CoverageList from './CoverageList';

function CoverageDetails({ viewId }: { viewId: string }) {
  return (
    <>
      <CoverageList viewId={viewId} />
    </>
  );
}

export default CoverageDetails;
