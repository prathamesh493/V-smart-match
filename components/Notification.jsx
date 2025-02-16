import React from 'react';
import { CheckCircle, AlertCircle, X } from 'lucide-react';

const Notification = ({ type, message, onClose }) => {
  const isSuccess = type === 'success';
  
  return (
    <div 
      className={`fixed top-4 right-4 z-50 max-w-md animate-slide-in-right ${
        isSuccess ? 'bg-gradient-to-r from-[#4f46e5] to-[#c6269e]' : 'bg-gradient-to-r from-red-500 to-pink-600'
      } text-white rounded-xl shadow-xl p-4 flex items-start`}
    >
      <div className="flex-shrink-0 mr-3">
        {isSuccess ? (
          <CheckCircle className="h-6 w-6 text-white" />
        ) : (
          <AlertCircle className="h-6 w-6 text-white" />
        )}
      </div>
      <div className="flex-1">
        <h3 className="font-medium">
          {isSuccess ? 'Success!' : 'Oops!'}
        </h3>
        <p className="text-white/90 text-sm mt-1">{message}</p>
      </div>
      <button 
        onClick={onClose} 
        className="ml-4 text-white/70 hover:text-white transition-colors"
      >
        <X className="h-5 w-5" />
      </button>
    </div>
  );
};

export default Notification;