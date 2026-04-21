import { Flexicon } from '@apptimus-ui/flexicon';
import { SVG } from '../others/SVG';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button } from '@apptimus-ui/ui-element';

function RecordController({ tableProperties, isRowPerPageVisible, isPaginationTextVisible, isPaginationButtonVisible }: any) {
  const t = useTrans('otr.common');
  const { itemsPerPage, dataLength, currentPage, setActivePage, setPageSize } = tableProperties;

  if (dataLength === 0) {
    return null;
  }

  const totalPages = Math.ceil(dataLength / itemsPerPage);

  const goToPage = (page: number) => {
    setActivePage(page);
  };

  return (
    <div className="d-flex justify-content-end align-items-center gap-5 my-4 text" style={{ textWrap: 'nowrap' }}>
      {isRowPerPageVisible && (
        <div className="d-none d-sm-flex align-items-center gap-2">
          <span>{t('rows_per_page')}</span>
          <div className="position-relative pss">
            <span className="d-flex align-items-center pointer fk-pg-size-selector">
              {itemsPerPage}
              <SVG icon="triangle" width={24} height={24} className="svg-muted" />
            </span>
            <select className="pg-size-selector" value={itemsPerPage} onChange={(e) => setPageSize(e.target.value)}>
              {[10, 25, 50, 100].map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}
      {isPaginationTextVisible && (
        <span className="no-select d-none d-sm-flex">
          {(currentPage - 1) * itemsPerPage + 1}-{Math.min(currentPage * itemsPerPage, dataLength)} of {dataLength}
        </span>
      )}
      {isPaginationButtonVisible && (
        <div className="d-flex align-items-center gap-3">
          {/* <span className={`pg-nav ${currentPage === 1 ? 'text-muted pointer-not-allowed' : 'text clickable-text'}`} {...(currentPage !== 1 && { onClick: () => goToPage(currentPage - 1) })}>
          <Flexicon icon="chevron-left" variant="line" size={18} />
        </span>
        <span
          className={`pg-nav ${currentPage === totalPages ? 'text-muted pointer-not-allowed' : 'text clickable-text'}`}
          {...(currentPage !== totalPages && { onClick: () => goToPage(currentPage + 1) })}
        >
          <Flexicon icon="chevron-right" variant="line" size={18} />
        </span> */}
          <Button
            color="light"
            variant="outline"
            className={`d-flex align-items-center gap-1 ${currentPage === 1 ? 'text-muted pointer-not-allowed' : 'text'}`}
            {...(currentPage !== 1 && { onClick: () => goToPage(currentPage - 1) })}
            disabled={currentPage === 1}
          >
            <Flexicon icon="arrow-narrow-left" variant="line" size={15} />
            <span>{t('previous')}</span>
          </Button>
          <Button
            color="light"
            variant="outline"
            className={`d-flex align-items-center gap-1 ${currentPage === totalPages ? 'text-muted pointer-not-allowed' : 'text'}`}
            {...(currentPage !== totalPages && { onClick: () => goToPage(currentPage + 1) })}
            disabled={currentPage === totalPages}
          >
            <span>{t('next')}</span>
            <Flexicon icon="arrow-narrow-right" variant="line" size={15} />
          </Button>
        </div>
      )}
    </div>
  );
}

export default RecordController;
