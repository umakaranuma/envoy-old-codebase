import { useState, useEffect } from 'react';

interface EditableTextProps {
  id?: string | number;
  title: string;
  onChange: (newTitle: string, id?: string | number) => void;
  className?: string;
  inputClassName?: string;
  disabled?: boolean;
}

export const EditableText = ({ id, title, onChange, className = '', inputClassName = '', disabled = false }: EditableTextProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [tempTitle, setTempTitle] = useState(title);

  useEffect(() => {
    setTempTitle(title);
  }, [title]);

  const handleStartEditing = () => {
    if (disabled) return;
    setTempTitle(title);
    setIsEditing(true);
  };

  const handleSave = () => {
    if (tempTitle !== title) {
      onChange(tempTitle, id);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      setIsEditing(false);
      setTempTitle(title);
    }
  };

  return (
    <div className={className}>
      {isEditing ? (
        <input
          type="text"
          value={tempTitle}
          onChange={(e) => setTempTitle(e.target.value)}
          onBlur={handleSave}
          onKeyDown={handleKeyDown}
          className={`form-control form-control-sm ${inputClassName}`}
          style={{ display: 'inline', width: 'auto' }}
          autoFocus
        />
      ) : (
        <span onClick={handleStartEditing} style={{ cursor: disabled ? 'default' : 'pointer' }}>
          {title}
        </span>
      )}
    </div>
  );
};
