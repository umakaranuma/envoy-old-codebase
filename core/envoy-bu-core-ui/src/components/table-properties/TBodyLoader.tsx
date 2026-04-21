import { Skeleton } from '@apptimus-ui/ui-element';
import React from 'react';

function TBodyLoader() {
  return (
    <div className="mb-4">
      {[1, 2, 3, 4, 5, 6, 7, 8].map((n: number) => {
        return (
          <div key={n} className="row mt-4">
            <div className="col-3">
              <Skeleton height="20px" loading={false} />
            </div>
            <div className="col-3">
              <Skeleton height="20px" loading={false} />
            </div>
            <div className="col-2">
              <div className="d-flex justify-content-center">
                <Skeleton height="20px" loading={false} />
              </div>
            </div>
            <div className="col-4">
              <Skeleton height="20px" loading={false} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default TBodyLoader;
