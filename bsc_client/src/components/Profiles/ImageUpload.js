import React, { useRef, useState, useEffect } from 'react';
import './ImageUpload.css';

const ImageUpload = ({ onFileSelect }) => {
  const fileInputRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [preview, setPreview] = useState(null);

  const handleFile = (file) => {
    if (file && file.type.startsWith('image/')) {
      onFileSelect(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  const handleChange = (e) => {
    const file = e.target.files[0];
    handleFile(file);
  };

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  return (
    <div className="image-upload-wrapper">
      <div
        className={`upload-area ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current.click()}
      >
        {preview ? (
          <div className="preview-wrapper">
            <img src={preview} alt="Превью" className="preview-image" />
            <p className="replace-text">Нажмите или перетащите, чтобы заменить фото</p>
          </div>
        ) : (
          <>
            <p>📷 Перетащите фото сюда</p>
            <p className="or-text">или нажмите для выбора</p>
          </>
        )}

        <input
          type="file"
          accept="image/*"
          ref={fileInputRef}
          onChange={handleChange}
          style={{ display: 'none' }}
        />
      </div>
    </div>
  );
};

export default ImageUpload;
