'use client';
import React, { useEffect, useRef } from 'react';
import 'quill/dist/quill.snow.css';

const QuillEditor = ({ defaultContent, onChange }: { defaultContent?: string; onChange: (value: string) => void }) => {
  const editorRef = useRef<HTMLDivElement | null>(null);
  const quillInstanceRef = useRef<any>(null); // store quill instance

  useEffect(() => {
    let isMounted = true;

    const initQuill = async () => {
      const QuillModule = await import('quill');
      const Quill = QuillModule.default;

      if (editorRef.current && !quillInstanceRef.current && isMounted) {
        const quill = new Quill(editorRef.current, {
          theme: 'snow',
          placeholder: 'Write something...',
          modules: {
            toolbar: [[{ header: [1, 2, false] }], ['bold', 'italic', 'underline'], [{ list: 'ordered' }, { list: 'bullet' }], ['link', 'image', 'code-block'], ['clean']],
          },
        });

        quill.on('text-change', () => {
          const html = quill.root.innerHTML;
          onChange(html);
        });

        quillInstanceRef.current = quill;

        // Set default content only once during initialization
        if (defaultContent) {
          quill.clipboard.dangerouslyPasteHTML(defaultContent);
        }
      }
    };

    initQuill();

    return () => {
      isMounted = false;
    };
  }, []);

  // Update content if `defaultContent` changes after mount
  useEffect(() => {
    if (quillInstanceRef.current && defaultContent) {
      quillInstanceRef.current.clipboard.dangerouslyPasteHTML(defaultContent);
    }
  }, [defaultContent]);

  return (
    <div className="w-full border-input rounded-1">
      <div ref={editorRef} />
    </div>
  );
};

export default QuillEditor;
