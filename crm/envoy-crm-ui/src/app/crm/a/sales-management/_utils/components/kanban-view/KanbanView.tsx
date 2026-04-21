import React, { useEffect, useState } from 'react';
import { useKanban } from '@apptimus-ui/kanban';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Badge } from '@apptimus-ui/ui-element';
import { useTrans } from '@/helpers/services/lang/langService';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { useRouter } from 'next/navigation';
import { getAllOpportunities, getOpportunityStages, updateOpportunityCustomer, updateOpportunityStatus } from '../../api-service';
import { formatDate, hexToRgba, thousandSeparator } from '@/helpers/services/commonService';
import AccountsCreate from '@/components/others/common/accounts/AccountsCreate';

export default function KanbanView({ onAdd, kanbanColumnReloadVers, settingId }: { onAdd: Function; kanbanColumnReloadVers: number; settingId: string }) {
  const [addColumnId, setAddColumnId] = useState<any>(null);
  const t = useTrans('label.tasks,label.sales_managements,otr.common');
  const router = useRouter();
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [onDropCardCallback, setOnDropCardCallback] = useState(null as any);
  const [dropCardData, setDropCardData] = useState(null as any);
  const [populateData, setPopulateData] = useState<{ accType: string; contactNumber: string; email: string; contactId: string; contact: string; name: string }>();
  const [dropCard, setDropCard] = useState<any>(null);

  const handleCreateFormOnCancel = () => {
    const { sourceColumn, destinationColumn } = dropCard;
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
    reload({ type: 'cards', columnId: destinationColumn.id });
    reload({ type: 'columns', columnId: destinationColumn.id });
    reload({ type: 'cards', columnId: sourceColumn.id });
    reload({ type: 'columns', columnId: sourceColumn.id });
  };

  const handleAfterSave = async (customerId: any) => {
    setCreateFormVisible(false);
    const { sourceColumn, destinationColumn, droppedCard, prevCard, nextCard } = dropCard;
    const response = await updateOpportunityStatus(droppedCard.id, {
      destination_status_id: destinationColumn.id,
      next_opportunity_id: nextCard ? nextCard.id : null,
      prev_opportunity_id: prevCard ? prevCard.id : null,
      source_status_id: sourceColumn.id,
      update_opportunity_id: droppedCard.id,
    });

    if (response.is_success) {
      onDropCardCallback(response.result);
    }

    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);

    if (dropCardData) {
      const response = await updateOpportunityCustomer(dropCardData.id, { customer_id: customerId });
      if (response.is_success) {
        if (onDropCardCallback) {
          onDropCardCallback(response.result);
        }
      }
    }
  };

  async function loadColumns() {
    const response = await getOpportunityStages();

    if (response.is_success) {
      return response.result || [];
    }

    return [];
  }

  async function loadCard(stage: any, page: any) {
    const response = await getAllOpportunities({
      stage_id: stage.id,
      page: page,
      sort_by: 'sort_index',
      sort_dir: 'asc',
      fields: 'additional',
    });

    if (response.is_success) {
      return response.result.data || [];
    }

    return [];
  }

  function renderheaderActionContent(column: any) {
    if (column.type === 'WON' || column.type === 'LOSS' || column.type === 'QUALIFIED' || column.type === 'PROSPECT') {
      return <></>;
    }

    return (
      <div className="d-flex justify-content-between align-items-center action-icon" onClick={() => (onAdd(column), setAddColumnId(column.id))}>
        <Flexicon icon="plus" variant="line" size={16} />
      </div>
    );
  }

  async function onDropCard(data: any, callBack: any) {
    const { sourceColumn, destinationColumn, droppedCard, prevCard, nextCard } = data;
    console.log('droppedCard', droppedCard);

    setPopulateData({
      accType: droppedCard.type ? droppedCard?.type : null,
      contactNumber: droppedCard?.contact_number ? droppedCard?.contact_number : droppedCard?.contact?.primary_contact ? droppedCard?.contact?.primary_contact : null,
      email: droppedCard?.email ? droppedCard?.email : droppedCard?.contact_email ? droppedCard?.contact_email : null, // changed dropCard -> droppedCard
      contactId: droppedCard?.contact_id ? droppedCard?.contact_id : null,
      contact: droppedCard?.contact ? droppedCard?.contact.name : droppedCard?.title ? droppedCard?.title : null,
      name: droppedCard?.title ? droppedCard?.title : null,
    });

    if (destinationColumn && destinationColumn.id.toString() === settingId.toString() && droppedCard && droppedCard.customer_id === null) {
      setDropCard(data);
      setCreateFormVisible(true);
      setOnDropCardCallback(() => callBack);
      setDropCardData(droppedCard);
      return;
    }

    const response = await updateOpportunityStatus(droppedCard.id, {
      destination_status_id: destinationColumn.id,
      next_opportunity_id: nextCard ? nextCard.id : null,
      prev_opportunity_id: prevCard ? prevCard.id : null,
      source_status_id: sourceColumn.id,
      update_opportunity_id: droppedCard.id,
    });

    if (response.is_success) {
      callBack(response.result);
    }
  }

  const { KanbanBoard, reload } = useKanban({
    columnProps: {
      // columnHeight: '60vh',
      columnWidth: '17rem',
      accessorKeys: {
        key: 'id',
        title: 'name',
        cardCount: 'total_opportunity_count',
        bgColor: 'color',
      },
      defaultColor: 'var(--custom-white)',
      headingBorder: true,
      loadColumns: loadColumns,
      headerActionContent: ({ column }) => renderheaderActionContent(column),
    },
    cardProps: {
      loaderHeight: '5rem',
      maxLoaderCount: 8,
      accessorKeys: {
        key: 'id',
      },
      loadCard: loadCard,
      cardDesign: (props) => <CutomCard {...props} />,
      onDropCard: onDropCard,
    },
  });

  useEffect(() => {
    if (addColumnId !== null) {
      reload({ type: 'cards', columnId: addColumnId });
      setAddColumnId(null);
    }
  }, [kanbanColumnReloadVers]);

  function CutomCard({ card }: any) {
    const contactInfo = {
      name: card.customer ? card.customer.name : card.contact ? card.contact.name : card.email,
      email: card.customer ? card.customer.email : card.contact ? card.contact.email : card.contact_number,
      picture: card.customer ? card.customer.logo : '',
      phone: card.customer ? card.customer.phone : card.contact ? card.contact.phone : '',
    };

    return (
      <div className="bg-custom-light p-2 rounded-2 mb-2" onClick={() => console.log('Card clicked: ', card.title)}>
        <div className="d-flex justify-content-between align-items-center">
          <div className="d-flex justify-content-between align-items-center gap-3 w-100">
            <div className="text fw-medium fs-14">{card.title}</div>
            <div className="d-flex flex-row gap-1 align-items-center">
              <Flexicon icon="calendar" variant="line" size={15} />
              <Badge text={`${formatDate(card.created_at) || 'N/A'}`} color="light" variant="outline" className="fs-12" />
            </div>
            {/* <div
              className={`d-flex flex-row align-items-center gap-1 rounded-5 fs-10 fw-bold badge`}
              style={{ background: hexToRgba(card.stage_color, 0.1), border: `1px solid ${hexToRgba(card.stage_color, 0.4)}`, color: card.stage_color }}
            >
              <svg width="9" height="8" viewBox="0 0 9 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="4.375" cy="4" r="3" fill={card.stage_color} />
              </svg>
              {card.stage_name}
            </div> */}
          </div>
          <div>
            <Dropdown
              trigger={
                <span className="action-icon">
                  <Flexicon icon="dots-vertical" variant="line" size={17} />
                </span>
              }
            >
              {(onClose: Function) => (
                <span className="t-action">
                  <DropdownItem onClick={() => (router.push(`/crm/a/sales-management/${card.id}?f=board`), onClose())}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="eye" variant="line" size={17} />
                      <span>{t('view')}</span>
                    </span>
                  </DropdownItem>
                  {/* <DeleteConfirmPop
                    trigger={
                      <DropdownItem onClick={() => null}>
                        <span className="d-flex gap-2 w-100">
                          <Flexicon icon="trash-03" variant="line" size={17} />
                          <span>{t('delete')}</span>
                        </span>
                      </DropdownItem>
                    }
                    deleteId={card.id}
                    {...{ handleOnDelete, onClose }}
                  /> */}
                </span>
              )}
            </Dropdown>
          </div>
        </div>
        <Badge text={`#${card.code}`} color="warning" variant="light" className="fs-12 mt-2" />
        <div className="d-flex justify-content-between align-items-center gap-3 mt-3">
          <div className="d-flex flex-row align-items-center gap-2">
            {card.opportunity_types?.length > 0 && (
              <div
                className={`d-flex flex-row align-items-center gap-1 rounded-5 fs-10 fw-bold badge`}
                style={{ background: hexToRgba('#B2DDFF', 0.1), border: `1px solid ${hexToRgba('#B2DDFF', 0.4)}`, color: '#175CD3' }}
              >
                <svg width="9" height="8" viewBox="0 0 9 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="4.375" cy="4" r="3" fill={'#175CD3'} />
                </svg>
                {card.opportunity_types[0].name}
              </div>
            )}
            {card.opportunity_types?.length > 1 && (
              <div
                className={`d-flex flex-row align-items-center gap-1 rounded-5 fs-10 fw-bold badge`}
                style={{ background: hexToRgba('#B2DDFF', 0.1), border: `1px solid ${hexToRgba('#B2DDFF', 0.4)}`, color: '#175CD3' }}
              >
                +{card.opportunity_types.length - 1} more
              </div>
            )}
          </div>
          <div className="me-3 text fs-13 fw-medium">{`${card.lead_value ? card.currency_symbol : ''} ${card.lead_value ? thousandSeparator(card.lead_value) : 'N/A'}`}</div>
        </div>
        <div className="mt-3 text fs-13 fw-medium">{card.product_name ? card.product_name : card.product_group_name}</div>
        {/* <div className="text mt-2 fs-14">{card.title}</div> */}
        <div className="mt-2 d-flex flex-row align-items-center gap-2">
          <Flexicon icon="mail-01" variant="line" size={16} />
          <div>
            <div className="fs-12 text-truncate text" style={{ maxWidth: '150px' }}>
              {card.email ? card.email : contactInfo.email}
            </div>
          </div>
          {/* <ContactCard name={contactInfo.name} email={contactInfo.email} imageKey={contactInfo.picture} /> */}
        </div>
        <div className="mt-2 d-flex flex-row align-items-center gap-2">
          <Flexicon icon="phone-call-01" variant="line" size={16} />
          <div>
            <span className="fs-12">{card.contact_number ? card.contact_number : contactInfo.phone}</span>
            <br />
          </div>
          {/* <ContactCard name={contactInfo.name} email={contactInfo.email} imageKey={contactInfo.picture} /> */}
        </div>
        {/* <div className="mt-2">
          <RatingBlock value={card.health_value ?? 0} />
        </div> */}
        {/* {card.next_task && (
          <div className="mt-2">
            <div className="fs-13">{t('todo')}</div>
            <div className="d-flex flex-row gap-1 align-items-center mt-1">
              <S3Avatar imageKey={card.next_task.assigned_user_picture} width={25} height={25} />
              <div className="fs-12">{card.next_task.task}</div>
            </div>
            {card.next_task.start_date && (
              <div className="d-flex flex-row align-items-center gap-2" style={{ marginLeft: '35px' }}>
                <Flexicon icon="calendar" variant="line" size={16} />
                <div className="text fs-13">{card.next_task.start_date}</div>
              </div>
            )}
          </div>
        )}
        {card.remarks && (
          <div className="text mt-2">
            <div className="fs-13">{t('remarks')}</div>
            <div className="fs-12 ms-2">{card.remarks}</div>
          </div>
        )} */}
      </div>
    );
  }

  return (
    <>
      <div className="mt-4">
        <div>{KanbanBoard}</div>
      </div>
      {createFormVisible && (
        <AccountsCreate populateData={populateData} key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} existingSelection={true} />
      )}
    </>
  );
}
