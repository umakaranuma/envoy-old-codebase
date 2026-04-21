import { Label } from '@apptimus-ui/ui-element';
import React, { useState, useRef, useEffect } from 'react';

type RankingProps = {
  options: any[];
  label?: string;
  isRequired?: boolean;
  onChange?: (values: string[], orderObjects: { order: number; option: string }[]) => void;
  className?: string;
};

const Ranking: React.FC<RankingProps> = ({ onChange, options, label, isRequired, className }) => {
  const [items, setItems] = useState(options);
  const [dragOverIdx, setDragOverIdx] = useState<number | null>(null);

  const dragItem = useRef<number | null>(null);

  useEffect(() => {
    setItems(options);
  }, [options]);

  const handleDragStart = (index: number) => {
    dragItem.current = index;
  };

  const handleDragOver = (index: number) => {
    setDragOverIdx(index);
    if (dragItem.current === null || dragItem.current === index) return;
    const updatedItems = [...items];
    const dragged = updatedItems[dragItem.current];
    updatedItems.splice(dragItem.current, 1);
    updatedItems.splice(index, 0, dragged);
    setItems(updatedItems);
    dragItem.current = index;

    // Call onChange with new order
    if (onChange) {
      const orderObjects = updatedItems.map((option, idx) => ({
        order: idx + 1,
        option,
      }));
      onChange(updatedItems, orderObjects);
    }
  };

  const handleDragEnd = () => {
    dragItem.current = null;
    setDragOverIdx(null);
  };

  return (
    <div className={className}>
      {label && <Label label={label} isRequired={isRequired} />}
      <ul className="list-group">
        {items.map((item: any, index) => (
          <li key={index} className={`list-group-item d-flex align-items-center justify-content-between mb-2 ${dragOverIdx === index ? 'border border-primary bg-light' : ''}`}>
            {/* Drag handle */}
            <span
              draggable
              onDragStart={() => handleDragStart(index)}
              onDragOver={(e) => {
                e.preventDefault();
                handleDragOver(index);
              }}
              onDragEnd={handleDragEnd}
              className="me-3"
              style={{
                cursor: 'grab',
                display: 'inline-flex',
                alignItems: 'center',
                padding: '4px 8px',
                borderRadius: '0.25rem',
                background: '#e9ecef',
              }}
              tabIndex={0}
              aria-label="Drag to reorder"
            >
              {/* Dots icon */}
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <circle cx="5" cy="5" r="1.5" fill="#6c757d" />
                <circle cx="5" cy="9" r="1.5" fill="#6c757d" />
                <circle cx="5" cy="13" r="1.5" fill="#6c757d" />
                <circle cx="13" cy="5" r="1.5" fill="#6c757d" />
                <circle cx="13" cy="9" r="1.5" fill="#6c757d" />
                <circle cx="13" cy="13" r="1.5" fill="#6c757d" />
              </svg>
            </span>
            <span className="flex-grow-1 text">{item.value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Ranking;
