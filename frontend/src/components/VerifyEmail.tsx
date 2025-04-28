import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useLocation, useNavigate } from 'react-router-dom';
import { CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

const VerifyEmail: React.FC = () => {
  const [isVerifying, setIsVerifying] = useState(true);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const verifyEmail = async () => {
      try {
        // Get token from URL query params
        const params = new URLSearchParams(location.search);
        const token = params.get('token');

        if (!token) {
          setError('No verification token found in URL');
          setIsVerifying(false);
          return;
        }

        // Call API to verify email
        const response = await fetch(`${import.meta.env.VITE_API_URL}/verify-email`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to verify email');
        }

        // Handle success
        setIsSuccess(true);
        setIsVerifying(false);
      } catch (error) {
        console.error('Email verification error:', error);
        setError(error instanceof Error ? error.message : 'An unknown error occurred');
        setIsVerifying(false);
      }
    };

    verifyEmail();
  }, [location]);

  const handleGoToLogin = () => {
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="relative h-32 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
            <div className="absolute inset-0 opacity-20">
              <div className="absolute -top-12 -right-12 w-40 h-40 bg-white/20 rounded-full"></div>
              <div className="absolute top-20 -left-12 w-24 h-24 bg-white/20 rounded-full"></div>
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
              <h1 className="text-3xl font-bold text-white tracking-wide">Email Verification</h1>
            </div>
          </div>

          <div className="p-8 text-center">
            {isVerifying ? (
              <div className="flex flex-col items-center space-y-4">
                <div className="spinner-border animate-spin inline-block w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full"></div>
                <p className="text-lg text-gray-700">Verifying your email address...</p>
              </div>
            ) : isSuccess ? (
              <div className="space-y-6">
                <div className="mx-auto w-20 h-20 bg-green-100 flex items-center justify-center rounded-full">
                  <CheckCircleIcon className="h-12 w-12 text-green-500" />
                </div>
                <h2 className="text-2xl font-bold text-gray-800">Email Verified!</h2>
                <p className="text-gray-600 mb-8">
                  Your email has been successfully verified. You can now log in to your account.
                </p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleGoToLogin}
                  className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200"
                >
                  Go to Login
                </motion.button>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="mx-auto w-20 h-20 bg-red-100 flex items-center justify-center rounded-full">
                  <ExclamationCircleIcon className="h-12 w-12 text-red-500" />
                </div>
                <h2 className="text-2xl font-bold text-gray-800">Verification Failed</h2>
                <p className="text-red-500 mb-4">{error}</p>
                <p className="text-gray-600 mb-8">
                  Your email verification link might be expired or invalid. Please try again or contact support.
                </p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleGoToLogin}
                  className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200"
                >
                  Go to Login
                </motion.button>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default VerifyEmail;