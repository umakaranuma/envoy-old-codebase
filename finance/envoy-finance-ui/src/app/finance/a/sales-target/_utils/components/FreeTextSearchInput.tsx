import React, { useState, useRef, useEffect } from 'react';
import { Input, Button } from '@apptimus-ui/ui-element';

const FreeTextSearchInput = ({ onChange }: { onChange?: (keywords: string[]) => void }) => {
  const [search, setSearch] = useState('');
  const [history, setHistory] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  // Call onChange whenever history changes
  useEffect(() => {
    if (onChange) {
      onChange(history);
    }
  }, [history, onChange]);

  // Save on blur or Enter
  const saveSearch = () => {
    const trimmed = search.trim();
    if (trimmed && !history.includes(trimmed)) {
      setHistory((prev) => [...prev, trimmed]);
      setSearch('');
    }
  };

  const removeTag = (idx: number) => {
    setHistory((prev) => prev.filter((_, i) => i !== idx));
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  return (
    <div className="d-flex gap-2 align-items-center mb-2">
      {/* Input row */}
      <div tabIndex={0} onBlur={saveSearch} className="d-flex align-items-center gap-2 form-control" style={{ maxWidth: 250 }}>
        <Input className="flex-grow-1 border-0 ms-1" ref={inputRef} value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Type Keywords" />
        <Button text={'Add'} onClick={saveSearch} disabled={!search.trim()} size="sm" className="px-3 py-1" />
      </div>
      {/* {history.length > 0 && <div className="mb-1 fw-semibold fs-13">Keywords:</div>} */}
      {history.length > 0 && (
        <div className="d-flex flex-wrap gap-2 mb-2">
          {history.map((item, index) => (
            <span key={index} className="badge bg-primary-subtle text-primary px-3 py-2 rounded-pill d-flex align-items-center gap-1 fs-13" style={{ height: '30px' }}>
              {item}
              <span
                style={{ cursor: 'pointer', marginLeft: 4 }}
                onClick={(e) => {
                  e.stopPropagation();
                  removeTag(index);
                }}
                aria-label="Remove"
              >
                &times;
              </span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export default FreeTextSearchInput;
