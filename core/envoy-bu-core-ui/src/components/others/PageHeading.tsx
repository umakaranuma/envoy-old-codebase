import React from 'react';
import { SVG, TIcon } from './SVG';

function PageHeading({ title, icon, subTitle }: { title: string; icon?: TIcon; subTitle?: any }) {
  return (
    <div className="d-flex align-items-center gap-3">
      {icon && <SVG icon={icon} className="text-primary d-none" />}
      <h1 className="page-title">
        {title} {subTitle}
      </h1>
    </div>
  );
}

export default PageHeading;
