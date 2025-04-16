import React, { useState } from 'react';

const ProjectTagsInput = ({ tags, setTags }) => {
  const [inputValue, setInputValue] = useState('');

  const addTag = () => {
    const trimmed = inputValue.trim();
    if (trimmed && !tags.includes(trimmed)) {
      setTags([...tags, trimmed]);
    }
    setInputValue('');
  };

  const removeTag = (index) => {
    setTags(tags.filter((_, i) => i !== index));
  };

  return (
    <div>
      <div className="pill-inline">
        {tags.map((tag, index) => (
          <span key={index} className="mini-pill">
            {tag}
            <span
              onClick={() => removeTag(index)}
              className="pill-remove"
              title="Удалить"
            >
              ×
            </span>
          </span>
        ))}
      </div>
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
        placeholder="Добавьте проект и нажмите Enter"
        className="project-input"
      />
    </div>
  );
};

export default ProjectTagsInput;