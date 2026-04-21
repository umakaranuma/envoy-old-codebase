'use client';
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button, Input } from '@apptimus-ui/ui-element';
import CreateMsg from './_utils/components/CreateMsg';
import { IMessage, initMessage } from './_utils/model';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import ViewMsg from './_utils/components/ViewMsg';
import { convertUTCTimeToLocal } from '@/helpers/services/commonService';

const Chat = ({
  id,
  getAllChatMsg,
  getSyncChatMsg,
  createMsgFn,
  handleAddQuotation,
  loading,
}: {
  id: string;
  getAllChatMsg: Function;
  getSyncChatMsg: Function;
  createMsgFn: Function;
  handleAddQuotation: (id: any) => void;
  loading: boolean;
}) => {
  const t = useTrans('label.chat,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [msgs, setMsgs] = useState<IMessage[]>([]);
  const [page, setPage] = useState(1);
  const [initialLoading, setInitialLoading] = useState(true);
  const [paginationLoading, setPaginationLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [selectedEmail, setSelectedEmail] = useState<IMessage | null>(null);
  const [conversationId, setConversationId] = useState<string>('');
  const [isCreateMsgOpen, setIsCreateMsgOpen] = useState(false);
  const [formData, setFormData] = useState(initMessage);
  const inboxRef = useRef<HTMLDivElement>(null);
  const [isFormProcessing, setIsFormProcessing] = useState<boolean>(false);
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [totalRecords, setTotalRecords] = useState(0);

  // Configuration
  const SCROLL_THRESHOLD = 150;
  const PAGE_SIZE = 10;

  const fetchAllMsg = useCallback(
    async (pageNum: number, isInitialLoad = false) => {
      isInitialLoad ? setInitialLoading(true) : setPaginationLoading(true);
      try {
        // Call getSyncChatMsg before fetching messages
        if (isInitialLoad) {
          try {
            await getSyncChatMsg(true, id);
          } catch (syncError) {
            console.error('Error syncing chat messages:', syncError);
          }
        }

        const params = {
          page: pageNum.toString(),
          limit: PAGE_SIZE.toString(),
        };

        const response = await getAllChatMsg(params, false, id);
        if (response?.is_success) {
          const result = response.result;

          if (result && result.conversation_metadata && Array.isArray(result.data)) {
            setConversationId(result.conversation_metadata.conversation_id);
            setTotalRecords(result.total_records);
            onFormChange('conversation_id', result.conversation_metadata.conversation_id);

            const filteredData = result.data.filter((msg: any) => msg.sender !== null).reverse();
            const apiEmails = filteredData.map((msg: any) => ({
              id: msg.id,
              body: msg.body,
              type: msg.type,
              sent_at: msg.sent_at,
              attachments: msg.attachments || [],
            }));

            isInitialLoad ? setInitialLoading(false) : setPaginationLoading(false);

            return {
              emails: apiEmails,
              hasMore: result.current_page < result.last_page,
              totalRecords: result.total_records,
            };
          } else {
            isInitialLoad ? setInitialLoading(false) : setPaginationLoading(false);
            return { emails: [], hasMore: false, totalRecords: 0 };
          }
        }
        return { emails: [], hasMore: false, totalRecords: 0 };
      } catch (error) {
        console.error('Error fetching messages:', error);
        return { emails: [], hasMore: false, totalRecords: 0 };
      }
    },
    [id],
  );

  const loadMoreEmails = useCallback(async () => {
    if (paginationLoading || !hasMore) return;

    const inbox = inboxRef.current;
    const prevScrollHeight = inbox?.scrollHeight || 0;
    const prevScrollTop = inbox?.scrollTop || 0;

    setPaginationLoading(true);
    try {
      const response = await fetchAllMsg(page + 1, false);

      if (response.emails.length > 0) {
        setMsgs((prev) => {
          const merged = [...response.emails, ...prev];
          const uniqueMessages = merged.reduce((acc: IMessage[], current: IMessage) => {
            if (!acc.find((item) => item.id === current.id)) {
              acc.push(current);
            }
            return acc;
          }, []);
          return uniqueMessages;
        });

        setPage((prev) => prev + 1);
        setHasMore(response.hasMore);

        // Maintain scroll position after loading older messages
        setTimeout(() => {
          if (inbox) {
            const newScrollHeight = inbox.scrollHeight;
            inbox.scrollTop = newScrollHeight - prevScrollHeight + prevScrollTop;
          }
        }, 0);
      }
    } catch (error) {
      console.error('Error loading more messages:', error);
    } finally {
      setPaginationLoading(false);
    }
  }, [page, paginationLoading, hasMore, fetchAllMsg]);

  // Initial load
  useEffect(() => {
    const loadInitialEmails = async () => {
      const response = await fetchAllMsg(1, true);
      if (response.emails.length > 0) {
        setMsgs(response.emails);
        setHasMore(response.hasMore);

        setTimeout(() => {
          if (inboxRef.current) {
            inboxRef.current.scrollTop = inboxRef.current.scrollHeight;
          }
        }, 100);
      }
    };
    loadInitialEmails();
  }, [fetchAllMsg]);

  // Scroll handler for loading more when reaching top
  useEffect(() => {
    const inbox = inboxRef.current;
    if (!inbox || initialLoading) return;

    let isFetching = false;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = inbox;
      const isNearTop = scrollTop < SCROLL_THRESHOLD;
      const isNearBottom = scrollHeight - (scrollTop + clientHeight) < 50;

      setIsAtBottom(isNearBottom);

      if (isNearTop && !paginationLoading && hasMore && !isFetching) {
        isFetching = true;
        loadMoreEmails().finally(() => {
          isFetching = false;
        });
      }
    };

    const debouncedScrollHandler = debounce(handleScroll, 200);
    inbox.addEventListener('scroll', debouncedScrollHandler);
    return () => inbox.removeEventListener('scroll', debouncedScrollHandler);
  }, [loadMoreEmails, paginationLoading, hasMore, initialLoading]);

  const debounce = (func: Function, wait: number) => {
    let timeout: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  };

  const handleEmailClick = (email: IMessage) => {
    setSelectedEmail(email);
  };

  const formatMessageDate = (date: Date): string => {
    if (isNaN(date.getTime())) return 'Invalid Date';

    const currentYear = new Date().getFullYear();
    const isCurrentYear = date.getFullYear() === currentYear;

    const options: Intl.DateTimeFormatOptions = {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
    };

    if (!isCurrentYear) {
      options.year = 'numeric';
    }

    return date.toLocaleDateString('en-US', options);
  };

  const handleAfterSave = async () => {
    setIsCreateMsgOpen(false);
    onFormChange('body', '');
    onFormChange('subject', '');

    setPage(1);
    const response = await fetchAllMsg(1, true);
    setMsgs(response.emails);
    setHasMore(response.hasMore);

    setTimeout(() => {
      if (inboxRef.current) {
        inboxRef.current.scrollTop = inboxRef.current.scrollHeight;
      }
    }, 0);

    if (isAtBottom) {
      setTimeout(() => {
        if (inboxRef.current) {
          inboxRef.current.scrollTop = inboxRef.current.scrollHeight;
        }
      }, 0);
    }
    setIsFormProcessing(false);
  };

  const handleSendMessage = (e: any) => {
    onSubmit(e);
  };

  const onFormChange = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }));
  };

  async function onSubmit(e: any) {
    e.preventDefault();
    clearError(form.approval.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createMsgFn(formData);
      if (responseData.is_success) {
        handleAfterSave();
      }
      if (responseData.status_code === 417) {
        printError(responseData.result, form.approval.store, tBe);
      }
    } catch (error) {
      console.error('An error occurred:', error);
      setIsFormProcessing(false);
    }
  }

  if (!initialLoading && msgs.length === 0)
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '200px' }}>
        {t('no_messages_found')}
      </div>
    );

  if (initialLoading)
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '200px' }}>
        <div className="text-center p-3">
          <div className="spinner-border spinner-border-sm text-primary" role="status"></div>
          <div className="ms-2 small text-muted">{t('loading_messages')}...</div>
        </div>
      </div>
    );

  return (
    <div className="container-fluid p-0 position-relative">
      <div className="card border-0 h-100">
        {!isCreateMsgOpen && !selectedEmail && (
          <>
            <div className="card-header bg-white border-bottom p-2 d-flex justify-content-between align-items-center">
              <div className="small text-muted">
                {t('total_messages')}: {totalRecords}
              </div>
              <div className="small text-muted">
                {t('page')} {page} {t('of')} {Math.ceil(totalRecords / PAGE_SIZE)}
              </div>
            </div>

            <div ref={inboxRef} className="card-body p-2" style={{ height: 'calc(100vh - 56px - 60px - 38px)', overflowY: 'auto', scrollBehavior: 'smooth' }}>
              {paginationLoading && (
                <div className="text-center p-3 bg-light bg-opacity-50">
                  <div className="spinner-border spinner-border-sm text-primary" role="status"></div>
                  <span className="ms-2 small text-muted">{t('loading_older_messages')}</span>
                </div>
              )}

              {!hasMore && msgs.length > 10 && !paginationLoading && <div className="text-center p-2 text-muted small bg-light">{t('no_more_older_messages')}</div>}

              {(() => {
                let lastDate: string | null = null;

                return msgs.map((msg) => {
                  const isReceived = msg.type !== 'sent';
                  const msgDate = new Date(msg.sent_at);
                  const currentDateStr = msgDate.toDateString();
                  const todayStr = new Date().toDateString();
                  const hasAttachments = msg.attachments && msg.attachments.length > 0;

                  const shouldShowDate = lastDate !== currentDateStr;

                  if (shouldShowDate) {
                    lastDate = currentDateStr;
                  }

                  // Decide label for date separator
                  let dateLabel = formatMessageDate(msgDate);
                  if (currentDateStr === todayStr) {
                    dateLabel = 'Today';
                  }

                  return (
                    <div key={msg.id}>
                      {shouldShowDate && (
                        <div className="chat-date-separator sticky-top">
                          <span className="chat-date-badge">{dateLabel}</span>
                        </div>
                      )}

                      <div className={`chat-message-container ${isReceived ? 'chat-message-container--received' : 'chat-message-container--sent'}`} onClick={() => handleEmailClick(msg)}>
                        <div className={`chat-message-bubble ${isReceived ? 'chat-message-bubble--received' : 'chat-message-bubble--sent'}`}>
                          <div className="chat-message-content" dangerouslySetInnerHTML={{ __html: msg.body }} />
                          <div className="d-flex align-items-center justify-content-between mt-2">
                            <div className="d-flex align-items-center gap-1">
                              {hasAttachments && (
                                <>
                                  <Flexicon icon="paperclip" variant="line" size={14} />
                                  <span className="small text-muted">
                                    {msg.attachments.length} {t('attachment')}
                                    {msg.attachments.length !== 1 ? 's' : ''}
                                  </span>
                                </>
                              )}
                            </div>
                            <div>{convertUTCTimeToLocal(msg.sent_at, 'time')}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                });
              })()}
            </div>
            {/* Input box*/}
            <div className="card-footer bg-white border-top p-3">
              <div className="d-flex align-items-center gap-2 w-100">
                <div className="flex-grow-1 d-flex align-items-center gap-2">
                  <div className="flex-grow-1">
                    <Input type="text" className="form-control rounded-pill" placeholder="Type a message..." value={formData.body} onChange={(e) => onFormChange('body', e.target.value)} />
                  </div>
                  <Button className="d-flex align-items-center justify-content-center" type="button" onClick={(e) => handleSendMessage(e)} disabled={isFormProcessing}>
                    <Flexicon icon="send-03" variant="line" size={16} />
                  </Button>
                </div>
                <Button className="d-flex align-items-center justify-content-center" onClick={() => setIsCreateMsgOpen(true)}>
                  <Flexicon icon="edit-05" variant="line" size={16} />
                </Button>
              </div>
            </div>
          </>
        )}

        {!isCreateMsgOpen && selectedEmail && <ViewMsg selectedEmail={selectedEmail} setSelectedEmail={setSelectedEmail} handleAddQuotation={handleAddQuotation} loading={loading} />}

        {isCreateMsgOpen && (
          <CreateMsg setIsCreateMsgOpen={setIsCreateMsgOpen} conversation_id={conversationId} afterSave={handleAfterSave} formData={formData} setFormData={setFormData} createMsgFn={createMsgFn} />
        )}
      </div>
    </div>
  );
};

export default Chat;
