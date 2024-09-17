import React, { useEffect } from 'react';
import { Toast, ToastContainer } from 'react-bootstrap';

interface StatusMessageProps {
  message: string;
  type: 'success' | 'failure';
  duration?: number;
  onClose: () => void;
}
// Generic status message for the wohle application 
const StatusMessage: React.FC<StatusMessageProps> = ({
  message,
  type,
  duration = 3000, // Default duration of 3 seconds
  onClose,
}) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <ToastContainer 
      position="bottom-center"
      style={{ marginBottom: '90px' }}
    >
      <Toast 
        bg={type === 'success' ? 'success' : 'danger'} 
        onClose={onClose}
        style={{ padding: '20px 30px' }}
      >
        <Toast.Body 
          className="text-white text-center"
          style={{ fontSize: '16px' }}
        >
          {message}
        </Toast.Body>
      </Toast>
    </ToastContainer>
  );
};

export default StatusMessage;
