import React, { useState, useEffect } from 'react';
import Draggable from 'react-draggable';

interface CanvasProps {
  selectedTool: string;
  toolProperties: {
    width: number;
    height: number;
    text: string;
    options: string[];
  };
}

interface UIElement {
  id: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  text?: string;
  options?: string[];
}

const Canvas: React.FC<CanvasProps> = ({ selectedTool, toolProperties }) => {
  const [elements, setElements] = useState<UIElement[]>([]);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);

  // Handle click on canvas to add new element
  const handleCanvasClick = (e: React.MouseEvent) => {
    if (!selectedTool) return;

    const rect = (e.target as HTMLElement).getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const newElement: UIElement = {
      id: `element-${Date.now()}`,
      type: selectedTool,
      x,
      y,
      width: toolProperties.width,
      height: toolProperties.height,
      text: toolProperties.text,
      options: toolProperties.options,
    };

    setElements([...elements, newElement]);
  };

  // Handle element drag
  const handleDrag = (id: string, e: any, data: { x: number; y: number }) => {
    setElements(
      elements.map((el) =>
        el.id === id ? { ...el, x: data.x, y: data.y } : el
      )
    );
  };

  // Render UI element based on type
  const renderElement = (element: UIElement) => {
    const style = {
      width: element.width,
      height: element.height,
      border: '1px solid #ccc',
      backgroundColor: selectedElement === element.id ? '#e3f2fd' : '#fff',
      padding: '8px',
      borderRadius: '4px',
      cursor: 'move',
    };

    const content = () => {
      switch (element.type) {
        case 'Button':
          return <button style={{ width: '100%', height: '100%' }}>{element.text}</button>;
        case 'Text Input':
          return <input type="text" placeholder={element.text} style={{ width: '100%' }} />;
        case 'Dropdown':
          return (
            <select style={{ width: '100%' }}>
              {element.options?.map((opt, i) => (
                <option key={i}>{opt}</option>
              ))}
            </select>
          );
        default:
          return <div>{element.type}</div>;
      }
    };

    return (
      <Draggable
        key={element.id}
        position={{ x: element.x, y: element.y }}
        onDrag={(e, data) => handleDrag(element.id, e, data)}
        onMouseDown={() => setSelectedElement(element.id)}
      >
        <div style={style}>{content()}</div>
      </Draggable>
    );
  };

  return (
    <div
      style={{
        width: '100%',
        height: 'calc(100vh - 100px)',
        border: '2px dashed #ccc',
        position: 'relative',
        backgroundColor: '#f5f5f5',
      }}
      onClick={handleCanvasClick}
    >
      {elements.map(renderElement)}
    </div>
  );
};

export default Canvas; 