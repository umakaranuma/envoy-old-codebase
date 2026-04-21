import React from 'react';
import { useKanban } from '@apptimus-ui/kanban';
import { useTrans } from '@/helpers/services/lang/langService';
import DateCard from './DateCard';
import { useRouter } from 'next/navigation';
import { getAllAssigneeTasks, getAllTaskStatuses, updateTaskStatus } from '../../../api-service';
import { Badge } from '@apptimus-ui/ui-element';
import { hexToRgba } from '@/helpers/services/commonService';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import ContactCard from './ContactCard';

export default function KanbanCard({ selectedAssignee }: { selectedAssignee: string }) {
  const t = useTrans('label.tasks,otr.common');
  const router = useRouter();

  const loadColumns = async (assignee: string) => {
    const response = await getAllTaskStatuses(assignee);

    if (response.is_success) {
      return response.result || [];
    }
    return [];
  };

  async function loadCard(status: any, page: string, selectedAssignee: string) {
    const response = await getAllAssigneeTasks(status.id, selectedAssignee, page, 'sort_index', 'asc', 'additional');

    if (response.is_success) {
      return response.result.data || [];
    }

    return [];
  }

  // function renderheaderActionContent(column: any) {
  //   return (
  //     <div className="d-flex justify-content-between align-items-center action-icon">
  //       <Flexicon icon="plus" variant="line" size={16} onClick={() => console.log('add: ' + JSON.stringify(column))} />
  //     </div>
  //   );
  // }

  async function onDropCard(data: any, callBack: any) {
    const { sourceColumn, destinationColumn, droppedCard, prevCard, nextCard } = data;

    const response = await updateTaskStatus(droppedCard.id, {
      destination_status_id: destinationColumn.id,
      next_task_id: nextCard ? nextCard.id : null,
      prev_task_id: prevCard ? prevCard.id : null,
      source_status_id: sourceColumn.id,
      update_task_id: droppedCard.id,
    });

    if (response.is_success) {
      callBack(response.result);
    }
  }

  const { KanbanBoard } = useKanban({
    columnProps: {
      // columnHeight: '60vh',
      columnWidth: '17.5vw',
      accessorKeys: {
        key: 'id',
        title: 'name',
        cardCount: 'total_task_count',
        bgColor: 'color',
      },
      defaultColor: 'var(--custom-white)',
      headingBorder: true,
      loadColumns: () => loadColumns(selectedAssignee),
      // headerActionContent: ({ column }) => renderheaderActionContent(column),
    },
    cardProps: {
      loaderHeight: '100px',
      maxLoaderCount: 5,
      accessorKeys: {
        key: 'id',
      },
      loadCard: (column: any, page: any) => loadCard(column, page, selectedAssignee),
      cardDesign: (props) => <CutomCard {...props} />,
      onDropCard: onDropCard,
    },
  });

  // const handleOnDelete = () => {};

  function CutomCard({ card }: any) {
    return (
      <div className="bg-custom-light p-2 rounded-2 mb-2" onClick={() => console.log('Card clicked: ', card.title)}>
        <div className="d-flex justify-content-between align-items-center">
          <div className="d-flex justify-content-between align-items-center gap-4">
            <Badge text={`Task #${card.code}`} color="warning" variant="light" />
            {card.opportunity && (
              <div
                className={`d-flex flex-row align-items-center gap-1 rounded-5 fs-10 fw-bold badge`}
                style={{ background: hexToRgba(card?.opportunity?.stage_color, 0.1), border: `1px solid ${hexToRgba(card?.opportunity?.stage_color, 0.4)}`, color: card?.opportunity?.stage_color }}
              >
                <svg width="9" height="8" viewBox="0 0 9 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="4.375" cy="4" r="3" fill={card?.opportunity?.stage_color} />
                </svg>
                {card?.opportunity?.stage_name}
              </div>
            )}
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
                  <DropdownItem onClick={() => (router.push(`/crm/a/tasks/${card.id}`), onClose())}>
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
        <div className="mt-2">
          <div className="text">{card.task}</div>
          {card.assigned_to_id && (
            <div className="mt-1">
              <ContactCard name={card.assigned_user_name} imageKey={card.assigned_user_picture} />
            </div>
          )}
        </div>
        <div className="d-flex flex-row align-items-center gap-3">
          <DateCard dateType={t('assigned_date')} date={card.assigned_date} />
          <DateCard dateType={t('due_date')} date={card.start_date} />
        </div>
      </div>
    );
  }

  return <>{KanbanBoard}</>;
}
