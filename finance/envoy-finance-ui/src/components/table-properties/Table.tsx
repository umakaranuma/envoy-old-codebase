import React from 'react';
import RecordController from './RecordController';
import RecordNotFound from './RecordNotFound';
import TBodyLoader from './TBodyLoader';
import { isEmptyObj } from '@/helpers/services/commonService';
import { Flexicon } from '@apptimus-ui/flexicon';

function Table({
  tableProperties,
  heading,
  isFullscreen = false,
  setIsFullscreen,
  setIsCustColumnVisible,
  recordControl = true,
  searchOption = true,
  setIsFilterVisible,
  isRowPerPageVisible = true,
  isPaginationTextVisible = true,
  isPaginationButtonVisible = true,
}: {
  tableProperties: any;
  heading?: React.ReactNode | string;
  isFullscreen?: boolean;
  setIsFullscreen?: Function;
  setIsCustColumnVisible?: Function;
  recordControl?: boolean;
  searchOption?: boolean;
  setIsFilterVisible?: Function;
  isRowPerPageVisible?: boolean;
  isPaginationTextVisible?: boolean;
  isPaginationButtonVisible?: boolean;
}) {
  const { Table, SearchInput, dataLength, setPageSize, tableInitiated } = tableProperties;

  const toggleFullscreen = () => {
    setIsFullscreen &&
      setIsFullscreen((prevIsFullscreen: boolean) => {
        setPageSize(prevIsFullscreen ? 10 : 100);
        return !prevIsFullscreen;
      });
  };

  const renderTopContent = () => {
    if (searchOption || setIsCustColumnVisible || setIsFullscreen) {
      return (
        <div className="dtc-header">
          {isFullscreen ? heading : searchOption ? <div className="datatable-search">{SearchInput}</div> : ''}
          <div className="d-flex align-items-center gap-3 text">
            {isFullscreen && searchOption && <div className="datatable-search d-none d-sm-inline">{SearchInput}</div>}
            {setIsFilterVisible && (
              <span className="position-relative d-none d-sm-inline" onClick={() => (setIsFullscreen && setIsFullscreen(false), setIsFilterVisible(true))}>
                <Flexicon icon="filter-lines" variant="line" size={18} className="pointer" />
                {tableProperties.tableState && !isEmptyObj(tableProperties.tableState.filters) && (
                  <span className="position-absolute bg-danger rounded-circle" style={{ padding: '6px', right: '-6px' }}></span>
                )}
              </span>
            )}
            {setIsCustColumnVisible && (
              <span className="d-none d-sm-inline" onClick={() => (setIsFullscreen && setIsFullscreen(false), setIsCustColumnVisible(true))}>
                <Flexicon icon="settings-03" variant="line" size={18} className="pointer" />
              </span>
            )}
            {setIsFullscreen && (
              <span onClick={toggleFullscreen} className="d-none d-sm-inline">
                <Flexicon icon={isFullscreen ? 'minimize-02' : 'maximize-02'} variant="line" size={18} className="pointer" />
              </span>
            )}
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <>
      {renderTopContent()}
      {Table}
      {tableInitiated && dataLength === 0 && <RecordNotFound />}
      {!tableInitiated && <TBodyLoader />}
      {recordControl && (
        <RecordController
          tableProperties={tableProperties}
          isRowPerPageVisible={isRowPerPageVisible}
          isPaginationTextVisible={isPaginationTextVisible}
          isPaginationButtonVisible={isPaginationButtonVisible}
        />
      )}
    </>
  );
}

export default Table;
